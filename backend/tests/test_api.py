import httpx
import pytest
from app.main import app, settings


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "mock_mode", True)


async def test_job_lifecycle(mock_settings):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.post("/api/v1/verify", json={"text": "The allowance is 100 units."})
        assert r.status_code == 202
        job = r.json()["job_id"]
        events = await c.get(f"/api/v1/verify/{job}/events")
        assert "event: run_complete" in events.text
        assert events.text.index("event: pii_report") < events.text.index("event: claim_result")
        poll = (await c.get(f"/api/v1/verify/{job}")).json()
        assert poll["result"]["mock"] is True
        resume = await c.get(f"/api/v1/verify/{job}/events", headers={"last-event-id": "999"})
        assert resume.text == ""
        assert (await c.get("/api/v1/verify/missing")).status_code == 404
        assert (await c.post("/api/v1/verify", json={"text": "  "})).status_code == 422
        assert (
            await c.post("/api/v1/verify", json={"text": "x", "pack": "missing"})
        ).status_code == 422
        assert (await c.post("/api/v1/verify", content="x" * 100001)).status_code == 413


async def test_metadata_and_chat(mock_settings):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        assert (await c.get("/api/v1/meta")).json()["mock"]
        assert len((await c.get("/api/v1/packs")).json()) == 5
        r = await c.post(
            "/api/v1/chat/verified",
            json={"messages": [{"role": "user", "content": "hello"}], "model": "test/model"},
        )
        assert r.json()["freshness"]["mock"]
