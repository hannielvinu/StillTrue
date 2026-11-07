# Verification — 8 November 2026 (Asia/Kolkata)

## Executed in this cloud machine

| Command/check | Result |
|---|---|
| `UV_CACHE_DIR=/tmp/stilltrue-uv uv sync --project backend` | Dependencies installed; lockfile saved |
| `npm ci --cache /tmp/stilltrue-npm --prefix frontend` | Reproducible install passed |
| `make test` | 17 backend tests and 7 frontend tests passed |
| `make lint` | Ruff lint/format and strict TypeScript passed |
| `make build` | Production frontend compiled |
| Docker multi-stage build with mounted cloud CA bundle | Built with TLS verification and hashed Python dependencies |
| Compose startup (cloud CA build-secret override) | App and Bifrost started |
| `/api/v1/health` from containerized app | app ok, bifrost_reachable true, mock true; Tavily key absent, live_ready false |
| `python scripts/browser_smoke.py` | 12 complete mock runs: 360, 390, 768, 1024, 1280, 1536px × light/dark; no horizontal overflow or page errors; routes, keyboard entry/submit, reduced motion passed |
| Screenshots | Real browser captures under docs/screenshots; synthetic data banner visible |
| Text/background token contrast calculation | 13 primary/status pairs passed ≥4.5:1; lowest 4.65:1 |
| `MOCK_MODE=true make bench` | Expected refusal; no report created |
| `python scripts/count_chars.py /tmp/stilltrue-pitch.txt --limit 140` | One-line pitch 114 characters |
| Dependency audits | Initial vulnerabilities fixed by upgrades; final npm audit: 0 vulnerabilities; final pip-audit: no known vulnerabilities |

Browser smoke uses the system Python Playwright installation and /usr/bin/chromium. Install Playwright and Chromium separately on machines without them. It requires the app to be running in explicit mock mode. It is not a Lighthouse or full assistive-technology audit. 200% zoom and layout-shift metrics have not been formally measured.

The non-mock pipeline is exercised with respx HTTP contract fixtures, including retrieval, dual verification and evidence-cache reuse. These are automated tests, not live provider responses.

`MOCK_MODE=true make dev` was also started and checked: port 5173 serves Vite and proxies /api/v1/meta to port 8000; backend health reaches the running Bifrost service. `make install` was rerun successfully against the final lockfiles.

## Not executed / remaining prerequisites

- No real Tavily or model inference calls: keys absent, as agreed with the user.
- No real capture, recording or benchmark numbers. Exactly one user-labelled seed exists; 40 candidates could not be sourced because official pages were blocked.
- Source packs have no activated authority domains pending accessible official-page checks. Run activation script after network access is saved and manually review the policy relevance.
- No remote GitHub Actions run or publication is claimed from a local workflow file.
- No Lighthouse scores, exhaustive screen-reader audit or production load test claimed.

## Known integration assumptions

Tavily request fields follow the supplied contract; official docs host was blocked and credentialed behavior remains unverified. Bifrost config, virtual keys, fallbacks and local catalog behavior were checked against upstream GitHub documentation. Vendor catalog examples are limited snapshots, not current price claims.

## Repository and configuration

The implementation was committed and pushed to origin/main as 038c42a. Documentation and browser evidence are committed separately. Both author and committer use Hanniel Vinu <hannielvinu@gmail.com>; commit-message attribution scan is clean. No credential-shaped tokens were detected by the local history scan; this is a limited pattern scan, not a credential-leak guarantee.

A cloud CA build-secret override was used only for this managed environment. No TLS verification was disabled. The committed Dockerfile accepts an optional BuildKit proxy_ca secret; ordinary local Docker builds use their normal trust store. Proxy exceptions for internal bifrost traffic are configured in Compose.
