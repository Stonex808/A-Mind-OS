#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data/demo"
RUNS_DIR="$DATA_DIR/runs"
MEMORY_DIR="$ROOT_DIR/data/memory"
INTENT_FILE="$DATA_DIR/demo-intent.txt"

mkdir -p "$DATA_DIR" "$RUNS_DIR"

cat > "$INTENT_FILE" <<'EOT'
remember the preferred backup path is ./data/backups
EOT

echo "[Refocus-OS] local demo runner"
echo "Offline mode: no cloud calls, no telemetry, no hidden setup"
echo
echo "1) storing an intent from a local file"
python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --intent-file "$INTENT_FILE"

echo
echo "2) recalling context from stdin"
printf 'recall backup path\n' | python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --stdin

echo
echo "Artifacts written under $DATA_DIR"
echo "- Intent file: $INTENT_FILE"
echo "- SQLite index: $DATA_DIR/orchestrator.db"
echo "- JSON run logs: $RUNS_DIR/"
echo "- Memory JSON: $MEMORY_DIR/"
echo
echo "Success looks like:"
echo "- The first run returns \"accepted\": true and \"status\": \"stored\""
echo "- The second run returns \"accepted\": true and \"status\": \"recalled\""
echo "- The recall output mentions the saved backup path in past_experiences or relevant_facts"
echo
echo "Security note: artifacts are plain-text local files; use disk encryption or encrypted backups if the intents contain sensitive data."
