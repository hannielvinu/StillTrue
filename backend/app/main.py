import asyncio
import os
import json
import time
from pathlib import Path
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from pydantic import BaseModel, Field
from .config import get_settings
from .schemas import VerifyInput
from .services import jobs
from .services.pipeline import run
from .services.trust import packs
from .services.pii import scan
from .clients.bifrost import Bifrost

settings = get_settings()
app = FastAPI(title="StillTrue", version="0.1.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Last-Event-ID"],
)


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(
        {"error": {"code": str(exc.status_code), "message": str(exc.detail)}},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        {
            "error": {
                "code": "validation_error",
                "message": "Invalid request. Check required fields and input limits.",
            }
        },
        status_code=422,
    )


@app.exception_handler(RateLimitExceeded)
async def rate_error(request, exc):
    return JSONResponse(
        {"error": {"code": "rate_limited", "message": "Too many checks. Please wait a minute."}},
        status_code=429,
    )


@app.middleware("http")
async def size_limit(request, call_next):
    if request.method in ("POST", "PUT"):
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > 100000):
            return JSONResponse(
                {"error": {"code": "too_large", "message": "Request too large"}}, status_code=413
            )
        body = await request.body()
        if len(body) > 100000:
            return JSONResponse(
                {"error": {"code": "too_large", "message": "Request too large"}}, status_code=413
            )
    return await call_next(request)


@app.get("/api/v1/meta")
async def meta():
    return {
        "version": "0.1.0",
        "mock": settings.mock_mode,
        "mode": settings.mode,
        "models": list({m.split("/")[0] for m in settings.models}),
        "max_input_chars": settings.max_input_chars,
    }


@app.get("/api/v1/packs")
async def list_packs():
    return [{"id": k, **v} for k, v in packs().items()]


@app.get("/api/v1/health")
async def health():
    reachable = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(settings.bifrost_base_url.rstrip("/") + "/health")
            reachable = response.is_success
    except httpx.HTTPError:
        pass
    return {
        "app": "ok",
        "bifrost_reachable": reachable,
        "tavily_key_present": bool(settings.tavily_api_key),
        "mock": settings.mock_mode,
        "live_ready": reachable
        and bool(settings.tavily_api_key and settings.extractor_model and settings.models),
    }


def validate(data):
    if not data.text.strip() or len(data.text) > settings.max_input_chars:
        raise HTTPException(422, f"Enter between 1 and {settings.max_input_chars} characters")
    if data.pack not in packs():
        raise HTTPException(422, "Unknown domain pack")


@app.post("/api/v1/verify", status_code=202)
@limiter.limit(settings.rate_limit)
async def verify(request: Request, data: VerifyInput):
    validate(data)
    if sum(not j.done for j in jobs.jobs.values()) >= 50:
        raise HTTPException(503, "Too many active checks; retry shortly")
    job = jobs.create(data, settings)
    return {"job_id": job.id, "mock": settings.mock_mode}


def get_job(job_id):
    job = jobs.jobs.get(job_id)
    if not job or time.monotonic() - job.created > 1800:
        raise HTTPException(404, "Check expired or not found")
    return job


@app.get("/api/v1/verify/{job_id}")
async def poll(job_id: str):
    job = get_job(job_id)
    return {
        "status": "complete" if job.done else "running",
        "result": job.result,
        "mock": settings.mock_mode,
        "error": next((d for e, d in job.events if e == "error"), None),
    }


@app.delete("/api/v1/verify/{job_id}")
async def cancel(job_id: str):
    job = get_job(job_id)
    if job.task and not job.done:
        job.task.cancel()
    return {"cancelled": True, "mock": settings.mock_mode}


@app.get("/api/v1/verify/{job_id}/events")
async def events(request: Request, job_id: str):
    job = get_job(job_id)
    try:
        cursor = max(0, int(request.headers.get("last-event-id", "0")))
    except ValueError:
        raise HTTPException(400, "Invalid event cursor")

    async def stream():
        nonlocal cursor
        last = time.monotonic()
        while True:
            while cursor < len(job.events):
                event, data = job.events[cursor]
                cursor += 1
                yield f"id: {cursor}\nevent: {event}\ndata: {json.dumps(data)}\n\n"
                last = time.monotonic()
            if job.done or await request.is_disconnected():
                return
            if time.monotonic() - last >= 15:
                yield ": keepalive\n\n"
                last = time.monotonic()
            await asyncio.sleep(0.1)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class ChatInput(BaseModel):
    messages: list[dict[str, str]] = Field(min_length=1, max_length=30)
    model: str = Field(min_length=3, max_length=200)
    pack: str = "general"


@app.post("/api/v1/chat/verified")
@limiter.limit(settings.rate_limit)
async def chat(request: Request, data: ChatInput):
    if settings.mock_mode:
        answer = "Illustrative mock answer: the allowance is 100 units."
    else:
        messages = [
            {"role": m.get("role", "user"), "content": scan(m.get("content", ""))[0]}
            for m in data.messages
        ]
        if sum(len(m["content"]) for m in messages) > settings.max_input_chars:
            raise HTTPException(422, "Conversation too long")
        try:
            answer = await Bifrost(settings).chat(data.model, messages)
        except Exception:
            raise HTTPException(502, "Gateway request failed; check configuration")
    inp = VerifyInput(text=answer, pack=data.pack)
    validate(inp)

    async def ignore(*args):
        pass

    try:
        result = await run(inp, settings, ignore)
    except Exception:
        raise HTTPException(502, "Verification failed; check configuration")
    return {"answer": answer, "freshness": result, "mock": settings.mock_mode}


DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
# Container layout can supply FRONTEND_DIST explicitly.
DIST = Path(os.getenv("FRONTEND_DIST", str(DIST)))


@app.get("/{path:path}", include_in_schema=False)
async def frontend(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "Not found")
    candidate = (DIST / path).resolve()
    if candidate.is_relative_to(DIST.resolve()) and candidate.is_file():
        return FileResponse(candidate)
    if path.startswith("benchmark/"):
        raise HTTPException(404, "Not yet run")
    if (DIST / "index.html").exists():
        return FileResponse(DIST / "index.html")
    raise HTTPException(404, "Build the frontend with npm run build")
