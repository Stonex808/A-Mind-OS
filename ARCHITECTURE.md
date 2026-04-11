# A-Mind-OS Architecture (MVP-facing)

This file describes the implementation-facing architecture for the current A-Mind-OS MVP path.

## Current vs planned boundary

### Current
- static offline shell (`ui/shell/`)
- local orchestrator demo (`services/orchestrator/local_demo.py`)
- orchestrator service boundary (`services/orchestrator/orchestrator_service.py`)
- shared task schema (`services/orchestrator/task_schema.py`, `config/contracts/task_envelope.v1.json`)
- local JSON/SQLite persistence and structured execution logs
- local smoke tests (`scripts/verify-local-demo.sh`, `scripts/smoke-orchestrator-task-flow.sh`)

### Planned
- full planner/worker runtime beyond MVP workers
- dedicated Hydra LangSec/CodeSec/SysSec daemons
- richer IPC/message bus
- production Tauri shell and service packaging

## Layered MVP model

1. **Shell Layer** (visible control surface)
   - Tabs: Chat, Tasks, Files, Logs, Settings
   - health/status visibility and emergency pause UI

2. **Task Contract Layer** (shared schema)
   - `TaskEnvelope` validation for task intake
   - contract JSON for independent validation/interop

3. **Orchestrator Backbone** (system spine)
   - verifier checks intent safety/shape
   - planner selects worker based on task kind
   - dispatcher routes through worker registry
   - structured event logging (SQLite + JSONL)

4. **Memory Layer** (local-first persistence)
   - existing memory interfaces under `python_core/memory/`
   - orchestrator memory worker stores/recalls deterministic local context

## Orchestrator service boundary

Primary entry point for MVP flow:
- `LocalOrchestratorDemo.process_intent(raw_intent, source)`

Boundary responsibilities:
- verify and normalize raw intent
- translate intent to validated task envelope
- dispatch task via planner + worker registry
- persist run artifact + execution event log
- return structured result payload to caller/UI

## Dispatch shape (MVP)

- Planner: `LocalPlanner`
- Workers: `memory_worker`, `research_worker`, `code_worker`
- Dispatcher: `TaskDispatcher` (FIFO, one-task-at-a-time)

This keeps extension points explicit without claiming full MATPO/RL behavior.

## Logging & observability (current)

Artifacts written locally under `data/demo/` by default:
- `runs/run-*.json` (full run payload)
- `execution_events.jsonl` (append-only event log)
- `orchestrator.db` (`orchestrator_task_events` table)

## Smoke test path

- `scripts/verify-local-demo.sh` validates store+recall path and artifacts.
- `scripts/smoke-orchestrator-task-flow.sh` validates task intake, routing, and execution event persistence.

## Design rules

- local-first by default
- modular boundaries over giant rewrites
- docs must match runnable state
- defer heavy future systems until MVP spine is stable
