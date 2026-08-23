#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONDONTWRITEBYTECODE=1

echo "[verify-repo] compile"
python3 -m compileall -q python_core services tools

echo "[verify-repo] unit and integration tests"
python3 -m unittest discover -s tests -v

echo "[verify-repo] agent contracts"
python3 services/orchestrator/validate_contracts.py

echo "[verify-repo] offline store/recall demo"
scripts/verify-local-demo.sh

echo "[verify-repo] canonical-source gate fails closed until governance inputs arrive"
set +e
GATE_OUTPUT="$(python3 tools/project-state/scripts/check_canonical_sources.py 2>&1)"
GATE_STATUS=$?
set -e
if [[ $GATE_STATUS -ne 2 ]] || [[ "$GATE_OUTPUT" != *"missing governance/01_AUTHORITY_MATRIX.yaml, governance/02_PROJECT_REGISTRY.yaml"* ]]; then
  echo "$GATE_OUTPUT" >&2
  echo "Unexpected project-state gate result: $GATE_STATUS" >&2
  exit 1
fi

echo "[verify-repo] PASS"
