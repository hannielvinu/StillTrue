const { makeDeck } = require("./lib");
const out = process.argv[2];
const IMG = "../../docs/screenshots/live-report-panel.png";

const d = makeDeck({
  bg: "F6F2E9", dark: "0E3B31", primary: "0F5C4C", accent: "B4441B", ink: "1B1F1D", muted: "6B716C",
  card: "FFFFFF", line: "D9D3C5", footer: "StillTrue · Global AI Hackathon 2026 · Stale-Answer Detector (Tavily + Bifrost)",
});
const { pptx, T } = d;

// 1 Title
{
  const s = d.slide({ dark: true });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.25, h: 7.5, fill: { color: "E8B04B" }, line: { color: "E8B04B" } });
  s.addText("GLOBAL AI HACKATHON 2026 · STALE-ANSWER DETECTOR · TAVILY + BIFROST", { x: 0.8, y: 0.8, w: 12, h: 0.4, fontFace: "Inter", fontSize: 13, bold: true, color: "E8B04B", charSpacing: 2 });
  s.addText("StillTrue", { x: 0.8, y: 1.6, w: 11, h: 1.5, fontFace: "Poppins", fontSize: 72, bold: true, color: "FFFFFF" });
  s.addText("Is what your AI told you still true today?", { x: 0.8, y: 3.1, w: 11.5, h: 0.8, fontFace: "Poppins", fontSize: 30, color: "CFE7DF" });
  s.addText("Paste any AI answer. Every claim you would act on (a price, a version, a fee, a deadline) is checked live against the organisation that publishes it, with a word-for-word official quote.", { x: 0.8, y: 4.1, w: 11, h: 1.0, fontFace: "Inter", fontSize: 18, color: "FFFFFF" });
  [["79% vs 61%", "correct vs the same AI alone (28 claims)"], ["6 / 7 vs 0 / 7", "on facts newer than the AI's training"], ["22 of 23", "verdicts right when it commits"]].forEach(([a, b], i) => {
    const x = 0.8 + i * 4.0;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 5.45, w: 3.7, h: 1.35, rectRadius: 0.1, fill: { color: "14503F" }, line: { color: "2E6B5A" } });
    s.addText(a, { x: x + 0.2, y: 5.5, w: 3.3, h: 0.7, fontFace: "Poppins", fontSize: 28, bold: true, color: "E8B04B" });
    s.addText(b, { x: x + 0.2, y: 6.15, w: 3.3, h: 0.55, fontFace: "Inter", fontSize: 13, color: "FFFFFF" });
  });
}

// 2 Problem
{
  const s = d.slide({ n: 2 });
  d.heading(s, "The problem", "AI answers go out of date silently");
  d.bullets(s, [
    "A model learns the world once, then answers for months or years. Prices, supported versions, visa fees and tax limits keep changing.",
    "The stale answer sounds exactly as confident as a correct one. Nothing on screen says \"this may be old\".",
    "Search alone does not fix it: the web is full of old blog posts and copies. Even official help pages can lag.",
    "People and apps act on these answers: they deploy unsupported software, pay the wrong fee, file the wrong form.",
  ], 0.6, 1.9, 6.6, 4.6, 17);
  d.card(s, 7.6, 1.9, 5.1, 4.7);
  s.addText("Measured on 21 Nov 2026", { x: 7.85, y: 2.05, w: 4.7, h: 0.4, fontFace: "Inter", fontSize: 12, bold: true, color: T.accent });
  s.addText("We asked a strong open model (gpt-oss-120b, no search): \"Is this still true today?\"", { x: 7.85, y: 2.45, w: 4.7, h: 0.8, fontFace: "Inter", fontSize: 14, color: T.ink });
  const rows = [["Python 3.14 is supported", "Outdated ✗"], ["PostgreSQL 18 is supported", "Outdated ✗"], ["Ubuntu 26.04 LTS is supported", "Outdated ✗"], ["Kubernetes 1.36 is supported", "Outdated ✗"]];
  rows.forEach(([c, v], i) => {
    s.addText(c, { x: 7.85, y: 3.35 + i * 0.55, w: 3.3, h: 0.45, fontFace: "Inter", fontSize: 13, color: T.ink });
    s.addText(v, { x: 11.1, y: 3.35 + i * 0.55, w: 1.5, h: 0.45, fontFace: "Inter", fontSize: 13, bold: true, color: T.accent });
  });
  s.addText("All four are current (official pages). The AI called all 7 new releases in our test \"outdated\": 0/7.", { x: 7.85, y: 5.6, w: 4.7, h: 0.85, fontFace: "Inter", fontSize: 13, bold: true, color: T.primary });
}

