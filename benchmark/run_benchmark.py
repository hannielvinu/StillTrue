import asyncio
import os
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import Settings
from app.clients.bifrost import Bifrost
from app.schemas import VerifyInput
from app.services.pipeline import run
from baseline import baseline


def metrics(rows, key):
    n = len(rows)
    stale = [r for r in rows if r["expected"] == "CHANGED"]
    latencies = sorted(
        r["baseline_latency_ms" if key == "baseline" else "latency_ms"] for r in rows
    )
    return {
        "n": n,
        "accuracy": sum(r[key] == r["expected"] for r in rows) / n,
        "false_current_rate": sum(r[key] == "CURRENT" for r in stale) / len(stale)
        if stale
        else None,
        "missed_change_rate": sum(r[key] != "CHANGED" for r in stale) / len(stale)
        if stale
        else None,
        "unconfirmed_rate": sum(r[key] == "UNCONFIRMED" for r in rows) / n,
        "latency_p50_ms": statistics.median(latencies),
        "latency_p95_ms": latencies[max(0, __import__("math").ceil(0.95 * n) - 1)],
    }


async def main():
    settings = Settings()
    if settings.mock_mode:
        raise SystemExit("Benchmarks refuse MOCK_MODE=true")
    if not settings.tavily_api_key or not settings.extractor_model or not settings.models:
        raise SystemExit("Configure real Tavily credentials and Bifrost models before benchmarking")
    source = [
        json.loads(line)
        for line in (ROOT / "benchmark/claims.jsonl").read_text().splitlines()
        if line.strip()
    ]
    rows = []

    async def ignore(*args):
        pass

    client = Bifrost(settings)
    # Reuse the no-retrieval baseline answers from an earlier run (saves free-tier tokens).
    reuse = {}
    if os.getenv("BASELINE_FROM"):
        for r in json.loads(Path(os.environ["BASELINE_FROM"]).read_text())["rows"]:
            reuse[r["id"]] = (r["baseline"], r["baseline_latency_ms"])
    for row in source:
        if row["label_status"] not in ("human_verified", "source_verified"):
            continue
        started = time.monotonic()
        result = await run(
            VerifyInput(text=row["claim_text"], pack=row["pack"]), settings, ignore, rewrite=False
        )
        # A provider failure is recorded as a failed row (never retried silently, never dropped).
        failed = not result["claims"] or result["claims"][0].get("reason") == "error"
        verdict = "UNCONFIRMED" if failed else result["claims"][0]["verdict"]
        pipeline_ms = round((time.monotonic() - started) * 1000)
        baseline_started = time.monotonic()
        # Baseline = the strongest configured model answering alone, with no retrieval.
        if row["id"] in reuse:
            plain, reused_ms = reuse[row["id"]]
        else:
            plain = await baseline(client, settings.verifier_model_a, row["claim_text"])
            reused_ms = None
        rows.append(
            {
                "id": row["id"],
                "expected": row["expected"].replace("UNCONFIRMED_EXPECTED", "UNCONFIRMED"),
                "verdict": verdict,
                "baseline": plain,
                "latency_ms": pipeline_ms,
                "baseline_latency_ms": reused_ms
                if reused_ms is not None
                else round((time.monotonic() - baseline_started) * 1000),
                "credits": result["metadata"]["tavily_credits"],
                "cache_hits": result["metadata"]["cache_hits"],
                "claim_count": len(result["claims"]),
                "failed": failed,
                "current_value": None if failed else result["claims"][0].get("current_value"),
                "source_url": None if failed else result["claims"][0].get("source_url"),
                "reason": None if failed else result["claims"][0].get("reason"),
                "judgments": None if failed else result["claims"][0].get("judgments"),
                "ground_truth_value": row.get("ground_truth_value"),
                "ground_truth_source_url": row.get("ground_truth_source_url"),
            }
        )
        # Checkpoint after every row so a crash never wastes credits already spent.
        (ROOT / "benchmark/results").mkdir(exist_ok=True)
        (ROOT / "benchmark/results/partial.json").write_text(json.dumps(rows, indent=2))
        print(row["id"], row["expected"], "->", verdict, "| baseline:", plain, flush=True)
    if not rows:
        raise SystemExit("No verified rows")
    label = f"SMALL SAMPLE (n={len(rows)})" if len(rows) < 20 else f"n={len(rows)}"
    print(label)
    now = datetime.now(timezone.utc)
    report = {
        "date": now.isoformat(),
        "sample_label": label,
        "models": settings.models,
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "stilltrue": metrics(rows, "verdict"),
        "baseline": metrics(rows, "baseline"),
        "mean_estimated_credits_per_claim": sum(r["credits"] for r in rows)
        / sum(r["claim_count"] for r in rows),
        "cache_hit_rate": sum(r["cache_hits"] for r in rows) / sum(r["claim_count"] for r in rows),
        "rows": rows,
    }
    dest = ROOT / "benchmark/results" / f"{now.strftime('%Y%m%dT%H%M%S')}.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(report, indent=2))
    public = ROOT / "frontend/public/benchmark/latest.json"
    public.parent.mkdir(parents=True, exist_ok=True)
    public.write_text(dest.read_text())
    print(dest)


if __name__ == "__main__":
    asyncio.run(main())
