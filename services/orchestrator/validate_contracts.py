"""CLI entry point for deterministic local contract validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from contract_registry import ContractRegistry, ContractValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate orchestrator agent contracts without network access."
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        action="append",
        help="Optional contract directory. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = ContractRegistry(search_roots=args.contracts_dir) if args.contracts_dir else ContractRegistry()
    try:
        registerable = registry.contracts_for_registration()
    except ContractValidationError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"Contract validation failed: {exc}")
        return 1

    if args.json:
        print(json.dumps({"ok": True, "contracts": registerable}, indent=2, sort_keys=True))
    else:
        print("Validated contracts:")
        for agent_name, metadata in sorted(registerable.items()):
            print(f"- {agent_name} ({metadata['role']}) -> {metadata['source_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
