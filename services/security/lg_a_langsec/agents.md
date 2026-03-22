# LG‑A LangSec — agents.md

**Status:** planned / blueprint only  
**Best contributor on-ramp:** do not start here first; begin with the local orchestrator demo in `services/orchestrator/local_demo.py`, then use this file as an interface sketch for future sanitization work.  
**Current repo reality:** this folder documents the intended service behavior only. No runnable LangSec daemon is checked in here yet.

**Role:** Input Sanitization & Prompt‑Injection Defense  
**Dependencies (target architecture):** python >= 3.11, fastapi, lightweight classifier

## Execution Plan
1. Load LangSec model; start `/sanitize` over `langsec.sock`.
2. Return sanitized or rejected message + reason.
3. Unit: `lg_a_langsec.service`, `After=kernel_hook.service lg_c_syssec.service`.

## Verification
- Future scope: benign prompts pass.
- Future scope: injection attempts are rejected and logged.
