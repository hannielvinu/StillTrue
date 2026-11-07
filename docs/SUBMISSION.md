# Submission copy kit

## One-line pitch
Check whether your AI answer is still true, claim by claim, against official sources—with evidence, not guesswork.

## Problem (two sentences)
People may act on AI answers whose deadlines, thresholds or requirements have changed. Search results can also be outdated, leaving users unsure which source to trust.

## Solution (two sentences)
StillTrue extracts actionable claims and compares them with retrieved official evidence. It returns claim-level freshness verdicts, copied quotes and explicit uncertainty through a web interface and developer API.

## AI usage
An AI coding assistant helped implement and test the software. Human review, real-key validation and benchmark labelling remain required before final submission.

## Technologies
Bifrost, Tavily, Python, FastAPI, Pydantic, httpx, SQLite, React, TypeScript, Vite, Tailwind CSS, Docker, GitHub Actions.

## Truthful checklist
- [x] Runnable implementation with automated local tests
- [x] Offline mode conspicuously labelled
- [ ] Real-key end-to-end demonstration
- [ ] Human-reviewed benchmark labels and measured results
- [ ] Real captured answer and recording
- [ ] Submission form and slide deck completed by entrant

Form idea-description character limit: parameter supplied by the actual form, not guessed. Use `python scripts/count_chars.py FILE --limit N`. Keep reports and pitch claims consistent with docs/VERIFICATION.md.
