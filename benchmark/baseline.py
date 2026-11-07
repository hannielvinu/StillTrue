async def baseline(client, model, claim):
    answer = await client.chat(
        model,
        [
            {
                "role": "system",
                "content": "Is this claim still true today? Answer CURRENT, CHANGED, or UNSURE only. Do not retrieve sources.",
            },
            {"role": "user", "content": claim},
        ],
    )
    return answer.strip() if answer.strip() in ("CURRENT", "CHANGED") else "UNCONFIRMED"
