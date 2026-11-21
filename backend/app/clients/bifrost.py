import asyncio
import json
import time
from pathlib import Path
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
        if "gpt-oss" in model:
            # Reasoning tokens are billed output; low effort keeps free-tier quotas intact.
            payload["reasoning_effort"] = "low"
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
                            await asyncio.sleep(self._retry_after(r, attempt))
                            continue
                    r.raise_for_status()
                    data = r.json()
                    for k in self.usage:
                        self.usage[k] += data.get("usage", {}).get(k, 0)
                    self._ledger(model, data.get("usage", {}))
                    self.used_models.append(data.get("model", model))
                    content = data["choices"][0]["message"]["content"]
                    return schema.model_validate_json(content) if schema else content
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * 2**attempt)
        raise RuntimeError("Gateway request failed")

    @staticmethod
    def _retry_after(response: httpx.Response, attempt: int) -> float:
        """Honour the provider's Retry-After (token-per-minute windows reset in seconds)."""
        try:
            return min(20.0, max(0.5, float(response.headers.get("retry-after", ""))))
        except ValueError:
            return min(20.0, 2.0 * 2**attempt) if response.status_code == 429 else 0.5 * 2**attempt

    def _ledger(self, model: str, usage: dict) -> None:
        """Append one line per model call so spending is auditable after every run."""
        try:
            path = Path(self.s.cache_path).with_name("usage.jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            row = {
                "t": round(time.time()),
                "model": model,
                **{
                    k: usage.get(k, 0)
                    for k in ("prompt_tokens", "completion_tokens", "total_tokens")
                },
            }
            with path.open("a") as f:
                f.write(json.dumps(row) + "\n")
        except OSError:
            pass
