import re
from datetime import datetime, timezone
from html import unescape
from ..schemas import Evidence
from .trust import tier, domain


def clean(text):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    return unescape(re.sub(r"<[^>]*>", " ", text))


async def retrieve(client, claim, pack, emit):
    query = f"{claim.subject_key.replace('_', ' ')} {claim.attribute_key.replace('_', ' ')} {pack['jurisdiction']} {datetime.now(timezone.utc).year}"
    await emit("claim_stage", {"id": claim.id, "stage": "searching"})
    response = await client.search(query, pack, bool(pack["tier1_domains"]))
    results = response.get("results", [])
    if not any(tier(r.get("url", ""), pack) == 1 for r in results) and pack["tier1_domains"]:
        results += (await client.search(query, pack, False)).get("results", [])
    await emit("claim_stage", {"id": claim.id, "stage": "reading"})
    urls = list(dict.fromkeys(r["url"] for r in results if tier(r.get("url", ""), pack) == 1))[:2]
    if urls:
        extracted = await client.extract(urls, query)
        for r in extracted.get("results", []):
            if r.get("url") in urls:
                results.insert(0, {"url": r["url"], "content": r.get("raw_content", "")})
    evidence, seen, remaining = [], set(), 3000
    for r in sorted(results, key=lambda r: tier(r.get("url", ""), pack) or 99):
        url = r.get("url", "")
        t = tier(url, pack)
        text = clean(r.get("content", "") or r.get("raw_content", ""))[: min(1500, remaining)]
        if t == 0 or url in seen or not text:
            continue
        seen.add(url)
        remaining -= len(text)
        date = re.search(
            r"(?:updated|published)[: ]+(\d{4}-\d{2}-\d{2}|[A-Za-z]+ \d{1,2},? \d{4})", text, re.I
        )
        evidence.append(
            Evidence(
                url=url,
                domain=domain(url),
                tier=t,
                text=text,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                page_date_hint=date.group(1) if date else None,
            ).model_dump()
        )
        if remaining <= 0:
            break
    return {"evidence": evidence, "query": query}
