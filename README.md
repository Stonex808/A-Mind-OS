# A-Mind-OS

A-Mind-OS is the **implementation track** for a local-first, AI-native operating environment inspired by Refocus-OS.

This repo is focused on an MVP you can run today:
- visible offline shell prototype
- local orchestrator service boundary with task routing
- local memory persistence
- structured execution logging
- smoke-testable developer flow

## Source of truth
For MVP planning, use these files first:
1. `README_MVP.md`
2. `ARCHITECTURE_MVP.md`
3. `TASKS.md`
4. `CODEX_PHASE1_2_PROMPT.md`

## Current runnable path

### 1) Setup
```bash
scripts/setup.sh
```

### 2) Run local orchestrator demo
```bash
scripts/verify-local-demo.sh
```

### 3) Run orchestrator task-flow smoke test
```bash
scripts/smoke-orchestrator-task-flow.sh
```

### 4) Run shell prototype
```bash
python3 -m http.server 4173 --directory ui/shell
```
Open `http://localhost:4173`.

## What is implemented now
- **Shell prototype** with tabs for Chat, Tasks, Files, Logs, Settings and visible health state in `ui/shell/`.
- **Orchestrator boundary** in `services/orchestrator/orchestrator_service.py` with planner, worker registry, dispatcher, and structured logging.
- **Shared task schema** in `services/orchestrator/task_schema.py` and `config/contracts/task_envelope.v1.json`.
- **Local demo path** in `services/orchestrator/local_demo.py` using verifier + dispatcher + local memory.
- **Smoke tests** in `services/orchestrator/test_task_flow.py` and `scripts/smoke-orchestrator-task-flow.sh`.

## Deferred by design
- full RL/MATPO training
- custom NHA
- eBPF SysSec runtime
- full multi-service/systemd production stack

## Contributor orientation
- Start local-first and offline-first.
- Prefer vertical slices over architecture-only stubs.
- Keep docs aligned with current reality.
- Treat contracts and task schema as service boundary anchors.
