import { CheckCircle, AlertTriangle, HelpCircle } from "lucide-react";
import type { Result, Run, Correction } from "../types";
import { safeUrl } from "../lib/api";
export const labels = {
  CURRENT: "Still true",
  CHANGED: "Changed",
  UNCONFIRMED: "Couldn’t confirm",
};
export function PiiNotice({ count }: { count: number }) {
  return count > 0 ? (
    <p role="status" className="notice">
      We found {count} personal details and masked them before checking.
    </p>
  ) : null;
}
export function ClaimCard({ result: r }: { result: Result }) {
  const Icon =
    r.verdict === "CURRENT"
      ? CheckCircle
      : r.verdict === "CHANGED"
        ? AlertTriangle
        : HelpCircle;
  return (
    <article className="claim" id={r.claim.id}>
      <div className="row spread">
        <span className={"status " + r.verdict}>
          <Icon size={16} />
          {labels[r.verdict]}
        </span>
        <span className="mono">
          {r.score ?? "—"}
          <small> / 100</small>
        </span>
      </div>
      <h3>{r.claim.text}</h3>
      {r.reason && <p className="muted">{r.reason.replaceAll("_", " ")}</p>}
      {r.verdict === "CHANGED" && (
        <p className="change">
          <del>{r.claim.asserted_value}</del> →{" "}
          <strong>{r.current_value}</strong>
        </p>
      )}
      {r.change_summary && <p>{r.change_summary}</p>}
      {r.effective_from && <p>Effective: {r.effective_from}</p>}
      {r.evidence_quote && <blockquote>{r.evidence_quote}</blockquote>}
      {r.evidence.map((e) => (
        <p className="source" key={e.url}>
          <a href={safeUrl(e.url)} target="_blank" rel="noopener noreferrer">
            {e.domain} ↗
          </a>{" "}
          ·{" "}
          {e.tier === 1
            ? "Official"
            : e.tier === 2
              ? "Reputable"
              : "Unofficial"}
          <br />
          <small>
            Sources checked {new Date(e.retrieved_at).toLocaleString()}
            {e.page_date_hint ? ` · Page date hint: ${e.page_date_hint}` : ""}
          </small>
        </p>
      ))}
      <details>
        <summary>How we checked</summary>
        <p>{r.query || "Synthetic offline fixture"}</p>
        <p>
          Model agreement:{" "}
          {r.models_agree === null ? "single-model" : String(r.models_agree)} ·{" "}
          {r.cache_hit ? "cached evidence" : "fresh retrieval"} · {r.latency_ms}{" "}
          ms
        </p>
      </details>
    </article>
  );
}
export function Summary({ run }: { run: Run }) {
  const s = run.summary;
  return (
    <section className="summary">
      <span className="eyebrow">THE FRESHNESS REPORT</span>
      <h2>
        {s.still_true} of {s.verified} checked claims are still true
      </h2>
      <p>
        {s.needs_attention} changed · {s.unconfirmed} couldn’t be confirmed
      </p>
      <label>
        Freshness (heuristic):{" "}
        <strong>
          {s.freshness ?? "—"}
          {s.freshness !== null ? "%" : ""}
        </strong>
      </label>
      <progress max="100" value={s.freshness ?? 0} />
      <p className="badge">
        {run.mode === "single"
          ? "Single-model check (add a second provider for cross-model verification)"
          : "Cross-model check (2 models)"}
      </p>
      <small>Checked {new Date(run.checked_at).toLocaleString()}</small>
    </section>
  );
}
export function Diff({ correction }: { correction: Correction }) {
  return (
    <section className="panel">
      <h2>Corrected answer</h2>
      {correction.edits.map((e, i) => (
        <p key={i}>
          <del>{e.before}</del>
          <br />
          <ins>{e.after}</ins>
        </p>
      ))}
      <button onClick={() => navigator.clipboard.writeText(correction.text)}>
        Copy corrected answer
      </button>
    </section>
  );
}
