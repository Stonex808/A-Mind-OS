    # Tiny Recursive Model (TRM) Verifier — agents.md

    **Role:** Pre‑LLM Data Validator  
    **Dependencies:** python >= 3.11, jsonschema, regex

    ## Execution Plan
    1. Implement `verify(data, constraints, depth=0)` with `depth<=3`.
2. Handlers: schema/type/regex/logic.
3. Unix socket: `/run/user/$UID/refocus/verifier.sock`.
4. Publish `verifier_trm.json` contract (semver + schemas).
5. Register with Orchestrator on boot.

    ## Verification
    - Valid inputs → `true`
- Invalid inputs → `false` + reason
- Authenticated handshake with Orchestrator
