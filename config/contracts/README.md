# Contracts

Put semver JSON contracts here. Each contract defines:
- inputs/outputs schema
- permitted tools/syscalls
- budget ceilings
- verifier hooks

The Orchestrator loads contracts from `/etc/refocus/contracts` (system path) or `./config/contracts` (dev path).
