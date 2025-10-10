    # LG‑C SysSec — agents.md

    **Role:** Real‑Time Syscall Anomaly Detection  
    **Dependencies:** python >= 3.11, small time‑series model, kernel hook feed

    ## Execution Plan
    1. Load SysSec model; subscribe to eBPF event stream.
2. Sliding window inference → anomaly score.
3. On threshold, trigger HALT + kill offending agent.
4. `lg_c_syssec.service` starts in `refocus-pre.target`.

    ## Verification
    - Normal sequences score low
- Malicious patterns trigger kill/quarantine
