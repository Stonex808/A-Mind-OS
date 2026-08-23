# Orchestrator Service — agents.md

**Status:** implemented now (with a narrower local-first scope than the long-term architecture)

**Best contributor on-ramp:** run `scripts/verify-repo.sh` before editing.

**Current runnable scope:** strict local intent validation, typed tasks, deterministic planner/worker routing, JSON/SQLite persistence, recall, retention, and an optional Unix socket demo.

**Long-term scope:** admitted signed IPC, authenticated agent sessions, sandboxed workers, and systemd-managed orchestration.

**Role:** System Orchestrator

**Dependencies now:** Python 3.11+ standard library.

**Dependencies later:** choose only after the admitted IPC contract is tested.

## Execution Plan
1. Keep `local_demo.py`, `task_schema.py`, and `orchestrator_service.py` as the only implementation path.
2. Add admitted, signed IPC without bypassing `harness_runtime.py`.
3. Add replay/tampering tests before a non-demo worker.
4. Wire OS-process supervision only behind the lifecycle contract.

## Verification
- `scripts/verify-repo.sh` passes without third-party packages.
- Redaction, refusal, retention, routing, recall, and event logging are covered under `tests/`.
- Future scope must add authentication, replay protection, and sandbox evidence before being labeled runnable.
