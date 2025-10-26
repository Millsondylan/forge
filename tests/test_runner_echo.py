import asyncio
from forge import storage
from forge.agent_manager import run_queue
from forge.models import make_provider


def test_run_queue_with_echo(tmp_path, monkeypatch):
    # Isolate DB
    storage.DB_PATH = tmp_path / "forge.db"  # type: ignore
    asyncio.run(storage.init_db())

    # Enqueue one task
    asyncio.run(storage.enqueue_task("say hello"))

    # Provider: echo (no network)
    _, provider = make_provider("debug-echo")

    # Run single worker
    asyncio.run(run_queue(1, provider, retries=0))

    # Should be marked done
    rows = asyncio.run(storage.list_tasks(10))
    assert rows[0][2] == "done"
