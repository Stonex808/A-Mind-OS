#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[A-Mind-OS] local setup"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.11 or newer is required." >&2
  exit 1
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")
print(f"Python {sys.version.split()[0]} is available.")
PY

mkdir -p \
  "$ROOT_DIR/data/demo/runs" \
  "$ROOT_DIR/data/demo/memory/episodic_local/episodes" \
  "$ROOT_DIR/data/demo/memory/semantic_local" \
  "$ROOT_DIR/data/demo/memory/procedural" \
  "$ROOT_DIR/data/user/memory/episodic_local/episodes" \
  "$ROOT_DIR/data/user/memory/semantic_local" \
  "$ROOT_DIR/data/user/memory/procedural"

echo "Local data directories are ready under data/."
echo "Run scripts/verify-repo.sh for the complete offline check."
