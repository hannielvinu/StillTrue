import { describe, it, expect } from "vitest";
import { offlineRun } from "./offlineDemo";
describe("key-free offline demo", () => {
  it("never claims truth or creates official evidence without retrieval", () => {
    const run = offlineRun(
      "The allowance is 100 units. The deadline is tomorrow.",
    );
    expect(run.mock).toBe(true);
    expect(run.claims).toHaveLength(2);
    expect(run.summary.verified).toBe(0);
    expect(run.summary.freshness).toBeNull();
    expect(
      run.claims.every(
        (c) => c.verdict === "UNCONFIRMED" && c.evidence.length === 0,
      ),
    ).toBe(true);
    expect(run.metadata.external_calls).toBe(0);
    expect(run.metadata.benchmark_eligible).toBe(false);
  });
  it("masks common identifiers locally", () => {
    expect(
      JSON.stringify(offlineRun("Contact a@b.com ABCDE1234F +91 9876543210")),
    ).not.toContain("a@b.com");
  });
  it("enforces input limits", () => {
    expect(() => offlineRun("  ")).toThrow();
    expect(() => offlineRun("x".repeat(6001))).toThrow();
  });
});
