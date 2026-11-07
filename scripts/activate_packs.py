"""Activate official-domain candidates only after successful HTTPS page checks."""

import asyncio
from pathlib import Path
import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = {
    "india_tax": [
        "https://www.incometaxindia.gov.in/w/8schedule_al",
        "https://www.incometax.gov.in/iec/foportal/",
    ],
    "uk_personal_finance": ["https://www.gov.uk/individual-savings-accounts"],
    "travel_visa": [
        "https://travel.state.gov/content/travel/en/us-visas.html",
        "https://www.gov.uk/check-uk-visa",
    ],
    "developer_apis": ["https://platform.openai.com/docs/deprecations"],
}


async def main():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for name, urls in CANDIDATES.items():
            path = ROOT / "backend/app/packs" / f"{name}.yaml"
            pack = yaml.safe_load(path.read_text())
            for url in urls:
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    host = httpx.URL(url).host
                    # Do not accept redirects to an unrelated host as proof.
                    if r.url.host not in (host, host.removeprefix("www.")):
                        raise ValueError("Unexpected redirect host; review manually")
                    if host not in pack["tier1_domains"]:
                        pack["tier1_domains"].append(host)
                    print(f"Activated {name}: {host}; manually review policy relevance")
                except (httpx.HTTPError, ValueError):
                    print(f"Not activated: {url} (access failed; no authority assumed)")
            path.write_text(yaml.safe_dump(pack, sort_keys=False))


if __name__ == "__main__":
    asyncio.run(main())
