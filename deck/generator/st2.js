const { deck } = require("./lib2");
const A = "/tmp/claude-0/-home-user/e323aa61-8f0e-5334-831c-29839f98ed72/scratchpad/deck2/";
const X = deck({
  bg: "F7F3EA", dark: "0B2E27", primary: "0F5C4C", accent: "E8A33D", accent2: "F2C46D", ink: "16201D", muted: "6B736E",
  card: "FFFFFF", line: "DDD6C6", red: "C2410C", soft: "E7F0EC",
  footer: "StillTrue · Global AI Hackathon 2026 · Stale-Answer Detector · Tavily + Bifrost",
});
const { pptx, T } = X;

// 1. Title
{
  const s = X.slide(true);
  s.addShape(pptx.ShapeType.ellipse, { x: 8.4, y: -2.2, w: 7.5, h: 7.5, fill: { color: "0F4A3D" }, line: { color: "0F4A3D" } });
  X.t(s, "GLOBAL AI HACKATHON 2026", 0.7, 0.7, 6, 0.35, { size: 12, bold: true, color: T.accent2, cs: 3 });
  X.t(s, "StillTrue", 0.7, 1.25, 7, 1.3, { font: X.H, size: 66, bold: true, color: "FFFFFF" });
  X.t(s, "Is what your AI told you still true today?", 0.7, 2.6, 6.6, 1.1, { font: X.H, size: 26, color: "CFE5DC" });
  X.t(s, "Paste any AI answer. Every price, version and deadline is checked live against the organisation that publishes it, with a word-for-word official quote.", 0.7, 3.8, 6.3, 1.2, { size: 15.5, color: "FFFFFF", ls: 1.15 });
  let x = 0.7;
  for (const [t, f] of [["Stale-Answer Detector", T.accent], ["Tavily", "1E7A66"], ["Bifrost", "1E7A66"]]) x += X.pill(s, t, x, 5.3, { fill: f, color: f === T.accent ? "0B2E27" : "FFFFFF" }) + 0.12;
  X.t(s, "github.com/hannielvinu/StillTrue", 0.7, 6.55, 6, 0.35, { size: 12, color: "9FC2B6" });
  X.browser(s, A + "st-report.png", 7.45, 1.35, 5.4, 4.6, { url: "localhost:8000 · live run, 21 Nov 2026" });
}

// 2. Hook
{
  const s = X.slide();
  X.head(s, "The problem", "AI answers expire. Nobody tells you.");
  X.t(s, "0 / 7", 0.55, 1.85, 5.2, 2.0, { font: X.H, size: 120, bold: true, color: T.red, valign: "middle" });
  X.t(s, "A strong open model (gpt-oss-120b) judged 7 software releases newer than its training. It called every one of them \"outdated\".", 0.6, 3.95, 5.0, 1.3, { size: 16, ls: 1.15 });
  X.t(s, "Measured 21 Nov 2026 · Python 3.14, PostgreSQL 18, Ubuntu 26.04, Kubernetes 1.36, PHP 8.5, Go 1.27, Node.js 26", 0.6, 5.3, 5.0, 0.8, { size: 11, color: T.muted });
  const pains = [
    ["Confident, not current", "A stale answer reads exactly like a correct one. Nothing says \"this may be old\"."],
    ["People act on it", "Deploy unsupported software, pay the wrong visa fee, file the wrong tax form."],
    ["Search alone doesn't fix it", "Old blogs and copies outrank the source. Even official help pages can lag."],
  ];
  pains.forEach(([h, b], i) => {
    const y = 1.95 + i * 1.6;
    X.box(s, 6.3, y, 6.5, 1.38, { shadow: true });
    X.dot(s, String(i + 1), 6.55, y + 0.36, 0.62, { fill: i === 0 ? T.red : T.primary });
    X.t(s, h, 7.4, y + 0.18, 5.2, 0.45, { font: X.H, size: 17, bold: true });
    X.t(s, b, 7.4, y + 0.62, 5.2, 0.7, { size: 13.5, color: "3A4440" });
  });
}

