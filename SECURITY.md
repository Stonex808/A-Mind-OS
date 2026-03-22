# Security Posture

Refocus-OS is currently a **local-first blueprint with a small set of concrete Python security primitives**. This document separates what is implemented now from what is still planned so the repository does not overstate its current protections.

## Scope and threat model

### Implemented now
- **Local-only security helpers in `python_core/refocus_core/`:**
  - strict schema validation for incoming user-intent payloads,
  - conservative local text sanitization,
  - explicit allowlist checks for any future tool/command execution path,
  - structured audit storage in local JSONL or SQLite.
- **No cloud dependency is required** for these protections. They are stdlib-only and work offline.
- **Audit storage stays on the local machine by default** under paths you choose, such as `./data/audit/audit.jsonl` or `./data/audit/audit.db`.

### Not implemented yet
- No running orchestrator service, IPC authentication layer, or signed envelope transport.
- No active eBPF monitor, syscall enforcement, or kernel attestation.
- No code-analysis daemon, verifier service, or quarantine automation.
- No key management, nonce rotation, or tamper-evident audit chain.

## Current guarantees

### Implemented now
- **Intent ingress hardening:** user intents can be normalized, sanitized, schema-validated, and rejected early if malformed or unsafe for downstream processing.
- **Execution gating:** any future execution path can be denied by default until a tool or command is explicitly allowlisted.
- **Structured auditability:** accept/reject decisions are written locally as structured records.
- **Offline-friendly operation:** the security primitives avoid telemetry, cloud calls, or hidden services.

### Planned later
- Cryptographic message authentication between agents.
- Runtime enforcement of per-agent capabilities at the bus and kernel layers.
- Signed or hash-linked audit chains.
- Automatic rollback, quarantine, and kill-switch workflows.

## Security areas: implemented now vs planned later

### LangSec
**Implemented now**
- Local intent sanitization removes control characters, normalizes Unicode, trims repeated whitespace, enforces size limits, and flags suspicious prompt-injection phrases.
- Schema validation enforces required fields and limits metadata size/content before an intent reaches planning logic.

**Planned later**
- Dedicated LangSec service over a local socket.
- Multi-stage prompt-injection detection and policy scoring.
- Context-aware redaction and richer policy packs.

### CodeSec
**Implemented now**
- No active code scanner exists today.
- The current concrete protection is architectural: any future code-executing tool path should be wrapped behind explicit allowlists and audit logging.

**Planned later**
- Static analysis of generated code.
- Policy checks for forbidden imports, dangerous APIs, and secret handling.
- Verification reports attached to execution artifacts.

### SysSec
**Implemented now**
- No syscall monitor or enforcement agent is running.
- The repository only provides documentation and service placeholders for this layer.

**Planned later**
- Local syscall/event ingestion.
- Anomaly scoring and response actions.
- Kill-switch integration with the orchestrator.

### eBPF monitoring
**Implemented now**
- Not implemented.

**Planned later**
- eBPF probes for a constrained set of security-relevant events.
- In-kernel filtering and low-overhead export to a local consumer.
- Operational benchmarks documenting overhead and fallbacks.

### Verifier behavior
**Implemented now**
- No verifier daemon is active.
- There is no runtime proof that outputs are safe or correct.

**Planned later**
- A dedicated verifier service.
- Policy-backed approval/rejection of high-risk outputs.
- Replayable evidence bundles for operator review.

## Earliest ingestion protections

The first concrete protections should be applied at the **user-intent ingress boundary**, before planning, retrieval, or execution decisions:

1. **Schema validation** rejects malformed payloads.
2. **Input sanitization** normalizes text and strips unsafe control characters.
3. **Suspicion flags** mark likely prompt-injection content for later policy decisions.
4. **Audit logging** records accepted and rejected intents locally.

Reference implementation:
- `python_core/refocus_core/intent_security.py`
- `python_core/refocus_core/audit.py`

## Future execution policy requirements

Any future command or tool execution path must satisfy all of the following:

1. **Default deny:** no command or tool may run without an explicit allowlist entry.
2. **Structured request shape:** execution requests must declare actor, action type, action name, arguments, and linked intent where available.
3. **Audit before/at decision time:** approvals and rejections must be recorded locally.
4. **No secret logging:** logs should record argument keys and policy context, not raw secrets.
5. **Local-first persistence:** audit records remain on-device unless an operator exports them.

## Audit storage, retention, and backups

### Storage formats
- **JSONL**
  - Pros: human-readable, easy to diff, easy to back up with standard file tools.
  - Cons: weaker queryability, easier to modify accidentally, no built-in indexing.
- **SQLite**
  - Pros: single local file, transactional writes, easier querying/filtering.
  - Cons: less human-readable, backups should respect file consistency.

### Retention guidance
- Keep **shorter retention** for high-volume event logs to reduce exposure if the host is compromised.
- Keep **longer retention** only for security-relevant allow/deny events, incident response, and user-visible audit trails.
- Review logs for accidental sensitive data; the current implementation intentionally stores summaries and argument keys rather than raw payload dumps when possible.

### Backup trade-offs
- Backing up JSONL or SQLite makes incident review easier but also duplicates sensitive metadata.
- Prefer encrypted local backups or full-disk-encrypted volumes.
- If backups are copied to removable media, treat the media as sensitive because audit trails can reveal behavior, file paths, and operator habits.

## Non-goals for the current repository state

- Claiming kernel-level enforcement before it exists.
- Claiming cryptographic attestation or signed envelopes before implementation.
- Claiming that verifier layers guarantee output correctness today.
- Sending audit or security telemetry to third-party services.

## Near-term security milestones

1. Wire the intent ingress hooks into a real local orchestrator endpoint.
2. Add policy-driven secret redaction to audit logs.
3. Implement a minimal CodeSec scanner for generated code.
4. Add a local verifier process with explicit decision records.
5. Prototype eBPF collection with measured overhead and opt-in deployment.
6. Add tamper-evident local audit chaining.

## Reporting vulnerabilities

This project does not yet publish a dedicated disclosure channel. Until one exists, treat the repository as pre-production and avoid relying on undocumented security properties.
