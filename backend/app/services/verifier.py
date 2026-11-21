import asyncio
import json
import re
from datetime import datetime, timezone
from ..schemas import Judgment
from .trust import ROOT


_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def same_value(a, b):
    """Verifiers agree unless both name a number and the numbers differ.

    Status values ("end-of-life" vs "no longer supported") are worded freely, so the
    relation carries the agreement; a numeric conflict ("£127" vs "£135") never passes.
    """
    if a is None or b is None:
        return True
    na = [n.replace(",", "") for n in _NUM.findall(a)]
    nb = [n.replace(",", "") for n in _NUM.findall(b)]
    if na and nb:
        return float(na[0]) == float(nb[0])
    return True


def _flat(text):
    """Compare quotes ignoring only case, whitespace, curly quotes and dash styles."""
    table = str.maketrans(
        {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u00a0": " ",
        }
    )
    return " ".join(text.translate(table).lower().split())


def quoted_in(quote, text):
    """Every fragment of the quote (split at an ellipsis) must appear verbatim in the page."""
    page = _flat(text)
    parts = [p.strip(" .\"'") for p in re.split(r"\.\.\.|\u2026", _flat(quote))]
    parts = [p for p in parts if p]
    stitched = len(parts) > 1
    return bool(parts) and all((len(p.split()) >= 3 or not stitched) and p in page for p in parts)


def quote_source(j, evidence):
    """Return the official page that contains the quote verbatim (cited page first)."""
    quote = j.evidence_quote
    if not quote or len(quote.split()) > 25:
        return None
    official = [e for e in evidence if e["tier"] == 1]
    official.sort(key=lambda e: e["url"] != j.source_url)
    return next((e["url"] for e in official if quoted_in(quote, e["text"])), None)


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
        first = judgments[0]
        agree = all(
            j.relation == first.relation and same_value(j.current_value, first.current_value)
            for j in judgments[1:]
        )
        base["models_agree"] = agree
        if not agree:
            return base | {"reason": "models_disagree"}
    if any(j.relation == "insufficient" for j in judgments):
        return base
    for i, j in enumerate(judgments):
        page = quote_source(j, evidence)
        if page is None:
            return base | {"reason": "quote_not_supported"}
        if page != j.source_url:
            # The quote is verbatim on another official page we retrieved: cite that page.
            judgments[i] = j = j.model_copy(update={"source_url": page})
    if judgments[0].relation == "contradicts" and not any(j.current_value for j in judgments):
        return base
    if judgments[0].relation == "contradicts" and not judgments[0].current_value:
        judgments[0] = judgments[0].model_copy(
            update={"current_value": next(j.current_value for j in judgments if j.current_value)}
        )
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

    async def one(model, repair=None):
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps({"claim": claim.model_dump(), "evidence": evidence}),
            },
        ]
        if repair is not None:
            messages += [
                {"role": "assistant", "content": repair.model_dump_json()},
                {
                    "role": "user",
                    "content": "Your evidence_quote is not an exact substring of any evidence text. "
                    "Copy one contiguous span character for character (no ellipsis, no paraphrase), "
                    "set source_url to that item's url, or answer insufficient.",
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

    judgments = list(await asyncio.gather(*(one(m) for m in models)))
    # One repair attempt for a verifier whose quote is not on any official page.
    for i, (model, j) in enumerate(zip(models, judgments)):
        if j.relation != "insufficient" and quote_source(j, evidence) is None:
            judgments[i] = await one(model, repair=j)
    return decide(judgments, evidence, settings.mode)
