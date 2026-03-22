#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=11

print_section() {
  printf '\n== %s ==\n' "$1"
}

version_ge() {
  local actual_major="$1"
  local actual_minor="$2"
  if (( actual_major > REQUIRED_PYTHON_MAJOR )); then
    return 0
  fi
  if (( actual_major == REQUIRED_PYTHON_MAJOR && actual_minor >= REQUIRED_PYTHON_MINOR )); then
    return 0
  fi
  return 1
}

print_section "[Refocus-OS] local-first bootstrap"
printf 'Repository root: %s\n' "$ROOT_DIR"
printf 'This setup script only checks local prerequisites and creates local data directories.\n'
printf 'It does not install packages, call cloud services, or hide any extra steps.\n'

print_section "Required dependency"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}+ before running the demo."
  exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major} {sys.version_info.minor} {sys.version_info.micro}")')"
read -r PY_MAJOR PY_MINOR PY_PATCH <<<"$PYTHON_VERSION"
printf 'python3 version: %s.%s.%s\n' "$PY_MAJOR" "$PY_MINOR" "$PY_PATCH"

if ! version_ge "$PY_MAJOR" "$PY_MINOR"; then
  echo "Python ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}+ is required for the currently implemented local demo."
  exit 1
fi

echo "Required path is available: python3 for scripts/dev.sh and services/orchestrator/local_demo.py"

print_section "Optional local dependencies"
cat <<'EOT'
Optional dependencies are not required for the default offline demo path:
- chromadb + sentence-transformers: enable vector-backed episodic/semantic memory instead of the built-in JSON fallback.
- structlog: enables structured JSON logging for Python components.
- jsonschema: required if you want to run contract schema validation or the contract validator tests.
- node, cargo/rust: only needed for future UI/Tauri work, not for the current demo.
- socat: only needed if you want to manually test --socket mode from another shell.
EOT

for tool in node cargo socat; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'optional tool available: %s -> %s\n' "$tool" "$($tool --version 2>/dev/null | head -n 1)"
  else
    printf 'optional tool missing: %s (ok for local demo)\n' "$tool"
  fi
done

print_section "Local data directories"
mkdir -p \
  "$ROOT_DIR/data/demo/runs" \
  "$ROOT_DIR/data/demo/memory/episodic_local/episodes" \
  "$ROOT_DIR/data/demo/memory/semantic_local" \
  "$ROOT_DIR/data/demo/memory/procedural" \
  "$ROOT_DIR/data/user/memory/episodic_local/episodes" \
  "$ROOT_DIR/data/user/memory/semantic_local" \
  "$ROOT_DIR/data/user/memory/procedural"

cat <<EOT
Created or verified these local-only directories:
- $ROOT_DIR/data/demo/
- $ROOT_DIR/data/demo/runs/
- $ROOT_DIR/data/demo/memory/episodic_local/episodes/
- $ROOT_DIR/data/demo/memory/semantic_local/
- $ROOT_DIR/data/demo/memory/procedural/
- $ROOT_DIR/data/user/memory/episodic_local/episodes/
- $ROOT_DIR/data/user/memory/semantic_local/
- $ROOT_DIR/data/user/memory/procedural/
EOT

print_section "Next step"
cat <<'EOT'
Run one of these from the repository root:
- scripts/dev.sh               # end-to-end local demo with stored + recalled intent
- scripts/verify-local-demo.sh # offline verification wrapper with artifact checks
EOT
