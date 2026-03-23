# Orchestrator Service — agents.md

**Status:** implemented now (with a narrower local-first scope than the long-term architecture)  
**Best contributor on-ramp:** run `scripts/dev.sh` or `python3 services/orchestrator/local_demo.py --intent-file ./data/demo/demo-intent.txt` before extending blueprint-only pieces.  
**Current runnable scope:** local intent validation, local JSON/SQLite persistence, deterministic recall, optional local Unix socket demo.  
**Long-term scope:** full IPC bus integration, authenticated agent sessions, MATPO planning, and systemd-managed orchestration.

**Role:** System Orchestrator  
**Dependencies (target architecture):** python >= 3.11, fastapi, uvicorn, py-unix-socket, numpy, systemd (user)

## Execution Plan
1. Keep the local demo path working offline first; it is the reference implementation for today's contributor workflow.
2. Initialize IPC bus at `/run/user/$UID/refocus/orch.sock` (asyncio + FastAPI).
3. Implement Priority Queue + AlphaMonk scheduler using `config/economist.yaml`.
4. Build IFN (weighted averaging + TRM confidence).
5. Implement MATPO planner generating DAG per contract schema.
6. Load & validate agent contracts from `/etc/refocus/contracts`.
7. ed25519 handshake with rotating nonces for agent sessions.
8. Install as `orchestrator.service` with `Restart=always` and `After=lg_a_langsec.service lg_c_syssec.service`.

## Verification
- `scripts/dev.sh` completes a store + recall flow locally.
- `python3 services/orchestrator/local_demo.py --stdin` accepts local intents and persists artifacts.
- Future scope: `/healthz` returns `status: ok`, authenticated socket connections succeed, and contracts load with LG‑A attestation.
