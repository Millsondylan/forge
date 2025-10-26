from __future__ import annotations
import asyncio
import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
from datetime import datetime
import aiosqlite

DB_PATH = Path("forge.db").resolve()


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              payload TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'queued',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              task TEXT NOT NULL,
              run_at TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'scheduled'
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              label TEXT NOT NULL,
              kind TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        await db.commit()


async def enqueue_task(payload: str) -> int:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO tasks (payload, status, created_at, updated_at) VALUES (?, 'queued', ?, ?)",
            (payload, now, now),
        )
        await db.commit()
        return cur.lastrowid


async def list_tasks(limit: int = 50) -> Sequence[tuple[int, str, str, str, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, payload, status, created_at, updated_at FROM tasks ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return await cur.fetchall()


async def acquire_next_task() -> Optional[tuple[int, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        cur = await db.execute(
            "SELECT id, payload FROM tasks WHERE status='queued' ORDER BY id LIMIT 1"
        )
        row = await cur.fetchone()
        if not row:
            await db.execute("COMMIT")
            return None
        task_id, payload = row
        now = datetime.utcnow().isoformat()
        await db.execute(
            "UPDATE tasks SET status='in_progress', updated_at=? WHERE id=? AND status='queued'",
            (now, task_id),
        )
        await db.commit()
        return task_id, payload


async def complete_task(task_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        await db.execute(
            "UPDATE tasks SET status='done', updated_at=? WHERE id=?",
            (now, task_id),
        )
        await db.commit()


async def fail_task(task_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        await db.execute(
            "UPDATE tasks SET status='failed', updated_at=? WHERE id=?",
            (now, task_id),
        )
        await db.commit()


async def add_schedule(task: str, run_at_iso: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO schedules (task, run_at, status) VALUES (?, ?, 'scheduled')",
            (task, run_at_iso),
        )
        await db.commit()
        return cur.lastrowid


async def due_schedules(now_iso: Optional[str] = None) -> Sequence[tuple[int, str]]:
    now_iso = now_iso or datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, task FROM schedules WHERE status='scheduled' AND run_at <= ?",
            (now_iso,),
        )
        return await cur.fetchall()


async def mark_schedule_done(sched_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE schedules SET status='done' WHERE id=?", (sched_id,))
        await db.commit()
