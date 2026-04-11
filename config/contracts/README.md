# Contracts

Put semver JSON contracts here. Each contract defines:
- inputs/outputs schema
- permitted tools/syscalls
- budget ceilings
- verifier hooks

The Orchestrator loads contracts from `/etc/refocus/contracts` (system path) or `./config/contracts` (dev path).

## Required fields

Every contract must include these top-level keys:
- `contract_version`: contract schema version such as `contract/v1.0`
- `version`: semver for the specific agent contract such as `1.0.0`
- `agent`: object with `name`, `role`, `service`, and `summary`
- `description`: human-readable local-first purpose statement
- `input_schema` / `output_schema`: object-shaped JSON-schema-like definitions
- `permissions`: `tools` and `syscalls` allowlists
- `budgets`: `token_budget`, `time_budget_ms`, `max_depth`, `max_memory_mb`
- `verifier_hooks`: one or more deterministic verification stages
- `registration`: handshake + attestation requirements before agent registration

## Validation behavior

Use the offline validator before registering agents:

```bash
python3 services/orchestrator/validate_contracts.py
```

The validator is stdlib-only, deterministic, and rejects malformed JSON, missing required keys, invalid semver, unsafe schema defaults (such as `additionalProperties != false`), unknown tool/syscall categories, non-positive budgets, and duplicate agent names.

## Local-first and security notes

Contracts are plain JSON files so they are easy to audit, diff, and back up locally. That also means they are not encrypted at rest; if a contract contains sensitive pathing or policy details, protect the repository with filesystem permissions and encrypted backups.


## Shared task schema

MVP task intake for the orchestrator uses `task_envelope.v1.json` as the shared wire contract for task routing (`task_id`, `kind`, `content`, `source`, and metadata).
