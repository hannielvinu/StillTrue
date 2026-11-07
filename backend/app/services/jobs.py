import asyncio
import time
from dataclasses import dataclass, field
from uuid import uuid4
from .pipeline import run


@dataclass
class Job:
    id: str = field(default_factory=lambda: uuid4().hex)
    created: float = field(default_factory=time.monotonic)
    events: list = field(default_factory=list)
    result: dict | None = None
    done: bool = False
    task: asyncio.Task | None = None

    async def emit(self, event, data):
        self.events.append((event, data))


jobs: dict[str, Job] = {}


async def execute(job, data, settings):
    try:
        job.result = await run(data, settings, job.emit)
    except asyncio.CancelledError:
        await job.emit("error", {"code": "cancelled", "message": "Check cancelled"})
    except Exception:
        await job.emit(
            "error",
            {
                "code": "pipeline_error",
                "message": "Check failed. Confirm gateway, model IDs and API keys, then retry.",
            },
        )
    finally:
        job.done = True


def create(data, settings):
    for key, old in list(jobs.items()):
        if time.monotonic() - old.created > 1800:
            if old.task and not old.done:
                old.task.cancel()
            del jobs[key]
    job = Job()
    jobs[job.id] = job
    job.task = asyncio.create_task(execute(job, data, settings))
    return job
