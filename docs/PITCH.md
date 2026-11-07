# Pitch outline (8 slides)
1. Problem: people act on AI answers whose actionable facts can age.
2. Evidence: show a genuine captured example and official source, only after capturing it.
3. Solution: claim-level Current / Changed / Unconfirmed.
4. Architecture: PII → Bifrost extraction → Tavily retrieval → Bifrost independent checks → quote gate.
5. Demo: live with credentials, genuine recording fallback; clearly label mock demonstrations.
6. Benchmark: real reports only; not yet run at build time.
7. Path: developer annotation API; potential usage-based service, no revenue claims.
8. Limits and next 30 days: source coverage, human labels, adversarial testing, shared jobs and auth.

## Questions and honest answers
1. Why not search-enabled chat? We expose claim-level provenance and enforce approved-source gates.
2. Why official sources? They are primary evidence, though they can lag updates.
3. What is mocked? Only explicit MOCK_MODE fixtures; banner and API flag identify them.
4. What is real? The implemented APIs and tested offline workflow; live results need credentials.
5. Cost? Tavily estimated credits and observed token usage, no invented dollar figure.
6. False positives? Authority and quote checks, disagreement downgrade, confidence threshold.
7. No official source? Unconfirmed.
8. Why two models? Disagreement detection; agreement is not proof.
9. Are models independent? Different providers are configured; training independence is not claimed.
10. Does caching stale the check? Evidence TTL is volatility-dependent; its retrieval time is shown.
11. Privacy? Best-effort masking; avoid sensitive input; upstream retention applies.
12. Can this replace advice? No, use official sources and qualified professionals.
13. Does the benchmark prove accuracy? Not yet; a small sample would not generalize.
14. How does it scale? Bounded concurrency now; shared job storage/auth needed for production.
15. What remains for submission? Real captures, source activation, human labels, measured results, human review and a finished slide deck.
