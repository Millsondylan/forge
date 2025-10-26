from __future__ import annotations
import asyncio
import os
import shutil
from typing import Optional

# Anthropic
from anthropic import AsyncAnthropic


class BaseProvider:
    name: str

    async def generate(self, system_prompt: str, user_prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError


class EchoProvider(BaseProvider):
    name = "debug-echo"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return f"[ECHO]\nSYSTEM:\n{system_prompt}\nUSER:\n{user_prompt}"


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, model: str):
        self.model = model
        self.client: Optional[AsyncAnthropic] = None

    async def _ensure_client(self) -> None:
        if self.client is not None:
            return
        try:
            # Newer SDKs may discover credentials from `anthropic login` automatically
            self.client = AsyncAnthropic()
            return
        except Exception:
            pass
        # If not configured, try launching interactive login via Anthropic CLI
        anth = shutil.which("anthropic")
        if not anth:
            raise RuntimeError(
                "Anthropic CLI not found. Install with `pip install anthropic` and run `forge auth anthropic`."
            )
        proc = await asyncio.create_subprocess_exec(anth, "login")
        await proc.wait()
        # Retry client creation
        self.client = AsyncAnthropic()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        await self._ensure_client()
        assert self.client is not None
        msg = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join([block.text for block in msg.content if getattr(block, "type", None) == "text"]) or ""
