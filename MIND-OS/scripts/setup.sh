#!/usr/bin/env bash
set -euo pipefail

echo "[Refocus-OS] bootstrap starting..."

# Python
if command -v python3 >/dev/null 2>&1; then
  python3 --version
else
  echo "python3 not found. Install Python 3.11+."
fi

# Node, Rust, Tauri (optional)
if command -v node >/dev/null 2>&1; then node -v; else echo "node not found (UI optional)"; fi
if command -v cargo >/dev/null 2>&1; then cargo --version; else echo "rust/cargo not found (UI optional)"; fi

echo "Done."
