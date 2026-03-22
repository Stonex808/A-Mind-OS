# LG‑B CodeSec — agents.md

**Status:** planned / blueprint only  
**Best contributor on-ramp:** treat this as future policy documentation; first validate changes through the runnable local-first orchestrator and shell paths.  
**Current repo reality:** no runnable CodeSec service implementation is present yet.

**Role:** Generated Code Safety Analyzer  
**Dependencies (target architecture):** python >= 3.11, tree‑sitter, regex (+ optional policy model)

## Execution Plan
1. Tokenize/parse outputs from code‑producing agents.
2. Match forbidden calls/patterns; score severity.
3. Reject + log unsafe code; expose report endpoint.
4. `lg_b_codesec.service` is required before Orchestrator starts.

## Verification
- Future scope: safe code passes with a report.
- Future scope: unsafe code is blocked with a trace in the audit log.
