import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import Settings
from app.schemas import VerifyInput
from app.services.pipeline import run


async def main():
    settings = Settings()
    if settings.mock_mode:
        raise SystemExit("Recording refuses MOCK_MODE=true")
    if len(sys.argv) < 2:
        raise SystemExit("Usage: make record-demo CAPTURE=../examples/captured_....json")
    capture = json.loads(Path(sys.argv[1]).read_text())
    events = []

    async def emit(event, data):
        events.append({"event": event, "data": data})

    result = await run(
        VerifyInput(text=capture["raw_answer"], question=capture["question"], pack="india_tax"),
        settings,
        emit,
    )
    path = Path(__file__).resolve().parents[1] / "frontend/public/demo/recorded-run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "date": datetime.now(timezone.utc).isoformat(),
                "capture": capture,
                "models": result["metadata"]["models"],
                "run": result,
                "events": events,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(path)


if __name__ == "__main__":
    asyncio.run(main())
