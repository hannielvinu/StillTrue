import re
from datetime import datetime, timezone
from html import unescape
from ..schemas import Evidence
from .trust import authority, domain, official_domains, tier


def clean(text):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    return unescape(re.sub(r"<[^>]*>", " ", text))


async def retrieve(client, claim, pack, emit):
    publisher = authority(claim.authority_domain)
    subject = claim.subject_key.replace("_", " ")
    attribute = claim.attribute_key.replace("_", " ")
    region = "" if pack["jurisdiction"] == "Global" else pack["jurisdiction"]
    year = datetime.now(timezone.utc).year
    # The claim's own words search better than snake_case keys; keys add the entity names.
    query = " ".join(f"{claim.text} {subject} {attribute} {region} {year}".split())[:380]
    # Ask the publisher of the fact first; fall back to the pack's official list.
    official = [publisher] if publisher else official_domains(pack, None)
    await emit("claim_stage", {"id": claim.id, "stage": "searching"})
    response = await client.search(query, pack, official)
    results = response.get("results", [])
    if not any(tier(r.get("url", ""), pack, publisher) == 1 for r in results):
        wider = official_domains(pack, None) if publisher and pack["tier1_domains"] else None
        results += (await client.search(query, pack, wider, basic=True)).get("results", [])
    await emit("claim_stage", {"id": claim.id, "stage": "reading"})
    urls = list(
        dict.fromkeys(r["url"] for r in results if tier(r.get("url", ""), pack, publisher) == 1)
    )[:2]
    if urls:
        extracted = await client.extract(urls, query)
        for r in extracted.get("results", []):
            if r.get("url") in urls:
                results.insert(0, {"url": r["url"], "content": r.get("raw_content", "")})
    evidence, seen, remaining = [], set(), 5000
    for r in sorted(results, key=lambda r: tier(r.get("url", ""), pack, publisher) or 99):
        url = r.get("url", "")
        t = tier(url, pack, publisher)
        text = clean(r.get("content", "") or r.get("raw_content", ""))[: min(2500, remaining)]
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
    return {"evidence": evidence, "query": query, "publisher": publisher}