// 3 Solution + innovation
{
  const s = d.slide({ n: 3 });
  d.heading(s, "The solution", "Claim-by-claim checks against the source of truth");
  const items = [
    ["Still true · Changed · Couldn't confirm", "Each actionable claim gets its own verdict, the current value, a freshness score and a corrected answer you can copy."],
    ["The publisher of the fact is the authority", "For each claim the AI names who officially publishes it (python.org, ubuntu.com, gov.uk). Tavily searches there first. Government sites count; blogs, wikis and aggregators never do."],
    ["No quote, no verdict", "A verdict needs a ≤25-word quote found word for word on an official page. Paraphrase gets one repair try, otherwise \"Couldn't confirm\". It never guesses."],
    ["Two independent AIs must agree", "Two models from two providers judge separately through Bifrost. If they disagree on the current value, there is no verdict."],
  ];
  items.forEach(([h, b], i) => {
    const x = 0.6 + (i % 2) * 6.2, y = 1.95 + Math.floor(i / 2) * 2.45;
    d.card(s, x, y, 5.95, 2.2);
    s.addShape(pptx.ShapeType.rect, { x, y: y + 0.25, w: 0.09, h: 1.7, fill: { color: i === 0 ? T.accent : T.primary }, line: { color: i === 0 ? T.accent : T.primary } });
    s.addText(h, { x: x + 0.3, y: y + 0.2, w: 5.45, h: 0.55, fontFace: "Poppins", fontSize: 17, bold: true, color: T.ink, fit: "shrink" });
    s.addText(b, { x: x + 0.3, y: y + 0.8, w: 5.45, h: 1.3, fontFace: "Inter", fontSize: 13.5, color: T.ink, fit: "shrink" });
  });
}

// 4 Architecture
{
  const s = d.slide({ n: 4 });
  d.heading(s, "Technical architecture", "Tavily finds the evidence; Bifrost runs every model call");
  d.flow(s, [
    { tag: "BIFROST", title: "Extract claims", sub: "Groq gpt-oss-20b pulls out prices, versions, deadlines; names each fact's official publisher" },
    { tag: "TAVILY", title: "Publisher-first search", sub: "Search the publisher's domain (advanced), wider basic search if needed, then extract the official pages" },
    { tag: "BIFROST", title: "Two verifiers", sub: "Groq gpt-oss-120b and NVIDIA Nemotron judge independently; fallbacks off so agreement is real" },
    { tag: "CODE, NO AI", title: "Evidence gates", sub: "Quote must be on an official page; numbers must match; else Couldn't confirm" },
    { tag: "OUTPUT", title: "Verdict + fix", sub: "Freshness score, dated quote, link, and a corrected answer" },
  ], 0.6, 1.95, 12.1, 2.55);
  d.card(s, 0.6, 4.8, 5.95, 1.95);
  s.addText("How Tavily contributes", { x: 0.85, y: 4.9, w: 5.5, h: 0.4, fontFace: "Poppins", fontSize: 15, bold: true, color: T.primary });
  s.addText("Live search restricted to the publisher's domain (include_domains), then Extract with the claim as the query to pull the exact table row or sentence. Evidence is cached by claim and topic.", { x: 0.85, y: 5.3, w: 5.5, h: 1.4, fontFace: "Inter", fontSize: 13, color: T.ink, fit: "shrink" });
  d.card(s, 6.75, 4.8, 5.95, 1.95);
  s.addText("How Bifrost contributes", { x: 7.0, y: 4.9, w: 5.5, h: 0.4, fontFace: "Poppins", fontSize: 15, bold: true, color: T.primary });
  s.addText("One OpenAI-compatible gateway for Groq and NVIDIA (custom provider), with request fallbacks for extraction, none for verification, and virtual keys. Swapping a model is a config change.", { x: 7.0, y: 5.3, w: 5.5, h: 1.4, fontFace: "Inter", fontSize: 13, color: T.ink, fit: "shrink" });
}

// 5 Prototype
{
  const s = d.slide({ n: 5 });
  d.heading(s, "Working prototype (real live run)", "It catches all three outdated recommendations");
  s.addImage({ path: IMG, x: 0.6, y: 1.8, w: 2.79, h: 5.17 });
  d.bullets(s, [
    { text: "Input: an AI-style answer recommending Ubuntu 20.04, Node.js 20 and PostgreSQL 14 for a new server.", bold: false },
    "Result: \"0 of 3 checked claims are still true\". All three are Changed.",
    "Ubuntu: \"For Ubuntu 20.04 LTS, this support lasted until 31 May 2025\" (ubuntu.com).",
    "PostgreSQL 14: support ended \"November 12, 2026\", nine days before this run (postgresql.org).",
    "A corrected answer, annotated text, run details and a copyable report.",
    "Also: REST API with live progress (SSE), a verified-chat endpoint for apps, and personal details masked before any call.",
  ], 3.75, 1.95, 8.95, 4.9, 16);
}

