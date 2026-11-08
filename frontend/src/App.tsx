import { useEffect, useState } from "react";
import {
  BrowserRouter,
  HashRouter,
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import {
  Clock3,
  ArrowUpRight,
  Sun,
  Moon,
  ShieldCheck,
  Search,
  FileCheck2,
} from "lucide-react";
import { api } from "./lib/api";
import { offlineDemo } from "./lib/offlineDemo";
import { useVerifyStream } from "./lib/useVerifyStream";
import {
  ClaimCard,
  Summary,
  Diff,
  PiiNotice,
  labels,
} from "./components/Results";
import type { Meta, Pack, Run } from "./types";
const examples = [
  {
    pack: "india_tax",
    text: "Schedule AL must be filled if total income exceeds ₹50 lakh.",
    label: "Tax threshold",
  },
  {
    pack: "uk_personal_finance",
    text: "The annual ISA allowance is £20,000.",
    label: "Savings allowance",
  },
  {
    pack: "developer_apis",
    text: "The legacy API endpoint will remain available after January 2025.",
    label: "API deprecation",
  },
];
function Check({ meta }: { meta: Meta | null }) {
  const [text, setText] = useState(""),
    [question, setQuestion] = useState(""),
    [pack, setPack] = useState("india_tax"),
    [packs, setPacks] = useState<Pack[]>([]),
    [packError, setPackError] = useState("");
  const stream = useVerifyStream();
  const load = () =>
    api<Pack[]>("/api/v1/packs")
      .then(setPacks)
      .catch((e) => setPackError(e.message));
  useEffect(() => {
    load();
  }, []);
  const limit = meta?.max_input_chars ?? 6000;
  const selected = packs.find((p) => p.id === pack);
  function submit(e: React.FormEvent) {
    e.preventDefault();
    stream.start({ text, question, pack, redact: true });
  }
  const copy = () =>
    navigator.clipboard.writeText(
      (stream.run?.mock ? "MOCK DATA — synthetic results\n" : "") +
        stream.results
          .map(
            (r) =>
              `${r.claim.text} — ${labels[r.verdict]}\n${r.evidence.map((e) => e.url).join("\n")}`,
          )
          .join("\n\n") +
        "\nChecked: " +
        stream.run?.checked_at,
    );
  return (
    <>
      <div className="hero">
        <span className="eyebrow">A SECOND LOOK, BEFORE YOU ACT</span>
        <h1>
          Is what your AI told you
          <br />
          <em>still true?</em>
        </h1>
        <p>
          Answers age. Check the claims that matter against live official
          sources.
        </p>
      </div>
      <div className="workspace">
        <section className="input-panel">
          <form onSubmit={submit}>
            <div className="row spread">
              <label htmlFor="answer">Paste an AI answer</label>
              <span className="mono muted">01 / INPUT</span>
            </div>
            <textarea
              id="answer"
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={limit}
              required
              placeholder="That tax threshold. A visa requirement. The deadline you’re about to rely on…"
            />
            <div className="counter">
              {text.length.toLocaleString()} / {limit.toLocaleString()}
            </div>
            <label htmlFor="question">
              What did you ask the AI? <small>(optional)</small>
            </label>
            <input
              id="question"
              value={question}
              maxLength={1000}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Add context for a more relevant check"
            />
            <label htmlFor="pack">Topic</label>
            <select
              id="pack"
              value={pack}
              onChange={(e) => setPack(e.target.value)}
            >
              {packs.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name.replaceAll("_", " ")}
                </option>
              ))}
            </select>
            <p className="muted small">{selected?.description}</p>
            <details>
              <summary>What does this check against?</summary>
              <p>
                {selected?.tier1_domains.join(", ") ||
                  "No approved official domains in this pack. Verdicts remain Unconfirmed."}
              </p>
            </details>
            {packError && (
              <p role="alert">
                {packError}{" "}
                <button type="button" onClick={load}>
                  Retry
                </button>
              </p>
            )}
            <div className="actions">
              <button
                className="primary"
                disabled={stream.busy || !text.trim() || !packs.length}
              >
                {stream.busy ? "Checking…" : "Check freshness"}{" "}
                <ArrowUpRight size={18} />
              </button>
              {stream.busy ? (
                <button type="button" onClick={stream.cancel}>
                  Stop
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setText("");
                    setQuestion("");
                  }}
                >
                  Clear
                </button>
              )}
            </div>
            <p className="privacy">
              <ShieldCheck size={15} /> Personal details are masked before
              checking.
            </p>
          </form>
          <div className="examples">
            <span className="eyebrow">TRY AN EXAMPLE</span>
            <div className="row wrap">
              {examples.map((e) => (
                <button
                  key={e.pack}
                  onClick={() => {
                    setText(e.text);
                    setPack(e.pack);
                  }}
                >
                  {e.label}
                </button>
              ))}
            </div>
            <small>Example text (illustrative), not a captured AI answer</small>
          </div>
        </section>
        <section className="results-panel" aria-label="Freshness results">
          <div className="row spread">
            <span className="eyebrow">YOUR REPORT</span>
            <span className="mono muted">02 / EVIDENCE</span>
          </div>
          <PiiNotice count={stream.pii} />
          <p aria-live="polite">{stream.stage}</p>
          {stream.error && (
            <div role="alert" className="notice">
              {stream.error}
              <button
                onClick={() =>
                  stream.start({ text, question, pack, redact: true })
                }
              >
                Retry
              </button>
            </div>
          )}
          {!stream.busy && !stream.run && !stream.error && (
            <div className="empty">
              <Clock3 size={44} strokeWidth={1} />
              <h2>
                A little certainty.
                <br />
                Before the next step.
              </h2>
              <p>
                Paste an answer to see what holds up,
                <br />
                what changed, and what we can’t confirm.
              </p>
              <ol>
                <li>
                  <FileCheck2 size={18} /> Find actionable claims
                </li>
                <li>
                  <Search size={18} /> Read official sources
                </li>
                <li>
                  <ShieldCheck size={18} /> Show the evidence
                </li>
              </ol>
            </div>
          )}
          {stream.busy && (
            <div className="loading">
              Checking {stream.results.length} of {stream.claims.length || "…"}{" "}
              claims
            </div>
          )}
          {stream.run && <Summary run={stream.run} />}
          <div className="claims">
            {stream.results.map((r) => (
              <ClaimCard key={r.claim.id} result={r} />
            ))}
          </div>
          {stream.run && (
            <>
              <section className="panel">
                <h2>Annotated answer</h2>
                <p className="annotated">{annotate(text, stream.results)}</p>
              </section>
              {stream.correction ? (
                <Diff correction={stream.correction} />
              ) : (
                <p className="small muted">
                  No correction: rewriting requires a confirmed change,
                  cross-model agreement and high confidence.
                </p>
              )}
              <details>
                <summary>Run details</summary>
                <pre>{JSON.stringify(stream.run.metadata, null, 2)}</pre>
              </details>
              <div className="row wrap">
                <button onClick={copy}>Copy summary</button>
                <button onClick={() => window.print()}>Print report</button>
              </div>
              <p className="small muted">
                StillTrue checks claims against sources at the time shown. It is
                not legal, tax, or financial advice. Confirm important decisions
                with the official source.
              </p>
            </>
          )}
        </section>
      </div>
    </>
  );
}
function annotate(text: string, results: Run["claims"]) {
  let cursor = 0;
  const nodes: React.ReactNode[] = [];
  for (const r of results) {
    const start = text.indexOf(r.claim.text, cursor);
    if (start < 0) continue;
    nodes.push(text.slice(cursor, start));
    nodes.push(
      <a
        className={"annotation " + r.verdict}
        href={"#" + r.claim.id}
        key={r.claim.id}
        onClick={
          offlineDemo
            ? (event) => {
                event.preventDefault();
                document.getElementById(r.claim.id)?.scrollIntoView();
              }
            : undefined
        }
      >
        {r.claim.text} [{labels[r.verdict]}]
      </a>,
    );
    cursor = start + r.claim.text.length;
  }
  nodes.push(text.slice(cursor));
  return nodes;
}
function RemotePage({ kind }: { kind: "demo" | "benchmark" }) {
  const [data, setData] = useState<any>(null),
    [state, setState] = useState("Loading…"),
    [step, setStep] = useState(0),
    [play, setPlay] = useState(false);
  const load = () => {
    setState("Loading…");
    fetch(
      import.meta.env.BASE_URL +
        (kind === "demo" ? "demo/recorded-run.json" : "benchmark/latest.json"),
    )
      .then(async (r) => {
        if (!r.ok) throw new Error();
        const d = await r.json();
        setData(d);
        setState("");
      })
      .catch(() =>
        setState(
          kind === "demo"
            ? "No recording yet. Run make record-demo."
            : "Not yet run.",
        ),
      );
  };
  useEffect(() => {
    load();
  }, [kind]);
  useEffect(() => {
    if (!play) return;
    const t = setInterval(() => setStep((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [play]);
  return (
    <section className="document">
      <span className="eyebrow">
        {kind === "demo" ? "WATCH THE CHECK" : "MEASURE, DON’T GUESS"}
      </span>
      <h1>{kind === "demo" ? "An answer. With evidence." : "Benchmark"}</h1>
      {state && <p role="status">{state}</p>}
      {!data && <button onClick={load}>Retry</button>}
      {data && kind === "benchmark" && (
        <>
          <p>Real run · {data.sample_label}</p>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </>
      )}
      {data && kind === "demo" && (
        <>
          <p className="notice">
            Recorded run, {data.date}, {data.models?.join(", ")}
          </p>
          <div className="workspace">
            <section>
              <h2>A normal chatbot answer</h2>
              <p>
                Captured from {data.capture?.model} on {data.capture?.date}
              </p>
              <blockquote>{data.capture?.raw_answer}</blockquote>
            </section>
            <section>
              <h2>With StillTrue</h2>
              <p>
                {
                  [
                    "Extract claims",
                    "Search official sources",
                    "Read evidence",
                    "Verdicts",
                  ][Math.min(step, 3)]
                }
              </p>
              {step >= 3 &&
                data.run?.claims.map((r: Run["claims"][0]) => (
                  <ClaimCard key={r.claim.id} result={r} />
                ))}
            </section>
          </div>
          <div className="row wrap">
            <button onClick={() => setPlay(!play)}>
              {play ? "Pause" : "Play"}
            </button>
            <button onClick={() => setStep((s) => s + 1)}>Next</button>
            <button
              onClick={() => {
                setStep(0);
                setPlay(false);
              }}
            >
              Restart
            </button>
            <Link to="/">Run it live</Link>
          </div>
        </>
      )}
    </section>
  );
}
function Info({ page }: { page: string }) {
  return (
    <section className="document">
      <span className="eyebrow">STILLTRUE / FIELD NOTES</span>
      {page === "how-it-works" ? (
        <>
          <h1>
            Trust the evidence.
            <br />
            See the uncertainty.
          </h1>
          <p>
            We extract actionable claims, retrieve current official evidence
            through Tavily, and ask independent models through Bifrost to judge
            each claim.
          </p>
          <svg
            viewBox="0 0 600 90"
            role="img"
            aria-label="Answer to claims to official sources to verdict"
          >
            <path d="M40 45H560" stroke="currentColor" />
            {["Answer", "Claims", "Sources", "Verdict"].map((s, i) => (
              <g key={s}>
                <rect
                  x={i * 150 + 5}
                  y="20"
                  width="135"
                  height="50"
                  rx="8"
                  fill="var(--surface)"
                  stroke="var(--brand)"
                />
                <text
                  x={i * 150 + 72}
                  y="50"
                  textAnchor="middle"
                  fill="currentColor"
                >
                  {s}
                </text>
              </g>
            ))}
          </svg>
          <h2>Official sources carry the verdict</h2>
          <p>
            Tier 1 means an approved primary source. Tier 2 adds context. Other
            pages cannot establish a Current or Changed verdict. A copied quote
            is required, and model disagreement produces Unconfirmed.
          </p>
          <h2>A score is a heuristic</h2>
          <p>
            It summarizes confidence and volatility, not a probability of truth.
            A retrieval date says when we read a page, not when the rule took
            effect.
          </p>
        </>
      ) : page === "developers" ? (
        <>
          <h1>Freshness, in your flow.</h1>
          <p>
            Call StillTrue after generating an answer. All model calls go
            through your Bifrost gateway.
          </p>
          <pre>{`curl -X POST http://localhost:8000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"text":"An answer to check", "pack":"general"}'`}</pre>
          <p>
            Use the returned job_id to subscribe to
            /api/v1/verify/&#123;job_id&#125;/events or poll
            /api/v1/verify/&#123;job_id&#125;.
          </p>
          <pre>{`import httpx
job = httpx.post("http://localhost:8000/api/v1/verify",
    json={"text": answer, "pack": "india_tax"}).json()`}</pre>
          <pre>{`from openai import OpenAI
client = OpenAI(base_url="http://localhost:8080/v1", api_key="gateway-key")
# Then annotate the generated answer with StillTrue.`}</pre>
          {offlineDemo ? (
            <p>
              API reference is available at /docs when running the full backend.
            </p>
          ) : (
            <a href="/docs">Explore the API reference ↗</a>
          )}
        </>
      ) : page === "limits" ? (
        <>
          <h1>
            Useful evidence.
            <br />
            Honest limits.
          </h1>
          <h2>Before you act</h2>
          <p>
            This is not legal, tax, financial or medical advice. Confirm
            consequential decisions with the official source. Models can misread
            pages. Official pages can lag behind policy changes. Missing
            evidence means Unconfirmed.
          </p>
          <h2>Your data</h2>
          {offlineDemo && (
            <p>
              This offline demonstration runs in your browser. Your input is not
              sent to Tavily, a model provider, or a backend. The description
              below applies to the full backend application.
            </p>
          )}
          <p>
            We mask detected personal details by default before sending claims
            and context to models through Bifrost and search queries to Tavily.
            Regex masking can miss sensitive data: remove it yourself before
            pasting. Pasted answers are held temporarily in memory for up to 30
            minutes for jobs and are not saved to disk. Only retrieved evidence
            and budget counters are cached in SQLite. Canonical cache keys and
            queries are derived from claims; avoid sensitive inputs. Provider
            retention policies apply.
          </p>
          <h2>Source coverage</h2>
          <p>
            Checks are limited to the configured packs and accessible official
            online material. Cross-model agreement is a useful check, not proof.
            Heuristic scores are not calibrated probabilities.
          </p>
        </>
      ) : (
        <>
          <h1>Page not found</h1>
          <Link to="/">Back to checking</Link>
        </>
      )}
    </section>
  );
}
function Shell() {
  const [meta, setMeta] = useState<Meta | null>(null),
    [metaError, setMetaError] = useState(false),
    [dark, setDark] = useState(
      window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false,
    );
  const location = useLocation();
  useEffect(() => {
    document.title = `StillTrue · ${location.pathname === "/" ? "Check the answer" : location.pathname.slice(1)}`;
  }, [location]);
  useEffect(() => {
    api<Meta>("/api/v1/meta")
      .then(setMeta)
      .catch(() => setMetaError(true));
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);
  return (
    <>
      <a
        className="skip"
        href="#main"
        onClick={(event) => {
          if (offlineDemo) {
            event.preventDefault();
            document.getElementById("main")?.focus();
            document.getElementById("main")?.scrollIntoView();
          }
        }}
      >
        Skip to content
      </a>
      {meta?.mock && (
        <div className="mock-banner" role="status">
          {offlineDemo ? "OFFLINE DEMO · " : ""}MOCK DATA · Synthetic fixtures
          for offline development. No live claims verified.
        </div>
      )}
      {metaError && (
        <div className="notice">
          Backend unavailable. Checks cannot run until connected.
        </div>
      )}
      <header>
        <Link to="/" className="wordmark">
          <Clock3 aria-hidden="true" />
          StillTrue<span className="wordmark-dot">.</span>
        </Link>
        <nav aria-label="Main navigation">
          <NavLink to="/">Check</NavLink>
          <NavLink to="/demo">Demo</NavLink>
          <NavLink to="/how-it-works">How it works</NavLink>
          <NavLink to="/benchmark">Benchmark</NavLink>
          <NavLink to="/developers">Developers</NavLink>
        </nav>
        <button
          className="theme"
          aria-label="Toggle colour theme"
          onClick={() => setDark(!dark)}
        >
          {dark ? <Sun size={19} /> : <Moon size={19} />}
        </button>
      </header>
      <main id="main" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<Check meta={meta} />} />
          <Route path="/demo" element={<RemotePage kind="demo" />} />
          <Route path="/benchmark" element={<RemotePage kind="benchmark" />} />
          {["how-it-works", "developers", "limits"].map((p) => (
            <Route path={"/" + p} key={p} element={<Info page={p} />} />
          ))}
          <Route path="*" element={<Info page="404" />} />
        </Routes>
      </main>
      <footer>
        <p>
          Answers change. <strong>Keep asking.</strong>
        </p>
        <div className="row wrap">
          <Link to="/limits">Limits & privacy</Link>
          <a href="https://github.com/hannielvinu/StillTrue">GitHub ↗</a>
        </div>
        <small>Built for the Global AI Hackathon with Bifrost and Tavily</small>
      </footer>
    </>
  );
}
const Router = offlineDemo ? HashRouter : BrowserRouter;
export default function App() {
  return (
    <Router>
      <Shell />
    </Router>
  );
}
