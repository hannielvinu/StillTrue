# Architecture

```mermaid
sequenceDiagram
  participant UI as React
  participant API as FastAPI
  participant BF as Bifrost
  participant TV as Tavily
  UI->>API: Create job (answer, pack)
  API->>API: Mask PII; emit report
  API->>BF: Extract actionable claims
  loop bounded concurrent claims
    API->>API: Evidence cache lookup
    API->>TV: Search official domains; extract pages on miss
    API->>BF: Independent verifier calls
    API->>API: Authority, quote, confidence, agreement gates
    API-->>UI: SSE claim_result
  end
  API-->>UI: Summary and metadata
```

Retrieved text is hostile data: HTML/scripts are removed, input is capped, prompts forbid following instructions in evidence. Deterministic source/quote gates limit unsupported outputs but cannot establish semantic truth or defeat every injection. Cross-provider verification can catch disagreement; shared model errors remain possible.

Evidence cache keys hash pack policy plus canonical subject/attribute. Pasted text is not stored in SQLite; extracted evidence is. TTL uses volatility. LLM judging still runs on cache hits. Bifrost semantic caching is off, distinct from this cache.

Failure modes: claim-level timeouts/budget failures become Unconfirmed; extraction errors end the job with a safe message. Jobs are in-memory with 30-minute expiry, lazy cleanup on job creation and SSE replay IDs. Restart loses jobs. Daily budget reservations use SQLite transactions across concurrent tasks; retry calls reserve again conservatively. Reservations are estimates, not a billing ledger.

Use one API worker, a persistent volume, an authenticated reverse proxy and TLS for nonlocal deployments. Public production hardening, distributed job storage and external monitoring are future work.
