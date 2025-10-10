    # Orchestrator Service — agents.md

    **Role:** System Orchestrator  
    **Dependencies:** python >= 3.11, fastapi, uvicorn, py-unix-socket, numpy, systemd (user)

    ## Execution Plan
    1. Initialize IPC bus at `/run/user/$UID/refocus/orch.sock` (asyncio + FastAPI).
2. Implement Priority Queue + AlphaMonk scheduler using `config/economist.yaml`.
3. Build IFN (weighted averaging + TRM confidence).
4. Implement MATPO planner generating DAG per contract schema.
5. Load & validate agent contracts from `/etc/refocus/contracts`.
6. ed25519 handshake with rotating nonces for agent sessions.
7. Install as `orchestrator.service` with `Restart=always` and `After=lg_a_langsec.service lg_c_syssec.service`.

    ## Verification
    - `/healthz` returns `status: ok`  
- Socket accepts authenticated connections  
- Contracts loaded and attested by LG‑A
