import os
from click.testing import CliRunner
from forge.cli import main
from forge import storage
import asyncio


def test_model_list_shows_examples():
    runner = CliRunner()
    res = runner.invoke(main, ["model", "list"])
    assert res.exit_code == 0
    assert "debug-echo" in res.output


def test_queue_add_and_list(tmp_path, monkeypatch):
    # Use temp DB
    monkeypatch.setenv("FORGE_CONFIG", str(tmp_path / "config.yaml"))
    storage.DB_PATH = tmp_path / "forge.db"  # type: ignore
    asyncio.run(storage.init_db())

    runner = CliRunner()
    res = runner.invoke(main, ["queue", "add", "hello-world-task"])
    assert res.exit_code == 0

    res2 = runner.invoke(main, ["queue", "list", "--limit", "5"])
    assert res2.exit_code == 0
    assert "hello-world-task" in res2.output
