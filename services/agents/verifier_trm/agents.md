# TRM verifier agent

**Status:** planned service. The currently runnable verifier is the deterministic rules boundary in `services/orchestrator/local_demo.py`, and agent contracts are validated by `contract_registry.py`.

Future work may add bounded schema, regex, and logic verification behind the admitted IPC contract. It must not replace or bypass current fail-closed validation, and any third-party dependency must be declared, locked, justified, and tested.

Acceptance requires valid/invalid/depth-limit tests, authenticated registration evidence, and integration into `scripts/verify-repo.sh`.
