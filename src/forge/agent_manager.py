from __future__ import annotations
import asyncio
import logging
from typing import Sequence, Optional
from .agent import Agent
from .providers import BaseProvider
from . import storage


class AgentPool:
    def __init__(self, n: int, provider: BaseProvider, system_prompt: str | None = None):
        self.agents: list[Agent] = [Agent(i, provider, system_prompt) for i in range(n)]

    async def run_all(self, tasks: Sequence[str]):
        coros = []
        for a, t in zip(self.agents, tasks):
            coros.append(a.run_task(t))
        return await asyncio.gather(*coros, return_exceptions=True)


async def run_queue(concurrency: int, provider: BaseProvider, retries: int = 0) -> None:
    logger = logging.getLogger("runner")
    # System log file
    from pathlib import Path
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        fh = logging.FileHandler(log_dir / "system.log")
        fh.setFormatter(logging.Formatter("%(asctime)s [runner] %(levelname)s: %(message)s"))
        logger.setLevel(logging.INFO)
        logger.addHandler(fh)
    await storage.init_db()

    async def worker(worker_id: int):
        while True:
            item = await storage.acquire_next_task()
            if not item:
                # No more queued tasks; exit
                return
            task_id, payload = item
            agent = Agent(worker_id, provider)
            attempt = 0
            while True:
                try:
                    await agent.run_task(payload)
                    await storage.complete_task(task_id)
                    break
                except Exception as e:
                    attempt += 1
                    logger.warning("task %s failed (attempt %s/%s): %s", task_id, attempt, retries + 1, e)
                    if attempt > retries:
                        await storage.fail_task(task_id)
                        break
                    await asyncio.sleep(1.0 * attempt)

    tasks = [asyncio.create_task(worker(i)) for i in range(concurrency)]
    await asyncio.gather(*tasks)
