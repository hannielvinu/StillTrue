# Enable live checking

The application runs offline with `MOCK_MODE=true`. This is a synthetic demonstration, never evidence for benchmarks.

## 1. Tavily

Create an account at https://app.tavily.com and obtain an API key from its dashboard. Check your plan's quota and pricing. Put it in local `.env` as `TAVILY_API_KEY` or enter it securely in cloud environment settings. Never paste it into chat, source files or a commit. Allow api.tavily.com for outbound HTTPS.

## 2. Bifrost and models

Bifrost is a gateway; it does not supply provider credits. Obtain a provider API key from your provider's account dashboard, with billing and model access enabled. For the supplied configuration use OpenAI (https://platform.openai.com/api-keys) and optionally Anthropic (https://console.anthropic.com/settings/keys). Put provider keys in `.env` for Docker Compose, which passes them to the gateway. For managed cloud proxy bindings use the documented destination-scoped credential route; do not assume a proxy placeholder is a usable raw Docker credential.

Set EXTRACTOR_MODEL and VERIFIER_MODEL_A to exact available `provider/model` IDs. Set VERIFIER_MODEL_B to an available model from a different provider for cross-model checks; blank is valid single-model mode. No particular example model is promised to exist in your account. Configure additional providers in bifrost/config.json using upstream documented env references. The optional BIFROST_VIRTUAL_KEY is a gateway access key, not a provider credential.

## 3. Activate sources and start

Allow the docs, Tavily, configured provider destinations and official pages in environment network settings. Run `backend/.venv/bin/python scripts/activate_packs.py` and inspect the activated domains. Set MOCK_MODE=false. `docker compose up --build -d`. Visit `/api/v1/health`, then run all three illustrative inputs. Health reports reachability and presence; only a completed non-mock check exercises the providers.

## 4. Capture, benchmark and submit

Capture a genuine model answer, record its verification, manually label benchmark candidates after checking official URLs, run `make bench`, and rebuild. Read docs/VERIFICATION.md for what has already run. Do not present a staged answer or synthetic fixture as a captured model error.

Tell the assistant only that configuration is ready; do not send key values. If live validation fails, share a sanitized error/status, never credentials. Revoke and replace any key accidentally disclosed.
