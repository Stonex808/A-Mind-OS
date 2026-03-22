# LG‑C SysSec — agents.md

**Status:** planned / blueprint only  
**Best contributor on-ramp:** begin with the local orchestrator demo and use this file as future-facing documentation for runtime anomaly controls.  
**Current repo reality:** this is a design note only; no runnable SysSec daemon is checked in here yet.

**Role:** Real‑Time Syscall Anomaly Detection  
**Dependencies (target architecture):** python >= 3.11, small time‑series model, kernel hook feed

## Execution Plan
1. Load SysSec model; subscribe to eBPF event stream.
2. Sliding window inference → anomaly score.
3. On threshold, trigger HALT + kill offending agent.
4. `lg_c_syssec.service` starts in `refocus-pre.target`.

## Verification
- Future scope: normal sequences score low.
- Future scope: malicious patterns trigger kill/quarantine.