// 6 Proof
{
  const s = d.slide({ n: 6 });
  d.heading(s, "Measured, not claimed", "28 claims, each labelled against the official page");
  d.bars(s, [
    { label: "Correct verdicts (28)", a: 22, b: 17, max: 28, fmt: (v) => `${v}/28` },
    { label: "New facts after the AI's training (7)", a: 6, b: 0, max: 7, fmt: (v) => `${v}/7` },
    { label: "Right when it commits to a verdict", a: 96, b: 68, max: 100, fmt: (v) => `${v}%` },
  ], 0.6, 2.4, 7.6, ["StillTrue", "Same model alone (gpt-oss-120b, no search)"], { rowH: 1.15, labelW: 3.1 });
  d.card(s, 8.6, 1.95, 4.1, 4.85);
  s.addText("Honest details", { x: 8.85, y: 2.05, w: 3.7, h: 0.4, fontFace: "Poppins", fontSize: 15, bold: true, color: T.primary });
  d.bullets(s, [
    "Cost: about 2.6 Tavily credits per claim, all on free tiers (Tavily, Groq, NVIDIA).",
    "Median 18.6 s per claim (two verifiers plus evidence fetch).",
    "1 wrong verdict: a government help page still says ₹50 lakh for Schedule AL; we quote it, visibly dated.",
    "5 \"Couldn't confirm\": the quote gate refused 3 inexact quotes, 1 model disagreement, 1 provider error.",
    "Raw results and labels are in the repo.",
  ], 8.85, 2.5, 3.7, 4.2, 12.5);
}

// 7 Impact / scale
{
  const s = d.slide({ n: 7 });
  d.heading(s, "Impact and scale", "A freshness layer any AI answer can pass through");
  const cols = [
    ["People", "Check an AI answer before acting on it: software choices, fees, allowances, deadlines. Free web app; no account; personal details masked."],
    ["Developers", "One API call (or the verified-chat endpoint) adds freshness stamps to any chatbot or agent output behind Bifrost."],
    ["Scale and cost", "Evidence cache by claim; publisher-first search keeps credits low; topic packs are YAML; models swap through Bifrost config."],
  ];
  cols.forEach(([h, b], i) => {
    const x = 0.6 + i * 4.07;
    d.card(s, x, 1.95, 3.85, 2.6);
    s.addText(h, { x: x + 0.25, y: 2.1, w: 3.4, h: 0.45, fontFace: "Poppins", fontSize: 17, bold: true, color: T.primary });
    s.addText(b, { x: x + 0.25, y: 2.6, w: 3.4, h: 1.85, fontFace: "Inter", fontSize: 13.5, color: T.ink, fit: "shrink" });
  });
  s.addText("Next", { x: 0.6, y: 4.85, w: 3, h: 0.4, fontFace: "Poppins", fontSize: 17, bold: true, color: T.ink });
  d.bullets(s, [
    "Conflict detection when two official pages disagree (our one miss), shown to the user instead of silently picking one.",
    "Browser extension that checks answers inside ChatGPT, Claude and Gemini.",
    "More topic packs (health guidance, travel rules), each with curated official domains.",
  ], 0.6, 5.25, 12.1, 1.6, 14);
}

// 8 Links
{
  const s = d.slide({ n: 8 });
  d.heading(s, "Try it", "Open source, reproducible, built during the hackathon");
  d.bullets(s, [
    "Code, setup and benchmark: github.com/hannielvinu/StillTrue",
    "Run: copy .env.example, add free Tavily, Groq and NVIDIA keys, docker compose up, open localhost:8000.",
    "Reproduce the numbers: make bench (labels in benchmark/claims.jsonl, results in benchmark/results/).",
    "Tech: Bifrost v2.4.0, Tavily Search + Extract, Groq gpt-oss-20b / gpt-oss-120b, NVIDIA Nemotron 3.5 Lightning, FastAPI, React + TypeScript, SQLite, Docker.",
    "AI use: models extract, verify and rewrite claims; an AI coding assistant helped build and test the code.",
  ], 0.6, 1.95, 12.1, 4.6, 17);
}

d.save(out).then(() => console.log("saved", out));
