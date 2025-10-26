from __future__ import annotations
from typing import Optional
from anthropic import AsyncAnthropic


def get_async_client() -> AsyncAnthropic:
    # Rely on SDK's default credential discovery (e.g., via `anthropic login`).
    return AsyncAnthropic()
