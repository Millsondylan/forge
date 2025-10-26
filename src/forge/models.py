from __future__ import annotations
from typing import Tuple
from .providers import (
    BaseProvider,
    EchoProvider,
    AnthropicProvider,
)


def make_provider(model: str) -> Tuple[str, BaseProvider]:
    m = model.lower()
    if m.startswith("debug-echo") or m == "echo":
        return "debug-echo", EchoProvider()
    # Default: Anthropic/Claude
    return model, AnthropicProvider(model)
