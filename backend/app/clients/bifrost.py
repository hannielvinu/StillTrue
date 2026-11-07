import asyncio
import json
import httpx
from pydantic import BaseModel
from ..config import Settings


class Bifrost:
    def __init__(self, settings: Settings):
        self.s = settings
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0}
        self.used_models: list[str] = []

    async def chat(self, model: str, messages: list[dict], schema: type[BaseModel] | None = None):
        if not model:
            raise ValueError("Configure a provider/model ID in environment settings")
        payload = {"model": model, "messages": messages, "temperature": 0}
        if self.s.fallback_models and (schema is None or schema.__name__ != "Judgment"):
            payload["fallbacks"] = [
                m.strip() for m in self.s.fallback_models.split(",") if m.strip()
            ]
        if schema:
            payload["response_format"] = {"type": "json_object"}
            payload["messages"] = [
                *messages,
                {
                    "role": "system",
                    "content": "JSON schema: " + json.dumps(schema.model_json_schema()),
                },
            ]
        headers = {}
        if self.s.bifrost_virtual_key:
            headers["x-bf-vk"] = self.s.bifrost_virtual_key
        async with httpx.AsyncClient(timeout=self.s.llm_timeout_s) as client:
            for attempt in range(3):
                try:
                    r = await client.post(
                        self.s.bifrost_base_url.rstrip("/") + "/v1/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                    if r.status_code == 429 or r.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(0.5 * 2**attempt)
                            continue
                    r.raise_for_status()
                    data = r.json()
                    for k in self.usage:
                        self.usage[k] += data.get("usage", {}).get(k, 0)
                    self.used_models.append(data.get("model", model))
                    content = data["choices"][0]["message"]["content"]
                    return schema.model_validate_json(content) if schema else content
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * 2**attempt)
        raise RuntimeError("Gateway request failed")
