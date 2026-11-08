# Free-only deployment and keys

## What can run without accounts or API keys

`VITE_OFFLINE_DEMO=true npm run build` from frontend produces a static browser-only demo. It performs **zero LLM or web-search calls**, uses hash routing for subpath hosting, and marks all claims Unconfirmed. It has a permanent OFFLINE DEMO / MOCK DATA banner, no fabricated official citations and no benchmark eligibility. No free-tier quota or credit card is needed to run it locally.

The GitHub Actions Pages workflow can publish this static demo on a public repository using GitHub Pages. Enable repository Settings → Pages → Source: GitHub Actions, then run the **Deploy free offline demo** workflow. The expected address is `https://hannielvinu.github.io/StillTrue/`; this is a proposed address, **not a confirmed live deployment** until the workflow completes and the address is tested. Hosting settings/Actions restrictions can require repository-owner action.

## Full backend option

The Docker app can be hosted by a provider offering a free Docker service. `render.yaml` is a prepared optional blueprint using `plan: free` and explicit mock mode. Its availability and current terms must be verified in the owner's account. No provider account, paid plan, card, or paid instance has been created. Ephemeral free storage loses evidence cache and budget state on restart. A live service also needs a reachable Bifrost gateway and credentials, not just frontend hosting.

## Real sponsor calls cannot be made from invented keys

- Tavily: create/sign in to your own account at https://app.tavily.com and obtain a key using any free allocation the account currently offers. No current quota amount is promised here. Set a provider-side usage limit; never add paid billing without choosing to do so.
- Model access: Bifrost is open-source gateway software, not free model credit. A provider's free developer tier or a local model is separate. Choose a currently available free-tier model, configure its provider in Bifrost, and supply that provider's credential securely. Examples of where to check current terms: https://ai.google.dev/gemini-api/docs/pricing and https://console.groq.com. Their free tiers and eligibility are not verified in this environment.
- Bifrost virtual keys are access/governance keys created in your gateway. They do not replace model-provider credentials.
- Local models can avoid model API charges, but do not remove the Tavily requirement and do not prove two-provider agreement. They have not been benchmarked here.

Do not paste keys in chat or commit them. Configure secrets in hosting/cloud settings. Application credit caps are estimates and cannot determine whether an account has paid billing enabled.

## Current external blockers

GitHub API and sponsor/source sites are denied by the active cloud allowlist. Required domain additions have been saved to the environment draft; they must be applied through environment settings. GitHub authentication exists, but API reachability is denied, so Pages enablement/deployment cannot yet be confirmed. No Tavily, model-provider, or hosting credentials are configured. Saving a draft does not apply it.
