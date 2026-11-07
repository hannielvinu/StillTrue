import asyncio
import json
from datetime import datetime, timezone
from ..schemas import Judgment
from .trust import ROOT


def decide(judgments, evidence, mode):
    base = {
        "verdict": "UNCONFIRMED",
        "score": None,
        "reason": "evidence_insufficient",
        "models_agree": None,
        "judgments": [j.model_dump() for j in judgments],
    }
    if not any(e["tier"] == 1 for e in evidence):
        return base | {"reason": "no_official_source"}
    if not judgments:
        return base
    if len(judgments) > 1:
        # Agreement must include the current value, not just a binary relation.
        agree = len({(j.relation, j.current_value) for j in judgments}) == 1
        base["models_agree"] = agree
        if not agree:
            return base | {"reason": "models_disagree"}
    if any(j.relation == "insufficient" for j in judgments):
        return base
    for j in judgments:
        quote = j.evidence_quote
        if (
            not quote
            or len(quote.split()) > 25
            or not any(
                e["tier"] == 1 and e["url"] == j.source_url and quote in e["text"] for e in evidence
            )
        ):
            return base | {"reason": "quote_not_supported"}
        if j.relation == "contradicts" and not j.current_value:
            return base
    confidence = sum(j.confidence for j in judgments) / len(judgments)
    if mode == "single" and confidence < 0.8:
        return base
    c = confidence * (0.9 if mode == "single" else 1)
    verdict = "CURRENT" if judgments[0].relation == "supports" else "CHANGED"
    score = round(60 + 40 * c) if verdict == "CURRENT" else round(20 * (1 - c))
    return base | {
        "verdict": verdict,
        "score": score,
        "reason": None,
        "confidence": confidence,
        **{
            k: getattr(judgments[0], k)
            for k in [
                "current_value",
                "effective_from",
                "change_summary",
                "evidence_quote",
                "source_url",
            ]
        },
    }


async def verify(client, claim, evidence, settings):
    models = settings.models if settings.mode == "cross-model" else settings.models[:1]
    system = (
        (ROOT / "prompts/verifier.md").read_text()
        + " Today: "
        + datetime.now(timezone.utc).date().isoformat()
    )

    async def one(model):
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps({"claim": claim.model_dump(), "evidence": evidence}),
            },
        ]
        for attempt in range(2):
            try:
                return await client.chat(model, messages, Judgment)
            except ValueError:
                if attempt:
                    raise
                messages.append(
                    {"role": "system", "content": "Repair your JSON to match the schema exactly."}
                )

    judgments = await asyncio.gather(*(one(m) for m in models))
    return decide(judgments, evidence, settings.mode)
