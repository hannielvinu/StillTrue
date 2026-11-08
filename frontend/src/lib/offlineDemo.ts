import type { Pack, Run } from "../types";
export const offlineDemo = import.meta.env.VITE_OFFLINE_DEMO === "true";
export const offlinePacks: Pack[] = [
  ["india_tax", "Indian tax"],
  ["uk_personal_finance", "UK personal finance"],
  ["travel_visa", "Travel and visas"],
  ["developer_apis", "Developer APIs"],
  ["general", "General"],
].map(([id, name]) => ({
  id,
  name,
  description: "Offline UI demonstration. No live sources are checked.",
  tier1_domains: [],
}));

export function offlineRun(text: string): Run {
  if (!text.trim() || text.length > 6000)
    throw new Error("Enter 1–6000 characters.");
  const redacted = text
    .replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g, "[EMAIL]")
    .replace(/\b[A-Z]{5}\d{4}[A-Z]\b/g, "[PAN]")
    .replace(/(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)/g, "[PHONE]");
  const claims = redacted
    .split(/(?<=[.!?])\s+/)
    .filter(Boolean)
    .slice(0, 8)
    .map((span, index) => ({
      claim: {
        id: `claim-${index + 1}`,
        text: span,
        asserted_value: "Not assessed offline",
        volatility: "medium" as const,
      },
      verdict: "UNCONFIRMED" as const,
      score: null,
      reason: "offline_demo_no_live_sources",
      models_agree: null,
      evidence: [],
      cache_hit: false,
      query: "No search performed in offline mode",
      latency_ms: 0,
      mock: true,
    }));
  return {
    mock: true,
    mode: "offline",
    claims,
    correction: null,
    checked_at: new Date().toISOString(),
    summary: {
      still_true: 0,
      needs_attention: 0,
      unconfirmed: claims.length,
      verified: 0,
      total: claims.length,
      freshness: null,
    },
    metadata: {
      execution:
        "Browser-only UI simulation; sentence splitting is not LLM extraction",
      external_calls: 0,
      models: [],
      tavily_credits: 0,
      credits_estimated: false,
      benchmark_eligible: false,
    },
  };
}
