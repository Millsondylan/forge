from __future__ import annotations
import asyncio
import datetime as dt
import os
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from .config import ensure_config, load_config, set_model, get_model, available_models
from .models import make_provider
from . import storage
from .agent_manager import run_queue
from .scheduler import run_scheduler

LOG_DIR = Path("logs")


def _setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)


@click.group()
def main():
    """Forge CLI control plane."""
    _setup_logging()


@main.command()
def init():
    """Setup environment and initial config and database."""
    ensure_config()
    asyncio.run(storage.init_db())
    click.echo("Initialized config and database.")


@main.group()
def auth():
    """Authenticate model providers (stores keys in system keyring)."""
    pass


@auth.command("anthropic")
def auth_anthropic():
    """Launch Anthropic browser login (OAuth-like flow)."""
    import shutil, subprocess
    anth = shutil.which("anthropic")
    if not anth:
        raise click.ClickException("Anthropic CLI not found. Install with `pip install anthropic`.")
    try:
        subprocess.check_call([anth, "login"])  # opens browser
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"anthropic login failed: {e}")
    click.echo("Anthropic login completed. Credentials cached for SDK use.")


@auth.command("openai")
@click.argument("key")
def auth_openai(key: str):
    keyring.set_password("forge", "openai_api_key", key)
    click.echo("OpenAI API key stored in system keyring.")


@auth.command("gemini")
@click.argument("key")
def auth_gemini(key: str):
    keyring.set_password("forge", "gemini_api_key", key)
    click.echo("Gemini API key stored in system keyring.")


@main.group()
def model():
    """Model operations."""
    pass


@model.command("list")
def model_list():
    import shutil, subprocess
    printed = False
    anth = shutil.which("anthropic")
    if anth:
        try:
            # Try to show available models from Anthropic CLI first
            out = subprocess.check_output([anth, "models", "list"], text=True)
            if out.strip():
                click.echo(out.strip())
                printed = True
        except Exception:
            pass
    # Always include configured models and debug-echo
    mods = available_models()
    extra = "\n".join(mods + ["debug-echo"])
    if printed:
        click.echo("\nConfigured models:")
    click.echo(extra)


@model.command("set")
@click.argument("model")
def model_set_cmd(model: str):
    set_model(model)
    click.echo(f"Default model set to {model}")


@model.command("select")
@click.option("--include-debug", is_flag=True, help="Include debug-echo in menu")
def model_select(include_debug: bool):
    import shutil, subprocess, sys
    # Gather models from Anthropic CLI if available
    names: list[str] = []
    anth = shutil.which("anthropic")
    if anth:
        try:
            out = subprocess.check_output([anth, "models", "list", "--quiet"], text=True)
            for line in out.splitlines():
                name = line.strip()
                if name and not name.startswith("#"):
                    names.append(name)
        except Exception:
            pass
    # Always include configured models
    for m in available_models():
        if m not in names:
            names.append(m)
    if include_debug and "debug-echo" not in names:
        names.append("debug-echo")
    if not names:
        raise click.ClickException("No models found. Try `anthropic login` and `anthropic models list`.")
    click.echo("Select a model:\n")
    for i, m in enumerate(names, 1):
        click.echo(f"  {i}) {m}")
    choice = click.prompt("Enter number", type=int)
    if choice < 1 or choice > len(names):
        raise click.ClickException("Invalid selection")
    chosen = names[choice - 1]
    set_model(chosen)
    click.echo(f"Default model set to {chosen}")


@main.group()
def agent():
    """Agent operations."""
    pass


@agent.command("spawn")
@click.argument("n", type=int)
@click.option("--model", "model_override", default=None, help="Override model")
@click.option("--retries", default=None, type=int, help="Retry attempts per task")
def agent_spawn(n: int, model_override: str | None, retries: int | None):
    cfg = load_config()
    model = model_override or cfg.get("model", get_model())
    model_name, provider = make_provider(model)
    retry_count = retries if retries is not None else int(cfg.get("retry_policy", {}).get("max_retries", 0))
    # Prompt login if using Anthropic
    if model_name != "debug-echo" and hasattr(provider, "_ensure_client"):
        asyncio.run(provider._ensure_client())  # type: ignore[attr-defined]
    click.echo(f"Running queue with concurrency={n} on model={model_name} (retries={retry_count})")
    asyncio.run(run_queue(n, provider, retry_count))


