# Contracts

**Status:** planned / blueprint only  
**Best contributor on-ramp:** start with the runnable local-first orchestrator demo and shell prototype; use this directory as the place where formal contracts will land once the multi-service runtime is fleshed out.  
**Current repo reality:** this directory currently documents the expected contract shape, but no concrete contract set is checked in yet.

Put semver JSON contracts here. Each contract defines:
- inputs/outputs schema
- permitted tools/syscalls
- budget ceilings
- verifier hooks

The Orchestrator loads contracts from `/etc/refocus/contracts` (system path) or `./config/contracts` (dev path).
