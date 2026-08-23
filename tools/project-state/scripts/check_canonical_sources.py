#!/usr/bin/env python3
"""Fail closed when complete canonical Matrix/Registry inputs are absent or look partial."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
paths = [
    ROOT / "governance/01_AUTHORITY_MATRIX.yaml",
    ROOT / "governance/02_PROJECT_REGISTRY.yaml",
]
missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
if missing:
    print("CANONICAL_SOURCE_GATE_BLOCKED: missing " + ", ".join(missing))
    raise SystemExit(2)

try:
    import yaml
except ImportError:
    print("CANONICAL_SOURCE_GATE_BLOCKED: PyYAML is required when canonical inputs exist")
    raise SystemExit(2)

matrix = yaml.safe_load(paths[0].read_text(encoding="utf-8"))
registry = yaml.safe_load(paths[1].read_text(encoding="utf-8"))
errors = []
if matrix.get("meta", {}).get("final_authority") != "STONE":
    errors.append("matrix final_authority must be STONE")
projects = registry.get("projects")
if not isinstance(projects, dict):
    errors.append("registry.projects must be a mapping")
else:
    if len(projects) < 25:
        errors.append(f"registry appears partial: only {len(projects)} projects")
    for project_id in (
        "aetheris",
        "a-mind-os",
        "a-mind-librarian",
        "mains",
        "monetization-os",
        "multi-ai-business-os",
    ):
        if project_id not in projects:
            errors.append(f"required canonical project missing: {project_id}")
if errors:
    print("CANONICAL_SOURCE_GATE_FAILED")
    for error in errors:
        print("- " + error)
    raise SystemExit(3)
print(
    "CANONICAL_SOURCE_GATE_PASS: "
    f"projects={len(projects)} "
    f"matrix={matrix['meta'].get('matrix_version')} "
    f"registry={registry['meta'].get('registry_version')}"
)
