    # Kernel Hook — agents.md

    **Role:** eBPF Telemetry Provider  
    **Dependencies:** python >= 3.11, bcc/libbpf, pyzmq, CAP_BPF

    ## Execution Plan
    1. Attach eBPF to `execve, openat, connect, sendto, recvfrom, ptrace, setuid, mount`.
2. Publish ZeroMQ topic stream to LG‑C.
3. Maintain per‑agent whitelist map; log violations.
4. Unit: `kernel_hook.service` in `refocus-pre.target`.

    ## Verification
    - Syscalls captured with agent attribution
- Unauthorized call → violation event
