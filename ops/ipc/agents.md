# IPC message bus

**Status:** planned. The current Unix socket in `services/orchestrator/local_demo.py` is an unauthenticated demo transport, not the production bus.

The next slice must define one signed envelope, validate it before dispatch, require a scoped `AdmissionDecision`, reject expiration/replay/tampering, and append evidence without leaking sensitive content. Extend `config/contracts/task_envelope.v1.json` and the existing harness seams; do not introduce a competing envelope or dispatcher.

Acceptance belongs in `tests/` and must run through `scripts/verify-repo.sh` before this surface is labeled runnable.
