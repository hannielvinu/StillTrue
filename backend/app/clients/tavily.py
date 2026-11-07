import asyncio
from datetime import datetime, timezone
import httpx
from ..cache.store import Store


class Tavily:
    def __init__(self, settings):
        self.s = settings
        self.credits = 0
        self.store = Store(settings.cache_path)

    async def call(self, endpoint: str, payload: dict, estimate: int):
        if not self.s.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is not configured")
        async with httpx.AsyncClient(timeout=self.s.tavily_timeout_s) as client:
            for attempt in range(3):
                await self.store.reserve(
                    datetime.now(timezone.utc).date().isoformat(),
                    estimate,
                    self.s.tavily_daily_credit_cap,
                )
                self.credits += estimate
                try:
                    r = await client.post(
                        "https://api.tavily.com/" + endpoint,
                        json=payload,
                        headers={"Authorization": "Bearer " + self.s.tavily_api_key},
                    )
                    if r.status_code == 429 or r.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(0.5 * 2**attempt)
                            continue
                    r.raise_for_status()
                    return r.json()
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * 2**attempt)
        raise RuntimeError("Retrieval request failed")

    async def search(self, query: str, pack: dict, official: bool):
        body = {
            "query": query,
            "search_depth": "advanced",
            "max_results": 5,
            "topic": "general",
            "exclude_domains": pack["blocked_domains"],
        }
        if official:
            body["include_domains"] = pack["tier1_domains"]
        return await self.call("search", body, 2)

    async def extract(self, urls, query):
        return await self.call(
            "extract",
            {"urls": urls, "query": query, "chunks_per_source": 3, "extract_depth": "basic"},
            1,
        )