// 3. Solution
{
  const s = X.slide();
  X.head(s, "The solution", "Claim-by-claim truth, from the source");
  X.browser(s, A + "st-ubuntu.png", 0.55, 1.8, 5.9, 4.9, { url: "StillTrue · claim card" });
  const p = [
    ["Still true · Changed · Couldn't confirm", "Every actionable claim gets its own verdict, the current value, a freshness score, and a corrected answer to copy."],
    ["The publisher is the authority", "python.org for Python, ubuntu.com for Ubuntu, gov.uk for UK fees. Government sites count; blogs, wikis and aggregators never do."],
    ["No quote, no verdict", "A ≤25-word quote must appear word for word on an official page, and two independent AI models must agree."],
  ];
  p.forEach(([h, b], i) => {
    const y = 1.85 + i * 1.65;
    X.dot(s, String(i + 1), 6.9, y + 0.05, 0.55, { fill: i === 2 ? T.accent : T.primary, color: i === 2 ? "0B2E27" : "FFFFFF" });
    X.t(s, h, 7.65, y, 5.2, 0.45, { font: X.H, size: 17.5, bold: true });
    X.t(s, b, 7.65, y + 0.48, 5.2, 1.05, { size: 13.5, color: "3A4440", ls: 1.1 });
  });
}

// 4. Architecture
{
  const s = X.slide();
  X.head(s, "How it works", "Tavily finds the proof. Bifrost runs the judges.");
  const steps = [
    ["Extract", "Claims you'd act on + each fact's official publisher", "BIFROST", "gpt-oss-20b"],
    ["Search", "Publisher domain first, then a wider basic search", "TAVILY", "Search"],
    ["Read", "Pull the exact sentence or table row from official pages", "TAVILY", "Extract"],
    ["Judge ×2", "Two models, two providers, judged separately", "BIFROST", "gpt-oss-120b + Nemotron"],
    ["Gate", "Quote on page? Values agree? Else Couldn't confirm", "CODE", "no AI"],
  ];
  const w = 2.25, gap = 0.24, y = 2.05;
  steps.forEach(([h, b, tag, sub], i) => {
    const x = 0.55 + i * (w + gap);
    const c = tag === "TAVILY" ? "1E6FB8" : tag === "BIFROST" ? T.primary : T.accent;
    X.box(s, x, y, w, 2.75, { shadow: true });
    s.addShape(pptx.ShapeType.rect, { x, y, w, h: 0.42, fill: { color: c }, line: { color: c } });
    X.t(s, tag, x, y, w, 0.42, { size: 11, bold: true, color: tag === "CODE" ? "0B2E27" : "FFFFFF", align: "center", valign: "middle", cs: 2 });
    X.dot(s, String(i + 1), x + w / 2 - 0.3, y + 0.58, 0.6, { fill: c, color: tag === "CODE" ? "0B2E27" : "FFFFFF" });
    X.t(s, h, x + 0.1, y + 1.25, w - 0.2, 0.42, { font: X.H, size: 16, bold: true, align: "center" });
    X.t(s, b, x + 0.12, y + 1.68, w - 0.24, 0.75, { size: 11.5, color: "3A4440", align: "center" });
    X.t(s, sub, x + 0.1, y + 2.4, w - 0.2, 0.3, { size: 10.5, bold: true, color: c === T.accent ? "8A5A12" : c, align: "center" });
    if (i < steps.length - 1) X.arrow(s, x + w + 0.02, y + 1.4, x + w + gap - 0.02, y + 1.4);
  });
  X.box(s, 0.55, 5.15, 6.0, 1.6, { fill: "E8F1FA", line: "BFD6EE" });
  X.t(s, "Tavily's role", 0.8, 5.28, 5.5, 0.38, { font: X.H, size: 15, bold: true, color: "1E6FB8" });
  X.t(s, "Live search restricted to the publisher (include_domains), then Extract with the claim as the query. Evidence is cached per claim: about 2.6 credits per claim.", 0.8, 5.66, 5.6, 1.0, { size: 12.5 });
  X.box(s, 6.8, 5.15, 6.0, 1.6, { fill: T.soft, line: "C3DBD1" });
  X.t(s, "Bifrost's role", 7.05, 5.28, 5.5, 0.38, { font: X.H, size: 15, bold: true, color: T.primary });
  X.t(s, "One OpenAI-compatible gateway for Groq and NVIDIA. Fallbacks for extraction, none for verification (so agreement is real), virtual keys, swap models by config.", 7.05, 5.66, 5.6, 1.0, { size: 12.5 });
}

