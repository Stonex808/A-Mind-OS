# Security Policy

A-Mind-OS is pre-production research software. The runnable path is offline and intentionally does not execute shell commands, call external services, or claim that the planned Hydra/eBPF layers exist.

## Current safeguards

- Verifier configuration and typed task envelopes fail closed.
- Local persistence defaults to obvious-secret redaction; `REFOCUS_SENSITIVE_CONTENT_MODE=refuse` blocks the write entirely.
- Runtime state is ignored by Git and tests use temporary directories.
- Future tool calls have explicit allowlist, admission, audit, and resource-budget primitives.
- The required local path uses only Python 3.11+ standard-library modules, so there is no lockfile or dependency-update queue for this repository.

These safeguards do not provide encryption at rest, comprehensive secret detection, authenticated IPC, sandboxing, malware detection, or tamper-evident logs. Use encrypted storage for personal data and do not expose the demo socket to untrusted users.

## Reporting a vulnerability

Do not publish credentials or exploit details in a public issue. Use GitHub's private vulnerability-reporting flow on the repository Security tab when available; otherwise contact the repository owner privately and provide the affected revision, reproduction, impact, and suggested containment.

## Dependency policy

Do not add a package manager or dependency merely for convenience. A dependency change must include a committed manifest and lockfile where the ecosystem supports one, a reason it is needed, and verification in the same focused change. Lockfiles are reproducibility records and should be updated by the package manager, not edited by hand or deleted to silence an alert.
