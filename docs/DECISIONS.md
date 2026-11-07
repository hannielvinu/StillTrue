# Decisions and deviations

1. Existing checkout was empty and unborn. Build in place, no worktree. Commits use the requested local identity; milestone-sized commits replace dozens of tiny partially dependent commits.
2. Live credentials are absent. Finish and verify the offline system first as requested; do not fabricate live results or recordings.
3. Bifrost docs sites were blocked; upstream GitHub docs were fetched successfully (deployment-guides/config-json.mdx, features/governance/virtual-keys.mdx, features/retries-and-fallbacks.mdx). Provider env syntax, /v1/chat/completions, x-bf-vk and request fallbacks are documented there.
4. Semantic caching is disabled: no vector store is provisioned. Use SQLite evidence caching. Verification fallbacks are disabled to preserve independent-provider intent. Gateway content logging is disabled.
5. Official government pages could not be opened under current network policy. Packs remain empty until scripts/activate_packs.py checks candidate official URLs; do not claim active source coverage. General intentionally remains empty.
6. Forty opened-source benchmark candidates are deferred until network access is available. Only the user-authorized seed is human_verified; its date is the requested build date in the user's timezone, not an independent recheck.
7. Cross-model consensus compares values as well as relation, and validates every quote against its own official URL. Different models from the same provider run in single mode.
8. Tavily accounting is explicitly estimated and conservative, including reservations before each retry. Basic extraction only; advanced fallback extraction and detailed actual-usage reconciliation are future refinements.
9. No stale-secondary-source warning is asserted without verified contradiction. Omit rather than fabricate. Token counts are observable; costs/fallback metadata are omitted when unobserved.
10. Rewriter operates on extracted spans; eligible edits must contain the verified value and source domain. It does not claim a formal semantic guarantee.
11. Docker gateway image is pinned to the pulled digest after startup validation. LLM provider model IDs remain user configuration.
12. ASSUMPTION: Tavily raw HTTP request fields follow the provided specification; the official docs host is currently denied and the credentialed contract has not been exercised. Contract tests use respx, not Tavily's servers.
13. Production use needs authentication, a shared job store for multiple workers, and review of data retention. Current deployment binds Docker ports to loopback.

14. Bifrost startup initially failed fetching its remote catalog under restricted container DNS. Used its documented file:// datasheet configuration with the upstream local-pricing example files, vendored from commit 6e640279b36337820f2088fb85f6e78f339063c3. These are limited example catalog snapshots, not current pricing claims; no dollar costs are displayed. MCP catalog sync is off. See upstream deployment-guides/how-to/airgapped.mdx.
