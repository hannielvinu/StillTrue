export type Verdict = "CURRENT" | "CHANGED" | "UNCONFIRMED";
export interface Claim {
  id: string;
  text: string;
  asserted_value: string;
  volatility: "high" | "medium" | "low";
}
export interface Evidence {
  url: string;
  domain: string;
  tier: number;
  text: string;
  retrieved_at: string;
  page_date_hint: string | null;
}
export interface Result {
  claim: Claim;
  verdict: Verdict;
  score: number | null;
  reason: string | null;
  current_value?: string;
  evidence_quote?: string;
  source_url?: string;
  effective_from?: string;
  change_summary?: string;
  models_agree: boolean | null;
  evidence: Evidence[];
  cache_hit: boolean;
  query: string;
  latency_ms: number;
  mock: boolean;
}
export interface Correction {
  text: string;
  edits: { before: string; after: string; url: string }[];
}
export interface Run {
  mock: boolean;
  mode: string;
  claims: Result[];
  summary: {
    still_true: number;
    needs_attention: number;
    unconfirmed: number;
    verified: number;
    total: number;
    freshness: number | null;
  };
  correction: Correction | null;
  checked_at: string;
  metadata: Record<string, unknown>;
}
export interface Pack {
  id: string;
  name: string;
  description: string;
  tier1_domains: string[];
}
export interface Meta {
  mock: boolean;
  mode: string;
  max_input_chars: number;
}
