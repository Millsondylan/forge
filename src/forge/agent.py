from __future__ import annotations
import asyncio
import logging
from typing import Any
from pathlib import Path
from .providers import BaseProvider


class Agent:
    def __init__(self, id: int, provider: BaseProvider, system_prompt: str | None = None):
        self.id = id
        self.provider = provider
        self.prompt = system_prompt or ""
        self.state = "idle"
        self._logger = logging.getLogger(f"agent-{self.id}")
        # File logger per agent
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir / f"agent_{self.id}.log")
        fh.setFormatter(logging.Formatter("%(asctime)s [agent-%(name)s] %(levelname)s: %(message)s"))
        self._logger.setLevel(logging.INFO)
        if not any(isinstance(h, logging.FileHandler) for h in self._logger.handlers):
            self._logger.addHandler(fh)

    async def run_task(self, task_payload: str) -> dict[str, Any]:
        self._logger.info("starting task")
        try:
            self.state = "running"
            result_text = await self._execute(task_payload)
            await self._verify(task_payload, result_text)
            self.state = "idle"
            self._logger.info("task complete")
            return {"agent": self.id, "output": result_text}
        except Exception as e:
            self._logger.exception("task failed: %s", e)
            await self._recover(e)
            self.state = "idle"
            raise

    async def _execute(self, task_payload: str) -> str:
        # Single-call generate; retries should be handled by caller/queue runner if needed
        return await self.provider.generate(self.prompt, task_payload)

    async def _verify(self, task_payload: str, output: str) -> None:
        # Logical verification: non-empty output
        if not isinstance(output, str) or not output.strip():
            raise ValueError("empty output from provider")
        await asyncio.sleep(0)

    async def _recover(self, e: Exception) -> None:
        # Recovery hook; could implement backoff per task in runner
        await asyncio.sleep(0)
        return None
