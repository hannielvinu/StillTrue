import asyncio
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
    for row in source:
        if row["label_status"] != "human_verified":
            continue
        started = time.monotonic()
        result = await run(VerifyInput(text=row["claim_text"], pack=row["pack"]), settings, ignore)
        if not result["claims"] or any(r.get("reason") == "error" for r in result["claims"]):
            raise SystemExit(
                "Benchmark aborted: extraction or provider failure; no report generated"
            )
        verdict = result["claims"][0]["verdict"]
        pipeline_ms = round((time.monotonic() - started) * 1000)
        baseline_started = time.monotonic()
        plain = await baseline(client, settings.extractor_model, row["claim_text"])
        rows.append(
            {
                "id": row["id"],
                "expected": row["expected"].replace("UNCONFIRMED_EXPECTED", "UNCONFIRMED"),
                "verdict": verdict,
                "baseline": plain,
                "latency_ms": pipeline_ms,
                "baseline_latency_ms": round((time.monotonic() - baseline_started) * 1000),
                "credits": result["metadata"]["tavily_credits"],
                "cache_hits": result["metadata"]["cache_hits"],
                "claim_count": len(result["claims"]),
            }
        )
    if not rows:
        raise SystemExit("No human-verified rows")
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