// 5. Live demo
{
  const s = X.slide();
  X.head(s, "Working prototype · real live run", "An answer goes in. The truth comes out.");
  X.browser(s, A + "st-input.png", 0.55, 1.8, 4.6, 4.95, { url: "1 · paste the answer" });
  X.arrow(s, 5.3, 4.25, 5.85, 4.25, { w: 3 });
  X.browser(s, A + "st-report.png", 5.95, 1.8, 4.3, 3.0, { url: "2 · verdict" });
  X.browser(s, A + "st-ubuntu.png", 5.95, 4.95, 4.3, 1.8, { url: "3 · proof" });
  const facts = [["Ubuntu 20.04", "Standard support ended 31 May 2025"], ["Node.js 20", "End of life April 2026"], ["PostgreSQL 14", "Ended 12 Nov 2026: nine days before this run"]];
  X.t(s, "All 3 flagged Changed", 10.5, 1.85, 2.4, 0.45, { font: X.H, size: 15, bold: true, color: T.red });
  facts.forEach(([h, b], i) => {
    const y = 2.45 + i * 1.35;
    X.box(s, 10.5, y, 2.35, 1.2, { fill: "FFF4EE", line: "F2C9B4" });
    X.t(s, h, 10.62, y + 0.1, 2.15, 0.35, { size: 13, bold: true });
    X.t(s, b, 10.62, y + 0.45, 2.15, 0.7, { size: 11, color: "3A4440" });
  });
  X.t(s, "Plus a corrected answer, annotated text, a REST API with live progress, and personal details masked before any call.", 10.5, 6.55, 2.4, 0.45, { size: 8.5, color: T.muted });
}

// 6. Results
{
  const s = X.slide();
  X.head(s, "Measured, not claimed", "28 real claims, each labelled against the official page");
  X.big(s, "6 / 7", "on facts newer than the AI's training. The same model alone: 0 / 7.", 0.55, 1.75, 3.9, { color: T.primary });
  X.big(s, "79%", "correct overall, vs 61% for the same model answering alone (22 vs 17 of 28).", 4.6, 1.75, 3.9, { color: T.primary });
  X.big(s, "22 / 23", "right when StillTrue commits to a verdict. It says \"Couldn't confirm\" instead of guessing.", 8.65, 1.75, 4.2, { color: T.accent });
  X.bars(s, [
    { label: "Correct (of 28)", a: 22, b: 17, max: 28, fa: "22", fb: "17" },
    { label: "New facts (of 7)", a: 6, b: 0, max: 7, fa: "6", fb: "0" },
    { label: "Right when it commits", a: 96, b: 68, max: 100, fa: "96%", fb: "68%" },
  ], 0.55, 4.45, 8.0, 0.78, ["StillTrue", "Same model, no search"]);
  X.box(s, 8.9, 4.0, 3.95, 2.75, { fill: "FFF8EC", line: "EFD9AE" });
  X.t(s, "Honest about misses", 9.1, 4.1, 3.6, 0.4, { font: X.H, size: 14, bold: true, color: "8A5A12" });
  X.t(s, "1 wrong verdict: an official incometax.gov.in help page still says ₹50 lakh for Schedule AL. StillTrue quoted it, dated. Conflicting official sources are our next feature.\n\nRaw results and labels are in the repo; reproduce with make bench.", 9.1, 4.5, 3.6, 2.2, { size: 11.5, ls: 1.1 });
}

// 7. Trust & safety
{
  const s = X.slide();
  X.head(s, "Built to be trusted", "It would rather say \"I don't know\" than guess");
  const cards = [
    ["Evidence gate", "Deterministic code checks every quote on an official page; numbers from both models must match."],
    ["Independent judges", "Two models on two providers via Bifrost; fallbacks off for verification."],
    ["Privacy", "Names, emails, phone and ID numbers are masked before any model or search call."],
    ["Visible uncertainty", "Couldn't confirm is a first-class result, with the reason shown."],
    ["Free-tier friendly", "Evidence cache, publisher-first search, token ledger, Retry-After handling."],
    ["Open & reproducible", "MIT licence, Docker Compose, labelled benchmark, every run's raw output."],
  ];
  cards.forEach(([h, b], i) => {
    const x = 0.55 + (i % 3) * 4.15, y = 1.85 + Math.floor(i / 3) * 2.45;
    X.box(s, x, y, 3.95, 2.2, { shadow: true });
    s.addShape(pptx.ShapeType.rect, { x: x + 0.3, y: y + 0.3, w: 0.55, h: 0.08, fill: { color: i % 2 ? T.accent : T.primary }, line: { color: i % 2 ? T.accent : T.primary } });
    X.t(s, h, x + 0.3, y + 0.5, 3.4, 0.45, { font: X.H, size: 17, bold: true });
    X.t(s, b, x + 0.3, y + 1.0, 3.4, 1.1, { size: 13, color: "3A4440", ls: 1.1 });
  });
}

