    # LG‑B CodeSec — agents.md

    **Role:** Generated Code Safety Analyzer  
    **Dependencies:** python >= 3.11, tree‑sitter, regex (+ optional policy model)

    ## Execution Plan
    1. Tokenize/parse outputs from code‑producing agents.
2. Match forbidden calls/patterns; score severity.
3. Reject + log unsafe code; expose report endpoint.
4. `lg_b_codesec.service` is required before Orchestrator starts.

    ## Verification
    - Safe code passes with report
- Unsafe code blocked with trace in audit log
