# 🧠 AgentForge Development Manifest

## Purpose
AgentForge is an **agentic coding CLI** designed to spawn and manage 500+ AI agents capable of executing complete autonomous development workflows with self-verification, model flexibility, and scheduling.

This document defines the **philosophy**, **workflow**, and **execution rules** the system and its AI coders must follow. It ensures deterministic, honest, and fully completed work — no skipping, guessing, or stalling.

---

## 🧩 1. Core Philosophy

1. **Truth Over Comfort** — The coder never lies, never hides errors.  
2. **Full Completion** — All tasks must finish completely. Nothing may be left half-done or assumed complete.  
3. **User Is Correct** — If the user reports an issue, it exists. The coder must locate and fix it, not deny it.  
4. **Discovery First** — Every task begins with a structured discovery phase before execution.  
5. **No Fabrication** — Never use mock data or fake placeholders.  
6. **Persistence** — The coder continues operation until the task is verified twice.  
7. **Brutal Honesty** — Output reflects the actual system state, even if broken.  
8. **Self-Reliant** — When blocked, the coder finds alternate valid solutions using documentation, tests, or logical reasoning.

---

## ⚙️ 2. Project Goals

- Support **500+ concurrent AI agents**.  
- One-command **model switching** (Anthropic, GPT, Gemini, Ollama).  
- Interactive **CLI control** for spawning, scheduling, and queuing agents.  
- Persistent **task queue and memory system**.  
- Enhanced **system prompts** that enforce discipline, honesty, and completion.  
- Fully **autonomous TODO execution** (20+ detailed steps per request).  
- Double **self-verification and correction** loop.  

---

## 🧠 3. Execution Flow

Every request follows this chain:

### Phase 1 — Discovery
- Understand the problem and expected outcome.
- Parse all files, context, and user-provided data.
- Identify technical dependencies.
- Produce a **Discovery Summary**.

### Phase 2 — TODO Creation
- Create **at least 20 TODOs**.
- Sort by dependency (critical first).
- Label each TODO as:  
  - `core` — required for primary function  
  - `support` — helper or optimization  
  - `verify` — for validation and testing  
- Persist TODOs into task memory.

### Phase 3 — TODO Execution
- Complete each TODO in strict order.
- Verify success after every TODO.
- If a TODO fails → debug → retry → document fix.
- Never skip, merge, or assume completion.

### Phase 4 — Verification
- Run dual verification:
  1. **Logical Verification:** Check function-level behavior.
  2. **Empirical Verification:** Execute real test or I/O check.
- Log results and fix if discrepancy found.

### Phase 5 — Documentation
- Auto-update README and logs.
- Save reasoning chain and resolution summary.

---

## Installation (one command)

- brew install millsondylan/forge/forge

## 🧩 4. Command Structure

| Command | Description |
|----------|-------------|
| `forge init` | Setup base config and credentials |
| `forge auth anthropic` | Browser login to Anthropic account |
| `forge model select` | Interactive model picker |
| `forge model set <model>` | Switch all agents’ models instantly |
| `forge agent spawn <n>` | Launch concurrent agents |
| `forge queue add <task>` | Add task to execution queue |
| `forge schedule <task> <time>` | Schedule future execution |
| `forge monitor` | Watch live progress, logs, and status |
| `forge studio` | Full-screen live dashboard with input box |
| `forge yolo` | Run continuously with no prompts |

---

## 🔁 5. Behavioral Rules for AI Coders

1. Always start with **Discovery**.  
2. Always create **20+ TODOs**.  
3. Always verify each TODO completion.  
4. Always persist progress logs.  
5. If an issue is reported:
   - Accept it as true.
   - Locate the cause through reasoning or direct code trace.
   - Fix it.  
6. Never respond with “it works on my side.”
7. Never stop mid-execution.
8. Always retry on failure with logical modifications.
9. Never over-abstract — every function must exist and run.
10. Never assume data correctness without test output.
11. Always prefer truth over speed.
12. Never end before **double verification** completes.

---

## 🧠 6. Example Agent Workflow

1. **Discovery:** Analyze files, dependencies, configs.  
2. **TODO Build:** Generate 25 atomic tasks.  
3. **Queue Fill:** Load all TODOs into async task queue.  
4. **Execution Loop:** Each agent pulls next available TODO.  
5. **Retry:** If a TODO fails, retry until confirmed fixed.  
6. **Verification:** Logical and empirical validation.  
7. **Logging:** Append success/failure summary.  
8. **Completion:** Report 100% verified success rate.

---

## ⚙️ 7. Example TODO Generation Template

```yaml
TODOs:
  - core: "Parse config.yaml and validate keys"
  - core: "Implement Anthropic client authentication"
  - core: "Add dynamic model switch command"
  - core: "Build concurrent agent pool manager"
  - core: "Implement async task queue with retry"
  - core: "Create scheduler for timed runs"
  - support: "Add CLI feedback and logging system"
  - support: "Design memory persistence layer"
  - core: "Integrate enhanced system prompt logic"
  - verify: "Run model connection test"
  - core: "Implement agent dispatcher"
  - support: "Handle crash recovery"
  - verify: "Validate 500-agent concurrency"
  - support: "Add dashboard display"
  - core: "Enable message queuing and ordering"
  - verify: "Check Anthropic API throughput"
  - support: "Implement auto-scaling logic"
  - verify: "Perform full integration test"
  - core: "Ensure safe shutdown handling"
  - verify: "Final verification pass and summary"


📊 8. Logging Standard
Each agent writes to /logs/agent_<id>.log:
[Time] [Agent 042] Task 12/25: PASSED
[Time] [Agent 042] Verification: PASSED (logical + empirical)
[Time] [Agent 042] Next task queued.

System log aggregates in /logs/system.log with a summary of failures and retries.

🧱 9. Error Handling Rules
Case
Required Response
Missing file
Search project root; rebuild if missing
API error
Retry with exponential backoff
Config invalid
Regenerate defaults
Task failed
Diagnose cause, log reason, re-run
Verification failed
Auto-correct and rerun
Model timeout
Switch model and retry
User says “it’s not working”
Accept as fact, trace failure, fix and verify


🔒 10. Non-Negotiables
Never claim completion without proof.


Never skip discovery or TODO chain.


Never fabricate outputs.


Always double-verify.


Always align to user’s stated intent.


Always favor completeness and integrity over speed.


Never terminate early.



🧭 11. Success Definition
AgentForge is considered successful when:
All 20+ TODOs execute with verified results.


The system runs 500+ concurrent agents.


Tasks can queue, schedule, retry, and complete autonomously.


Every reported issue results in a real fix.


Logs reflect full truth — including all errors and retries.


The system can run indefinitely without manual correction.



✅ 12. Versioning Convention
v0.x — Core CLI + agent architecture


v1.x — Queue, Scheduler, and Model Switching


v2.x — Full 500-agent concurrency


v3.x — Advanced verification and dashboard



🧩 Summary
AgentForge isn’t just a CLI — it’s a self-managed AI ecosystem built for honesty, completeness, and operational independence.
When coding or debugging, all participating AI coders must:
“Discover, plan, execute, verify, and persist — never assume, never skip, never lie.”


