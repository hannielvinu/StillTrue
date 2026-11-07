import hashlib
import json
import time
from pathlib import Path
import aiosqlite


class Store:
    def __init__(self, path: str):
        self.path = path

    async def connect(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        db = await aiosqlite.connect(self.path)
        await db.execute(
            "CREATE TABLE IF NOT EXISTS evidence (key TEXT PRIMARY KEY, created REAL, data TEXT)"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS budget (day TEXT PRIMARY KEY, credits REAL)")
        await db.commit()
        return db

    @staticmethod
    def key(pack, claim):
        return hashlib.sha256(
            f"{pack}|{claim.subject_key}|{claim.attribute_key}".encode()
        ).hexdigest()

    async def get(self, key: str, ttl_h: float):
        db = await self.connect()
        try:
            async with db.execute("SELECT created, data FROM evidence WHERE key=?", (key,)) as cur:
                row = await cur.fetchone()
            return json.loads(row[1]) if row and time.time() - row[0] < ttl_h * 3600 else None
        finally:
            await db.close()

    async def put(self, key: str, data):
        db = await self.connect()
        try:
            await db.execute(
                "INSERT OR REPLACE INTO evidence VALUES (?, ?, ?)",
                (key, time.time(), json.dumps(data)),
            )
            await db.commit()
        finally:
            await db.close()

    async def reserve(self, day: str, amount: float, cap: float):
        db = await self.connect()
        try:
            await db.execute("BEGIN IMMEDIATE")
            async with db.execute("SELECT credits FROM budget WHERE day=?", (day,)) as cur:
                row = await cur.fetchone()
            spent = row[0] if row else 0
            if spent + amount > cap:
                raise BudgetExhausted("Daily retrieval budget exhausted")
            await db.execute("INSERT OR REPLACE INTO budget VALUES (?, ?)", (day, spent + amount))
            await db.commit()
        finally:
            await db.close()


class BudgetExhausted(Exception):
    pass
