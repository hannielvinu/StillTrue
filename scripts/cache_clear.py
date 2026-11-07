import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import Settings
from app.cache.store import Store


async def main():
    db = await Store(Settings().cache_path).connect()
    await db.execute("DELETE FROM evidence")
    await db.commit()
    await db.close()
    print("Evidence cache cleared; daily budget preserved")


if __name__ == "__main__":
    asyncio.run(main())
