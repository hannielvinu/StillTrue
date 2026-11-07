from pydantic import BaseModel
from .trust import ROOT, domain


class Rewrite(BaseModel):
    sentence: str


async def rewrite(client, text, results, settings):
    corrected = text
    edits = []
    for result in results:
        if not (
            result["verdict"] == "CHANGED"
            and result.get("models_agree") is True
            and result.get("confidence", 0) >= 0.8
        ):
            continue
        claim = result["claim"]["text"]
        value, host = result["current_value"], domain(result["source_url"])
        output = await client.chat(
            settings.extractor_model,
            [
                {"role": "system", "content": (ROOT / "prompts/rewriter.md").read_text()},
                {
                    "role": "user",
                    "content": f"Sentence: {claim}\nVerified value: {value}\nSource: {host}",
                },
            ],
            Rewrite,
        )
        if value in output.sentence and f"[{host}]" in output.sentence and claim in corrected:
            corrected = corrected.replace(claim, output.sentence, 1)
            edits.append({"before": claim, "after": output.sentence, "url": result["source_url"]})
    return {"text": corrected, "edits": edits} if edits else None