// 8. Impact
{
  const s = X.slide();
  X.head(s, "Impact and scale", "A freshness layer every AI answer can pass through");
  const who = [
    ["People", "Check an AI answer before acting: software, fees, allowances, deadlines. Free web app, no account."],
    ["Developers", "One API call adds freshness stamps to any chatbot or agent output behind Bifrost."],
    ["Teams", "Audit AI-written docs and support replies before they ship; every verdict links its source."],
  ];
  who.forEach(([h, b], i) => {
    const x = 0.55 + i * 4.15;
    X.box(s, x, 1.85, 3.95, 2.25, { fill: i === 1 ? T.dark : T.card, line: i === 1 ? T.dark : T.line, shadow: true });
    X.t(s, h, x + 0.3, 2.0, 3.4, 0.5, { font: X.H, size: 19, bold: true, color: i === 1 ? "FFFFFF" : T.ink });
    X.t(s, b, x + 0.3, 2.55, 3.4, 1.45, { size: 13.5, color: i === 1 ? "D7E7E0" : "3A4440", ls: 1.12 });
  });
  X.t(s, "ROADMAP", 0.55, 4.45, 3, 0.3, { size: 11, bold: true, color: T.primary, cs: 3 });
  s.addShape(pptx.ShapeType.line, { x: 0.9, y: 5.35, w: 11.6, h: 0, line: { color: T.line, width: 3 } });
  [["Now", "Live web app + API, 5 topic packs, measured benchmark"], ["Next", "Detect conflicting official sources (our one miss)"], ["Then", "Browser extension that checks answers inside any AI chat"], ["Later", "Health and travel packs with curated official domains"]].forEach(([h, b], i) => {
    const x = 0.9 + i * 3.05;
    X.dot(s, "", x - 0.16, 5.19, 0.32, { fill: i === 0 ? T.accent : T.primary });
    X.t(s, h, x - 0.16, 5.6, 2.8, 0.35, { font: X.H, size: 14, bold: true });
    X.t(s, b, x - 0.16, 5.95, 2.8, 0.8, { size: 12, color: "3A4440" });
  });
}

// 9. Close
{
  const s = X.slide(true);
  X.t(s, "Before you act on an AI answer,", 0.8, 1.7, 11.5, 0.9, { font: X.H, size: 36, color: "CFE5DC" });
  X.t(s, "check it's still true.", 0.8, 2.55, 11.5, 1.2, { font: X.H, size: 54, bold: true, color: "FFFFFF" });
  const st = [["6 / 7", "new facts right (AI alone: 0 / 7)"], ["22 / 23", "right when it commits"], ["2.6", "Tavily credits per claim"]];
  st.forEach(([a, b], i) => {
    const x = 0.8 + i * 4.0;
    X.t(s, a, x, 4.15, 3.6, 0.8, { font: X.H, size: 38, bold: true, color: T.accent2 });
    X.t(s, b, x, 4.95, 3.6, 0.5, { size: 14, color: "FFFFFF" });
  });
  X.t(s, "github.com/hannielvinu/StillTrue  ·  Tavily + Bifrost  ·  Groq + NVIDIA models  ·  MIT", 0.8, 6.3, 11.5, 0.4, { size: 13, color: "9FC2B6" });
  X.t(s, "AI use: models extract, verify and rewrite claims through Bifrost; an AI coding assistant helped build the code.", 0.8, 6.75, 11.5, 0.35, { size: 10, color: "6F978A" });
}

X.save(process.argv[2]).then(() => console.log("saved"));
