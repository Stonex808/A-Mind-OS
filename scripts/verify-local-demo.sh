#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data/demo"
DEMO_MEMORY_DIR="$DATA_DIR/memory"
USER_MEMORY_DIR="$ROOT_DIR/data/user/memory"
DB_PATH="$DATA_DIR/orchestrator.db"
EVENTS_PATH="$DATA_DIR/execution_events.jsonl"
RUNS_DIR="$DATA_DIR/runs"
INTENT_FILE="$DATA_DIR/demo-intent.txt"

fail() {
  echo "[verify-local-demo] ERROR: $1" >&2
  exit 1
}

echo "[verify-local-demo] preparing offline local demo verification"
"$ROOT_DIR/scripts/setup.sh"

echo
echo "[verify-local-demo] running scripts/dev.sh"
"$ROOT_DIR/scripts/dev.sh" > /tmp/refocus-local-demo.log
cat /tmp/refocus-local-demo.log

echo
echo "[verify-local-demo] validating expected artifacts"
[[ -f "$INTENT_FILE" ]] || fail "missing intent file: $INTENT_FILE"
[[ -f "$DB_PATH" ]] || fail "missing sqlite index: $DB_PATH"
[[ -f "$EVENTS_PATH" ]] || fail "missing execution events log: $EVENTS_PATH"
[[ -d "$RUNS_DIR" ]] || fail "missing runs directory: $RUNS_DIR"
[[ -f "$DEMO_MEMORY_DIR/semantic_local/facts.json" ]] || fail "missing demo semantic memory facts.json"
[[ -d "$DEMO_MEMORY_DIR/episodic_local/episodes" ]] || fail "missing demo episodic memory episodes directory"
[[ -d "$DEMO_MEMORY_DIR/procedural" ]] || fail "missing demo procedural memory directory"
[[ -d "$USER_MEMORY_DIR/episodic_local/episodes" ]] || fail "missing default user episodic directory scaffold"
[[ -d "$USER_MEMORY_DIR/semantic_local" ]] || fail "missing default user semantic directory scaffold"
[[ -d "$USER_MEMORY_DIR/procedural" ]] || fail "missing default user procedural directory scaffold"

RUN_COUNT="$(find "$RUNS_DIR" -maxdepth 1 -name 'run-*.json' | wc -l | tr -d ' ')"
(( RUN_COUNT >= 2 )) || fail "expected at least 2 run artifacts, found $RUN_COUNT"

python3 - <<'PY' "$DB_PATH" "$RUNS_DIR"
import json
import sqlite3
import sys
from pathlib import Path

db_path = Path(sys.argv[1])
runs_dir = Path(sys.argv[2])

with sqlite3.connect(db_path) as conn:
    events_count = conn.execute("SELECT COUNT(*) FROM orchestrator_task_events").fetchone()[0]
if events_count < 2:
    raise SystemExit(f"expected at least 2 task-event rows in {db_path}, found {events_count}")

latest_runs = sorted(runs_dir.glob("run-*.json"))[-2:]
payloads = [json.loads(path.read_text(encoding="utf-8")) for path in latest_runs]
statuses = [payload.get("result", {}).get("status") for payload in payloads]
if "stored" not in statuses or "recalled" not in statuses:
    raise SystemExit(f"expected latest runs to include stored and recalled statuses, got {statuses}")

recall_payload = next(payload for payload in payloads if payload.get("result", {}).get("status") == "recalled")
recall_blob = json.dumps(recall_payload)
if "backup path" not in recall_blob and "./data/backups" not in recall_blob:
    raise SystemExit("recall payload does not mention the saved backup path")

print("Artifact validation passed.")
PY

echo
echo "[verify-local-demo] success"
echo "The currently implemented local path is working offline."
echo "Not runnable yet by design: the full systemd boot chain, Hydra security services, kernel/eBPF instrumentation, and the production multi-agent runtime."
