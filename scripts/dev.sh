#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DATA_DIR="${REFOCUS_DEMO_DATA_DIR:-$ROOT_DIR/data/demo}"
DEMO_MEMORY_ROOT="${REFOCUS_DEMO_MEMORY_ROOT:-$ROOT_DIR/data/demo/memory}"
INTENT_FILE="$DEMO_DATA_DIR/demo-intent.txt"

mkdir -p "$DEMO_DATA_DIR" "$DEMO_MEMORY_ROOT"

cat > "$INTENT_FILE" <<'EOT'
remember the preferred backup path is ./data/backups
EOT

echo "[Refocus-OS] local demo runner"
echo "Offline mode: no cloud calls, no telemetry, no hidden setup"
echo "Demo data directory: $DEMO_DATA_DIR"
echo "Demo memory directory: $DEMO_MEMORY_ROOT"
echo "Sensitive-content mode: ${REFOCUS_SENSITIVE_CONTENT_MODE:-redact}"
echo

echo "1) storing an intent from a local file"
REFOCUS_DEMO_DATA_DIR="$DEMO_DATA_DIR" \
REFOCUS_MEMORY_SEMANTIC_DIR="${REFOCUS_MEMORY_SEMANTIC_DIR:-$DEMO_MEMORY_ROOT/semantic_local}" \
REFOCUS_MEMORY_EPISODIC_DIR="${REFOCUS_MEMORY_EPISODIC_DIR:-$DEMO_MEMORY_ROOT/episodic_local}" \
REFOCUS_MEMORY_PROCEDURAL_DIR="${REFOCUS_MEMORY_PROCEDURAL_DIR:-$DEMO_MEMORY_ROOT/procedural}" \
python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --intent-file "$INTENT_FILE"

echo
echo "2) recalling context from stdin"
printf 'recall backup path\n' | \
REFOCUS_DEMO_DATA_DIR="$DEMO_DATA_DIR" \
REFOCUS_MEMORY_SEMANTIC_DIR="${REFOCUS_MEMORY_SEMANTIC_DIR:-$DEMO_MEMORY_ROOT/semantic_local}" \
REFOCUS_MEMORY_EPISODIC_DIR="${REFOCUS_MEMORY_EPISODIC_DIR:-$DEMO_MEMORY_ROOT/episodic_local}" \
REFOCUS_MEMORY_PROCEDURAL_DIR="${REFOCUS_MEMORY_PROCEDURAL_DIR:-$DEMO_MEMORY_ROOT/procedural}" \
python3 "$ROOT_DIR/services/orchestrator/local_demo.py" --stdin

echo
echo "Artifacts written under $DEMO_DATA_DIR"
echo "- Intent file: $INTENT_FILE"
echo "- SQLite index: $DEMO_DATA_DIR/orchestrator.db"
echo "- JSON run logs: $DEMO_DATA_DIR/runs/"
echo "- Demo memory JSON: $DEMO_MEMORY_ROOT/"
echo "- Retention knobs: config/refocus-os.toml [local_persistence.demo]"
echo
echo "Success looks like:"
echo "- The first run returns \"accepted\": true and \"status\": \"stored\""
echo "- The second run returns \"accepted\": true and \"status\": \"recalled\""
echo "- The recall output mentions the saved backup path in past_experiences or relevant_facts"
echo
echo "Security note: artifacts are plain-text local files by design. Use disk encryption or encrypted backups for sensitive data, or set REFOCUS_SENSITIVE_CONTENT_MODE=refuse to block obviously sensitive content from being written."
