# StillTrue speaker script
Event time limit unknown. Full main-deck target: 4:40 (280 seconds). Backup slides are Q&A only.

## Three-minute cut
S1 10s; S2 20s; S3 10s; S4 20s; S5 20s; S6 55s; S7 25s; S8 20s = 180s. S3 and S8 are shortened; trimming only those two cannot reduce 4:40 to 3:00. Other cuts and a shorter demo are necessary.

## S1 — StillTrue
Timing: 0:00 · 10 seconds. Criterion: Innovation; problem and impact
We built StillTrue to check whether an actionable AI answer is still current. We show the evidence and keep uncertainty visible.

## S2 — An AI told a taxpayer to fill a form. The rule had changed.
Timing: 0:10 · 25 seconds. Criterion: Problem and impact
A reported case described an engineer using an AI assistant for an ITR-2 filing. It gave an outdated Schedule AL instruction. The supplied reporting and official page describe a move from fifty lakh to one crore. We do not claim an assessment year, and we do not present this as our own captured model response.

## S3 — People act on AI answers about money. Companies own their bots’ words.
Timing: 0:35 · 25 seconds. Criterion: Problem and potential impact
Our supplied sources report roughly twenty-eight million UK users of AI for money guidance. A survey of five hundred accountants found half knew businesses harmed by wrong AI advice. Air Canada owed eight hundred twelve Canadian dollars and two cents after its chatbot invented a fare policy. That was fabrication, not stale information: a different failure, the same responsibility lesson.

## S4 — The live web is stale too.
Timing: 1:00 · 30 seconds. Criterion: Innovation; use of AI
Search alone does not resolve conflicting pages. The supplied brief describes an official one-crore threshold and a secondary guide showing fifty lakh. We need dated captures before displaying them as observed evidence. We deliberately leave those screenshots as placeholders and do not infer what a particular chatbot would choose.

## S5 — Five steps, official sources first.
Timing: 1:30 · 30 seconds. Criterion: Technical execution; use of AI
We extract time-sensitive claims, search allow-listed official domains through Tavily, read the evidence, and route model judgments through Bifrost. Approved official evidence and a matching quote are required for definitive verdicts. The implementation can make a broader discovery search when official results are missing, but secondary material alone cannot produce a definitive verdict.

## S6 — Watch it catch the change.
Timing: 2:00 · 90 seconds. Criterion: Working prototype; user experience
For this segment, we will paste an actually captured model answer and show its capture model and date. Then we will show a completed real check, its copied evidence and official page. At present the capture, recording and live deployment have not been supplied or validated, so this slide displays unmistakable placeholders. If the live demo fails, switch to a genuine recorded run and say plainly that it is recorded. If no real recording exists, show the labelled offline UI demonstration and say that it does not verify claims.

## S7 — Built on both sponsors, and measured.
Timing: 3:30 · 40 seconds. Criterion: Technical execution; scalability
The architecture separates model routing, retrieval, evidence caching and deterministic verdict checks. Sponsor feature status starts planned until the author marks it verified. The benchmark panel remains empty because no real results file exists. When measured, it compares accuracy and false-Still-true rate against a no-retrieval baseline, including sample size and latency. A small sample will be explicitly labelled.

## S8 — From one checked claim to a trusted layer for AI answers.
Timing: 4:10 · 30 seconds. Criterion: Potential impact; scalability
Our path is free access for people and the same engine as an API for developers. More source packs, a browser extension and team audit logs are next steps, not shipped traction. We cover claims with official online sources; sources can lag and models can err. This is not professional advice. We want evidence to be inspectable before someone acts.

## B1 — Backup: landscape and Q&A
Timing: 4:40 · 0 seconds. Criterion: Innovation; questions
These are descriptions from the supplied listings, not a comparative product test. Verity offers freshness verdicts through a Chrome extension and MCP. jev exposes claim verification. 402oracle offers paid claim and URL freshness checks. StillTrue focuses on official evidence, dated claim-level explanations and a consumer plus developer flow. We have not demonstrated superiority over these products.

## B2 — Backup: privacy and limits
Timing: 4:40 · 0 seconds. Criterion: Security; technical execution
The full application sends masked claims and evidence to the configured model provider through Bifrost, and derived search queries and official URLs to Tavily. Regex masking can miss personal information. Pasted text is not persisted to disk; temporary jobs exist in memory. SQLite retains retrieved evidence and budget counters. The static offline demo calls neither service. Provider retention policies still apply.
