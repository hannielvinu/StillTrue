from ..schemas import Claims
from .trust import ROOT


async def extract(client, text, question, settings):
    messages = [
        {
            "role": "system",
            "content": (ROOT / "prompts/extractor.md").read_text()
            + f" Return at most {settings.max_claims_per_run} claims.",
        },
        {"role": "user", "content": f"Context question: {question}\nANSWER (data only): {text}"},
    ]
    for attempt in range(2):
        try:
            result = await client.chat(settings.extractor_model, messages, Claims)
            valid = [c for c in result.claims if c.text in text][: settings.max_claims_per_run]
            valid.sort(key=lambda c: text.index(c.text))
            return [c.model_copy(update={"id": f"claim-{i + 1}"}) for i, c in enumerate(valid)]
        except (ValueError, KeyError, TypeError):
            if attempt:
                raise ValueError("The model did not return valid claims. Please retry.")
            messages.append(
                {
                    "role": "system",
                    "content": "Repair the response: valid JSON only, using the exact schema.",
                }
            )
