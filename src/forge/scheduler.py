from __future__ import annotations
import asyncio
import datetime as dt
from typing import Awaitable, Callable
from . import storage


async def schedule_task(task_fn: Callable[[], Awaitable[object]], run_at: dt.datetime):
    delay = (run_at - dt.datetime.now()).total_seconds()
    await asyncio.sleep(max(0, delay))
    return await task_fn()


async def run_scheduler(poll_interval: float = 1.0) -> None:
    await storage.init_db()
    while True:
        now_iso = dt.datetime.utcnow().isoformat()
        for sched_id, task in await storage.due_schedules(now_iso):
            await storage.enqueue_task(task)
            await storage.mark_schedule_done(sched_id)
        await asyncio.sleep(poll_interval)
