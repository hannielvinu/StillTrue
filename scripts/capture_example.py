import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.clients.bifrost import Bifrost
from app.config import Settings


async def main():
    parser = argparse.ArgumentParser(description="Capture a real model response via Bifrost")
    parser.add_argument("question")
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    settings = Settings()
    if settings.mock_mode:
        raise SystemExit("Capture refuses MOCK_MODE=true")
    answer = await Bifrost(settings).chat(args.model, [{"role": "user", "content": args.question}])
    now = datetime.now(timezone.utc)
    path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / f"captured_{now.strftime('%Y%m%dT%H%M%S')}.json"
    )
    path.write_text(
        json.dumps(
            {
                "model": args.model,
                "date": now.isoformat(),
                "question": args.question,
                "raw_answer": answer,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(path)


if __name__ == "__main__":
    asyncio.run(main())
