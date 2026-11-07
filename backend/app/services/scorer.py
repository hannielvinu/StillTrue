def summarize(results):
    counts = {
        v: sum(r["verdict"] == v for r in results) for v in ["CURRENT", "CHANGED", "UNCONFIRMED"]
    }
    verified = [r for r in results if r["score"] is not None]
    weights = {"high": 3, "medium": 2, "low": 1}
    total = sum(weights[r["claim"]["volatility"]] for r in verified)
    return {
        "still_true": counts["CURRENT"],
        "needs_attention": counts["CHANGED"],
        "unconfirmed": counts["UNCONFIRMED"],
        "verified": len(verified),
        "total": len(results),
        "freshness": round(
            sum(r["score"] * weights[r["claim"]["volatility"]] for r in verified) / total
        )
        if total
        else None,
    }
