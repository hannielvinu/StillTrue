import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { offlineDemo, offlineRun } from "./offlineDemo";
import type { Claim, Correction, Result, Run } from "../types";
export function useVerifyStream() {
  const [claims, setClaims] = useState<Claim[]>([]),
    [results, setResults] = useState<Result[]>([]),
    [run, setRun] = useState<Run | null>(null),
    [stage, setStage] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [pii, setPii] = useState(0),
    [correction, setCorrection] = useState<Correction | null>(null);
  const source = useRef<EventSource | null>(null),
    job = useRef(""),
    generation = useRef(0);
  useEffect(
    () => () => {
      generation.current++;
      source.current?.close();
    },
    [],
  );
  async function cancel() {
    generation.current++;
    source.current?.close();
    setBusy(false);
    setStage("Cancelled");
    if (job.current)
      await api("/api/v1/verify/" + job.current, { method: "DELETE" }).catch(
        () => {},
      );
  }
  async function start(input: {
    text: string;
    question: string;
    pack: string;
    redact: boolean;
  }) {
    source.current?.close();
    const gen = ++generation.current;
    setBusy(true);
    setError("");
    setClaims([]);
    setResults([]);
    setRun(null);
    setPii(0);
    setCorrection(null);
    setStage("Extracting time-sensitive claims…");
    try {
      if (offlineDemo) {
        const result = offlineRun(input.text);
        setClaims(result.claims.map((r) => r.claim));
        setStage(
          "Offline demonstration: no models or live sources are called.",
        );
        for (const claim of result.claims) {
          await new Promise((resolve) => setTimeout(resolve, 120));
          if (gen !== generation.current) return;
          setResults((old) => [...old, claim]);
        }
        if (gen !== generation.current) return;
        setRun(result);
        setBusy(false);
        setStage(
          "Offline demonstration complete — every claim remains Unconfirmed.",
        );
        return;
      }
      const data = await api<{ job_id: string }>("/api/v1/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      if (gen !== generation.current) return;
      job.current = data.job_id;
      const es = new EventSource("/api/v1/verify/" + data.job_id + "/events");
      source.current = es;
      let last = 0;
      const listen = (name: string, fn: (value: any) => void) =>
        es.addEventListener(name, (raw) => {
          if (gen !== generation.current) return;
          const e = raw as MessageEvent;
          if (Number(e.lastEventId) <= last) return;
          last = Number(e.lastEventId);
          try {
            fn(JSON.parse(e.data));
          } catch {
            setError("Invalid server response");
          }
        });
      listen("pii_report", (d) => setPii(d.masked ? d.count : 0));
      listen("claims_extracted", (d) => {
        setClaims(d.claims);
        setStage(`Found ${d.claims.length} claims, checking sources…`);
      });
      listen("claim_stage", (d) => setStage(`${d.id}: ${d.stage}`));
      listen("claim_result", (d) =>
        setResults((r) => [...r.filter((x) => x.claim.id !== d.claim.id), d]),
      );
      listen("rewrite", setCorrection);
      listen("run_complete", (d) => {
        setRun(d);
        setResults(d.claims);
        setBusy(false);
        setStage("Check complete");
        es.close();
      });
      es.addEventListener("error", (e) => {
        if (gen !== generation.current) return;
        if (e instanceof MessageEvent) {
          try {
            setError(JSON.parse(e.data).message);
          } catch {
            setError("Check failed");
          }
          setBusy(false);
          es.close();
        } else {
          setStage("Connection interrupted. Reconnecting…");
        }
      });
    } catch (e) {
      if (gen === generation.current) {
        setError((e as Error).message);
        setBusy(false);
      }
    }
  }
  return {
    claims,
    results,
    run,
    stage,
    error,
    busy,
    pii,
    correction,
    start,
    cancel,
  };
}
