from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict
import yaml

CONFIG_PATH = Path(os.getenv("FORGE_CONFIG", "config.yaml")).resolve()

DEFAULT_CONFIG: Dict[str, Any] = {
    "model": "claude-3.5-sonnet",
    "providers": {
        "anthropic": "login",  # managed via `anthropic login`
    },
    "concurrency_limit": 500,
    "retry_policy": {"max_retries": 3, "delay_seconds": 2},
}


def ensure_config() -> None:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))


def load_config() -> Dict[str, Any]:
    ensure_config()
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}


def save_config(cfg: Dict[str, Any]) -> None:
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def set_model(model: str) -> None:
    cfg = load_config()
    cfg["model"] = model
    save_config(cfg)


def get_model() -> str:
    return load_config().get("model", DEFAULT_CONFIG["model"])


def available_models() -> list[str]:
    cfg = load_config()
    return list(cfg.get("available_models", ["claude-3.5-sonnet"]))
