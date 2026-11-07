import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = sorted((root / "benchmark/results").glob("*.json"))
if not files:
    raise SystemExit("No real benchmark results; README unchanged")
r = json.loads(files[-1].read_text())
text = f"{r['sample_label']} · {r['date']}\n\n| Metric | StillTrue | Baseline |\n|---|---:|---:|\n"
for key in ["accuracy", "false_current_rate", "missed_change_rate", "unconfirmed_rate"]:
    text += f"| {key} | {r['stilltrue'][key]} | {r['baseline'][key]} |\n"
p = root / "README.md"
p.write_text(
    re.sub(
        r"<!-- benchmark:start -->.*?<!-- benchmark:end -->",
        "<!-- benchmark:start -->\n" + text + "<!-- benchmark:end -->",
        p.read_text(),
        flags=re.S,
    )
)
