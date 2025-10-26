# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

- Setup (editable install + dev tools):
  - python3 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -e .[dev]
  - make dev
- Auth (Anthropic browser login):
  - forge auth anthropic       # opens browser; grant access
- Model ops:
  - forge model list           # queries Anthropic CLI; also shows configured models + debug-echo
  - forge model select         # interactive selector (numbers) then persists to config
  - forge model set <model>    # e.g. claude-3.5-sonnet | claude-3.5-haiku | debug-echo
- Queue:
  - forge init                 # creates config + DB (idempotent)
  - forge queue add "<task>"   # enqueue a task (free-form string)
  - forge queue list --limit 20
  - forge queue run --concurrency 500 --model claude-3.5-sonnet
- Agents:
  - forge agent spawn 500 --model claude-3.5-sonnet
- Scheduler:
  - forge schedule add "<task>" in:5m
  - forge schedule run --interval 1.0
- Monitor (simple TUI):
  - forge monitor
- Slash-style palette:
  - forge commands           # prints /-prefixed command palette
- Lint/format/typecheck/tests:
  - make lint
  - make format
  - make typecheck
  - make test
  - make test-one k="pattern"   # run a single test

## Architecture (big picture)

- CLI entry (forge.cli)
  - click-based groups: auth, model, agent, queue, schedule, monitor
  - Uses system keyring for API keys; config at config.yaml (override via FORGE_CONFIG)
- Config (forge.config)
  - YAML config with default model and retry/concurrency settings
  - ensure_config(), load_config(), set_model()
- Providers (forge.providers, forge.models)
  - Anthropic-only routing (Claude models). Debug echo available for offline tests.
- Storage/Queue (forge.storage)
  - aiosqlite-backed persistence (forge.db): tasks, schedules, todos
  - Atomic acquisition with BEGIN IMMEDIATE; statuses: queued → in_progress → done/failed
- Agents and Pool (forge.agent, forge.agent_manager)
  - Agent wraps a single provider call with basic logical verification and logging
  - run_queue(concurrency, provider, retries) spawns N workers pulling from persistent queue
- Scheduler (forge.scheduler)
  - Polls schedules table and enqueues due tasks; separate long-running process
- System prompt (forge.system_prompt)
  - Default discipline/verification prompt used by agents if provided via CLI/code

## Notes for future agents

- Default model is debug-echo for offline dev; set a real model via forge model set <model> before production runs.
- Keys are stored in OS keyring; environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, OLLAMA_HOST) are also respected at runtime.
- Tests run fully offline using the echo provider and an isolated sqlite DB.

## From README (essentials)

- Philosophy: truth, full completion, discovery-first, no fabrication, double verification.
- Goals: 500+ concurrent agents; model switching; persistent queue/memory; scheduler; self-verification loop.
- Command structure aligns with README’s forge init/auth/model/agent/queue/schedule/monitor.
