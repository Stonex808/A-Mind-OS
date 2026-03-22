# Contracts

Put semver JSON contracts here. Each contract defines:
- inputs/outputs schema
- permitted tools/syscalls
- budget ceilings
- verifier hooks

The Orchestrator loads contracts from `/etc/refocus/contracts` (system path) or `./config/contracts` (dev path).


Current local-first contract set:
- `envelope.v1.schema.json` — base envelope every message must satisfy.
- `orchestrator.envelope.v1.schema.json` — orchestrator-bound dispatch envelopes.
- `verifier.envelope.v1.schema.json` — verifier requests for schema/policy checks.
- `langsec.envelope.v1.schema.json` — LangSec prompt/context review requests.
- `examples/*.json` — offline valid/invalid fixtures for regression tests.
