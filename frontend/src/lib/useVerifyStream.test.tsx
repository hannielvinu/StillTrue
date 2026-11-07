import { act, renderHook, waitFor } from "@testing-library/react";
import { it, expect, vi } from "vitest";
import { useVerifyStream } from "./useVerifyStream";
it("deduplicates replayed events and cancels on the server", async () => {
  let es: FakeSource;
  class FakeSource {
    listeners: Record<string, ((e: any) => void)[]> = {};
    close = vi.fn();
    constructor() {
      es = this;
    }
    addEventListener(n: string, f: (e: any) => void) {
      (this.listeners[n] ??= []).push(f);
    }
    send(n: string, id: number, data: unknown) {
      this.listeners[n]?.forEach((f) =>
        f({ lastEventId: String(id), data: JSON.stringify(data) }),
      );
    }
  }
  vi.stubGlobal("EventSource", FakeSource);
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ job_id: "test" }) }),
  );
  const { result, unmount } = renderHook(() => useVerifyStream());
  await act(async () => {
    await result.current.start({
      text: "a",
      question: "",
      pack: "general",
      redact: true,
    });
  });
  act(() => {
    es.send("claim_result", 1, { claim: { id: "a" } });
    es.send("claim_result", 1, { claim: { id: "a" } });
  });
  expect(result.current.results).toHaveLength(1);
  await act(async () => {
    await result.current.cancel();
  });
  expect(es!.close).toHaveBeenCalled();
  expect(fetch).toHaveBeenLastCalledWith("/api/v1/verify/test", {
    method: "DELETE",
  });
  unmount();
  vi.unstubAllGlobals();
});
