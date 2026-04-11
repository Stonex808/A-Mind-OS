#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[smoke-orchestrator-task-flow] running orchestrator task flow smoke test"
python3 "$ROOT_DIR/services/orchestrator/test_task_flow.py"

echo "[smoke-orchestrator-task-flow] success"
