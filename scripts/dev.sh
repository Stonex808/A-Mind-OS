#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data/demo"
INTENT_FILE="$DATA_DIR/demo-intent.txt"

mkdir -p "$DATA_DIR"

cat > "$INTENT_FILE" <<'EOF'
remember the preferred backup path is ./data/backups
EOF

echo "[Refocus-OS] local demo runner"
echo "1) storing an intent from a local file"
python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --intent-file "$INTENT_FILE"

echo
echo "2) recalling context from stdin"
printf 'recall backup path\n' | python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --stdin

echo
echo "Artifacts written under $DATA_DIR"
echo "- SQLite index: $DATA_DIR/orchestrator.db"
echo "- JSON run logs: $DATA_DIR/runs/"
echo "- Memory JSON: $ROOT_DIR/data/memory/"
echo
echo "Security note: artifacts are plain-text local files; use disk encryption or encrypted backups if the intents contain sensitive data."
