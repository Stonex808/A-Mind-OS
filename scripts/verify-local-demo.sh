#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERIFY_DIR="$(mktemp -d)"
trap 'rm -rf -- "$VERIFY_DIR"' EXIT

export PYTHONDONTWRITEBYTECODE=1
export REFOCUS_DEMO_DATA_DIR="$VERIFY_DIR/demo"
export REFOCUS_DEMO_MEMORY_ROOT="$VERIFY_DIR/memory"
export REFOCUS_DEMO_FEED_PATH="$VERIFY_DIR/orchestrator-feed.json"

echo "[verify-local-demo] running in $VERIFY_DIR"
"$ROOT_DIR/scripts/dev.sh" > "$VERIFY_DIR/demo.log"

python3 - "$REFOCUS_DEMO_DATA_DIR" "$REFOCUS_DEMO_MEMORY_ROOT" "$REFOCUS_DEMO_FEED_PATH" <<'PY'
import json
import sqlite3
import sys
from pathlib import Path

data_dir, memory_dir, feed_path = map(Path, sys.argv[1:])
runs = sorted((data_dir / "runs").glob("run-*.json"))
if len(runs) != 2:
    raise SystemExit(f"expected exactly two run artifacts, found {len(runs)}")
payloads = [json.loads(path.read_text(encoding="utf-8")) for path in runs]
statuses = {payload["result"]["status"] for payload in payloads}
if statuses != {"stored", "recalled"}:
    raise SystemExit(f"unexpected demo statuses: {sorted(statuses)}")
recall = next(payload for payload in payloads if payload["result"]["status"] == "recalled")
if "backup" not in json.dumps(recall).lower():
    raise SystemExit("the recall artifact does not contain the stored backup context")
with sqlite3.connect(data_dir / "orchestrator.db") as connection:
    runs_count = connection.execute("SELECT COUNT(*) FROM orchestrator_runs").fetchone()[0]
    events_count = connection.execute("SELECT COUNT(*) FROM orchestrator_task_events").fetchone()[0]
if (runs_count, events_count) != (2, 2):
    raise SystemExit(f"unexpected SQLite counts: runs={runs_count}, events={events_count}")
for required in (
    memory_dir / "semantic_local" / "facts.json",
    memory_dir / "semantic_local" / "concepts.json",
    memory_dir / "episodic_local" / "episodes",
    feed_path,
):
    if not required.exists():
        raise SystemExit(f"missing demo artifact: {required}")
print("Local store/recall path passed.")
PY