@main.group()
def queue():
    """Queue operations."""
    pass


@queue.command("add")
@click.argument("task")
def queue_add(task: str):
    asyncio.run(storage.init_db())
    task_id = asyncio.run(storage.enqueue_task(task))
    click.echo(f"Queued task id={task_id}")


@queue.command("list")
@click.option("--limit", default=20, type=int)
def queue_list(limit: int):
    asyncio.run(storage.init_db())
    rows = asyncio.run(storage.list_tasks(limit))
    table = Table(title="Tasks")
    for col in ["id", "payload", "status", "created_at", "updated_at"]:
        table.add_column(col)
    for r in rows:
        table.add_row(*[str(x) for x in r])
    Console().print(table)


@queue.command("run")
@click.option("--concurrency", default=None, type=int)
@click.option("--model", "model_override", default=None)
@click.option("--retries", default=None, type=int)
def queue_run(concurrency: int | None, model_override: str | None, retries: int | None):
    cfg = load_config()
    n = concurrency or int(cfg.get("concurrency_limit", 1))
    model = model_override or cfg.get("model", get_model())
    model_name, provider = make_provider(model)
    retry_count = retries if retries is not None else int(cfg.get("retry_policy", {}).get("max_retries", 0))
    # Prompt login if using Anthropic
    if model_name != "debug-echo" and hasattr(provider, "_ensure_client"):
        asyncio.run(provider._ensure_client())  # type: ignore[attr-defined]
    click.echo(f"Running queue with concurrency={n} on model={model_name} (retries={retry_count})")
    asyncio.run(run_queue(n, provider, retry_count))


@main.group()
def schedule():
    """Scheduling operations."""
    pass


@schedule.command("add")
@click.argument("task")
@click.argument("time")
def schedule_add(task: str, time: str):
    # time can be ISO (UTC) or relative 'in:5m', 'in:2h'
    when: dt.datetime
    if time.startswith("in:"):
        val = time.split(":", 1)[1]
        unit = val[-1]
        num = int(val[:-1])
        if unit == "s":
            delta = dt.timedelta(seconds=num)
        elif unit == "m":
            delta = dt.timedelta(minutes=num)
        elif unit == "h":
            delta = dt.timedelta(hours=num)
        else:
            raise click.ClickException("Unsupported relative time; use s, m, or h")
        when = dt.datetime.utcnow() + delta
    else:
        try:
            when = dt.datetime.fromisoformat(time)
        except Exception as e:
            raise click.ClickException(f"Invalid time format: {e}")
    asyncio.run(storage.init_db())
    sched_id = asyncio.run(storage.add_schedule(task, when.isoformat()))
    click.echo(f"Scheduled task id={sched_id} at {when.isoformat()} UTC")


@schedule.command("run")
@click.option("--interval", default=1.0, type=float)
def schedule_run(interval: float):
    click.echo("Running scheduler...")
    asyncio.run(run_scheduler(interval))


@main.command()
def monitor():
    """Simple monitor of recent tasks."""
    asyncio.run(storage.init_db())
    console = Console()
    try:
        while True:
            rows = asyncio.run(storage.list_tasks(20))
            table = Table(title="Recent Tasks")
            for col in ["id", "payload", "status", "created_at", "updated_at"]:
                table.add_column(col)
            for r in rows:
                table.add_row(*[str(x) for x in r])
            console.clear()
            console.print(table)
            asyncio.run(asyncio.sleep(2))
    except KeyboardInterrupt:
        pass


@main.command()
@click.argument("slash", required=False, default="")
def commands(slash: str):
    """Show slash-style command palette."""
    items = [
        "/init",
        "/auth anthropic",
        "/model list",
        "/model select",
        "/model set <name>",
        "/agent spawn <n>",
        "/queue add <task>",
        "/queue list",
        "/queue run",
        "/schedule add <task> <time>",
        "/schedule run",
        "/monitor",
    ]
    if slash:
        items = [x for x in items if x.startswith(slash)]
    click.echo("\n".join(items))


if __name__ == "__main__":
    main()
