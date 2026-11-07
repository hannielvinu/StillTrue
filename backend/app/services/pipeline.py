import asyncio
import json
import re
import time
from datetime import datetime, timezone
from ..cache.store import Store, BudgetExhausted
from ..clients.bifrost import Bifrost
from ..clients.tavily import Tavily
from ..schemas import Claim, Judgment
from . import extractor, retriever, verifier, rewriter
from .pii import scan
from .scorer import summarize
from .trust import packs, ROOT


async def run(data, settings, emit):
    started = time.monotonic()
    text, findings = scan(data.text, data.redact)
    question, _ = scan(data.question, data.redact)
    await emit("run_started", {"mock": settings.mock_mode, "mode": settings.mode})
    await emit("pii_report", {"count": len(findings), "masked": data.redact, "findings": findings})
    llm, tavily, store = Bifrost(settings), Tavily(settings), Store(settings.cache_path)
    if settings.mock_mode:
        spans = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()][
            : settings.max_claims_per_run
        ]
        claims = [
            Claim(
                id=f"claim-{i + 1}",
                text=s,
                subject_key=f"mock_{i}",
                attribute_key="allowance",
                asserted_value="illustrative value",
                claim_type="threshold",
            )
            for i, s in enumerate(spans)
        ]
    else:
        claims = await extractor.extract(llm, text, question, settings)
    await emit("claims_extracted", {"claims": [c.model_dump() for c in claims]})
    sem = asyncio.Semaphore(settings.claim_concurrency)
    results = []

    async def one(claim):
        await emit("claim_stage", {"id": claim.id, "stage": "queued"})
        async with sem:
            begin = time.monotonic()
            cached, evidence, query = False, [], ""
            try:
                if settings.mock_mode:
                    fixture = json.loads((ROOT / "fixtures/offline.mock.json").read_text())
                    evidence = [
                        {
                            "url": fixture["url"],
                            "domain": "example.test",
                            "tier": 1,
                            "text": fixture["evidence_text"],
                            "retrieved_at": datetime.now(timezone.utc).isoformat(),
                            "page_date_hint": None,
                        }
                    ]
                    for stage in ["searching", "reading", "verifying"]:
                        await emit("claim_stage", {"id": claim.id, "stage": stage})
                        await asyncio.sleep(0.08)
                    judgment = Judgment(
                        relation="contradicts",
                        current_value="200 units",
                        evidence_quote=fixture["evidence_text"],
                        source_url=fixture["url"],
                        confidence=0.95,
                    )
                    decision = verifier.decide([judgment], evidence, "single")
                else:
                    pack = packs()[data.pack]
                    # Include the trust policy in the key so edited packs invalidate evidence.
                    key = Store.key(data.pack + json.dumps(pack, sort_keys=True), claim)
                    ttl = {
                        "high": settings.cache_ttl_high_h,
                        "medium": settings.cache_ttl_med_h,
                        "low": settings.cache_ttl_low_h,
                    }[claim.volatility]
                    retrieval = await store.get(key, ttl)
                    cached = retrieval is not None
                    if retrieval is None:
                        retrieval = await retriever.retrieve(tavily, claim, pack, emit)
                        if retrieval["evidence"]:
                            await store.put(key, retrieval)
                    evidence, query = retrieval["evidence"], retrieval["query"]
                    await emit("claim_stage", {"id": claim.id, "stage": "verifying"})
                    decision = await verifier.verify(llm, claim, evidence, settings)
            except Exception as exc:
                decision = {
                    "verdict": "UNCONFIRMED",
                    "score": None,
                    "reason": "budget_exhausted" if isinstance(exc, BudgetExhausted) else "error",
                    "models_agree": None,
                }
            result = {
                "claim": claim.model_dump(),
                **decision,
                "evidence": evidence,
                "query": query,
                "cache_hit": cached,
                "latency_ms": round((time.monotonic() - begin) * 1000),
                "mock": settings.mock_mode,
            }
            results.append(result)
            await emit("claim_stage", {"id": claim.id, "stage": "done"})
            await emit("claim_result", result)

    await asyncio.gather(*(one(c) for c in claims))
    results.sort(key=lambda r: text.index(r["claim"]["text"]))
    correction = None
    if not settings.mock_mode:
        try:
            correction = await rewriter.rewrite(llm, text, results, settings)
        except Exception:
            pass
    if correction:
        await emit("rewrite", correction)
    result = {
        "mock": settings.mock_mode,
        "mode": "single" if settings.mock_mode else settings.mode,
        "claims": results,
        "summary": summarize(results),
        "correction": correction,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "latency_ms": round((time.monotonic() - started) * 1000),
            "models": llm.used_models,
            "tokens": llm.usage,
            "cache_hits": sum(r["cache_hit"] for r in results),
            "tavily_credits": tavily.credits,
            "credits_estimated": True,
        },
    }
    await emit("run_complete", result)
    return result
