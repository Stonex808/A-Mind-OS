# Kernel Hook — agents.md

**Status:** planned / blueprint only  
**Best contributor on-ramp:** start with the runnable local demo first; use this file as the future kernel telemetry contract, not as a ready-to-run component.  
**Current repo reality:** no eBPF/kernel hook implementation is checked in here yet.

**Role:** eBPF Telemetry Provider  
**Dependencies (target architecture):** python >= 3.11, bcc/libbpf, pyzmq, CAP_BPF

## Execution Plan
1. Attach eBPF to `execve, openat, connect, sendto, recvfrom, ptrace, setuid, mount`.
2. Publish ZeroMQ topic stream to LG‑C.
3. Maintain per‑agent whitelist map; log violations.
4. Unit: `kernel_hook.service` in `refocus-pre.target`.

## Verification
- Future scope: syscalls are captured with agent attribution.
- Future scope: unauthorized calls emit violation events.
