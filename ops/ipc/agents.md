    # IPC Message Bus & Envelope Schema — agents.md

    **Role:** Signed Message Transport & Semantic Spine  
    **Dependencies:** python >= 3.11, pydantic, nacl (ed25519), sqlite or lite index

    ## Execution Plan
    1. Define `Envelope v1`: id, ts, src, dst, verb, payload, sig, budget.
2. Validate at ingress; forward only after LG‑A/LG‑C stamps.
3. Integrate GRACE: `/embed`, `/search`, `/log_and_embed` hooks.
4. Provide idempotent replay buffer for audits.

    ## Verification
    - Envelopes verify signature
- Replay reproduces outputs deterministically
