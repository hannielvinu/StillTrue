import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("--limit", type=int)
args = parser.parse_args()
text = Path(args.file).read_text().strip()
print(f"{len(text)} characters")
if args.limit and len(text) > args.limit:
    raise SystemExit("Exceeds limit")
