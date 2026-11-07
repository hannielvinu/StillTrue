import { render, screen, cleanup } from "@testing-library/react";
import { afterEach, describe, it, expect } from "vitest";
import { ClaimCard, Summary, Diff, PiiNotice } from "./Results";
import type { Result, Run } from "../types";
afterEach(cleanup);
const base: Result = {
  claim: {
    id: "a",
    text: "An actionable claim",
    asserted_value: "100",
    volatility: "high",
  },
  verdict: "UNCONFIRMED",
  score: null,
  reason: "no_official_source",
  models_agree: null,
  evidence: [],
  cache_hit: false,
  query: "allowance",
  latency_ms: 10,
  mock: false,
};
describe("evidence report", () => {
  it.each([
    ["CURRENT", "Still true"],
    ["CHANGED", "Changed"],
    ["UNCONFIRMED", "Couldn’t confirm"],
  ] as const)("renders %s with a text label", (verdict, label) => {
    render(<ClaimCard result={{ ...base, verdict }} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });
  it("explains PII masking", () => {
    render(<PiiNotice count={2} />);
    expect(screen.getByRole("status")).toHaveTextContent("2 personal details");
  });
  it("shows before and after without hiding the original", () => {
    render(
      <Diff
        correction={{
          text: "New",
          edits: [{ before: "Old", after: "New", url: "https://example.com" }],
        }}
      />,
    );
    expect(screen.getByText("Old").tagName).toBe("DEL");
    expect(screen.getByText("New").tagName).toBe("INS");
  });
  it("does not invent a summary score", () => {
    render(
      <Summary
        run={
          {
            summary: {
              still_true: 0,
              verified: 0,
              total: 1,
              needs_attention: 0,
              unconfirmed: 1,
              freshness: null,
            },
            mode: "single",
            checked_at: "2026-11-08",
          } as Run
        }
      />,
    );
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
