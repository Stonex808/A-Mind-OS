# Work Queue

`Main` is the implementation baseline. GitHub issues should hold detailed feature discussion; this file only names the durable sequence so contributors do not invent parallel roadmaps.

## Baseline complete

- [x] One offline store/recall orchestrator path.
- [x] One strict task schema and one planner/worker implementation.
- [x] Local JSON/SQLite persistence with redaction, refusal, and bounded retention.
- [x] Standard-library contract validation, tests, and a single `scripts/verify-repo.sh` gate.
- [x] Generated state removed from version control and superseded MVP docs retired.

## Next slice: admitted IPC

- [ ] Define one signed envelope compatible with the existing task and agent contracts.
- [ ] Require `AdmissionDecision` at the socket boundary before any worker effect.
- [ ] Add replay, expiration, scope-mismatch, and tampering tests.
- [ ] Document the threat model and migration before enabling a non-demo worker.

## Later, in order

- [ ] Wire lifecycle supervision to an OS-process adapter.
- [ ] Add a genuinely sandboxed worker with an explicit capability contract.
- [ ] Integrate a local model runtime behind the same admitted boundary.
- [ ] Implement security services and kernel telemetry before claiming the systemd boot graph works.
- [ ] Replace the static shell only after the backend contract is stable.

Do not start a later item by creating a second orchestrator, memory stack, task schema, test suite, or roadmap document.
