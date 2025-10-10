    # LG‑A LangSec — agents.md

    **Role:** Input Sanitization & Prompt‑Injection Defense  
    **Dependencies:** python >= 3.11, fastapi, lightweight classifier

    ## Execution Plan
    1. Load LangSec model; start `/sanitize` over `langsec.sock`.
2. Return sanitized or rejected message + reason.
3. Unit: `lg_a_langsec.service`, `After=kernel_hook.service lg_c_syssec.service`.

    ## Verification
    - Benign prompts pass
- Injection attempts rejected and logged
