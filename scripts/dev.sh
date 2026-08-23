#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DATA_DIR="${REFOCUS_DEMO_DATA_DIR:-$ROOT_DIR/data/demo}"
DEMO_MEMORY_ROOT="${REFOCUS_DEMO_MEMORY_ROOT:-$DEMO_DATA_DIR/memory}"
DEMO_FEED_PATH="${REFOCUS_DEMO_FEED_PATH:-$ROOT_DIR/ui/shell/orchestrator-feed.json}"
INTENT_FILE="$DEMO_DATA_DIR/demo-intent.txt"

mkdir -p "$DEMO_DATA_DIR" "$DEMO_MEMORY_ROOT"
printf '%s\n' 'remember the preferred backup path is ./data/backups' > "$INTENT_FILE"

export REFOCUS_DEMO_DATA_DIR="$DEMO_DATA_DIR"
export REFOCUS_DEMO_MEMORY_ROOT="$DEMO_MEMORY_ROOT"
export REFOCUS_DEMO_FEED_PATH="$DEMO_FEED_PATH"

echo "[A-Mind-OS] offline local demo"
echo "Data: $DEMO_DATA_DIR"
echo "Sensitive-content mode: ${REFOCUS_SENSITIVE_CONTENT_MODE:-redact}"
echo
echo "1) Store an intent"
python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --intent-file "$INTENT_FILE"
echo
echo "2) Recall the stored context"
printf '%s\n' 'recall backup path' | python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --stdin
echo
echo "3) Export the optional shell feed"
python3 "$ROOT_DIR/services/orchestrator/export_shell_feed.py"
echo
echo "Artifacts: $DEMO_DATA_DIR"
echo "Shell feed: $DEMO_FEED_PATH"
