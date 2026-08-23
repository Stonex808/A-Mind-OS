# Canonical Slice A Mainline

**Decision date:** 2026-08-17 HST  
**Repository:** `Stonex808/A-Mind-OS`  
**Governing rule:** **AI proposes. The system records. Stone decides.**

## Canonical lineage decision

Stone selected this repository as the continuing A-Mind implementation lineage. The prior `Main` tip is preserved at `lineage/historical-main-2026-04-11`; it is historical evidence, not the active implementation baseline.

This slice integrates the previously divergent work without collapsing provenance:

- PR #16: TaskEnvelope, orchestrator service boundary, dispatcher, execution logging, smoke-testable MVP spine.
- PR #17: deterministic MATPO-lite planner/worker contracts, bounded worker contexts, shell feed bridge, planner-worker tests.
- PR #18: guarded Slice A project-state placement and fail-closed canonical-source gate.
- Harness v0.1.0: runtime-immutable constitutional kernel, versioned evolvable userland, typed harness lineage/evaluation/promotion/rollback records.
- Refocus ancestry: three retained interfaces only: lifecycle supervision, deterministic tool brokerage, and Compute Economist resource accounting.

The 2026-08-23 maintenance consolidation also retained the unique value from superseded PRs #11 and #15: configurable local persistence, redaction/refusal, retention, strict task validation, and structured task-event logging. Their parallel docs, planner path, and stale tests were deliberately not retained.

## Authority boundary

Selecting the repository resolves the repository-lineage blocker. It does **not** fabricate missing governance state. The Slice A production gate must continue to fail closed until complete current copies of these sources exist:

- `governance/01_AUTHORITY_MATRIX.yaml`
- `governance/02_PROJECT_REGISTRY.yaml`

Fixture extracts remain fixtures and must not be promoted as canonical truth.

## Refocus extraction disposition

### 1. Process Manager -> LifecycleSupervisor

Retain: worker identity, health state, heartbeat supervision, graceful lifecycle semantics, resource visibility.

Do not carry forward yet: direct process spawning/signals as the canonical harness API. The OS-process backend is an implementation adapter behind the lifecycle contract.

### 2. Tool Registry -> ToolBroker

Retain: named tool registration, typed invocation, execution accounting, isolated boundary.

Reject: arbitrary shell strings, `shell=True`, or comments standing in for path enforcement. A tool call requires deterministic scoped admission before the registered callable can execute.

### 3. Compute Economist -> deterministic resource accountant

Retain: explicit token/time/tool/worker ceilings, oversubscription prevention, measurable resource usage.

Refine: budgets are hard constraints, consistent with Harness lexicographic gates. Quality cannot buy its way through a resource ceiling.

## Harness placement

- `python_core/refocus_core/harness_contracts.py`: typed HarnessVersion, HarnessDelta, EvaluationContract, PromotionReceipt, RollbackPointer and lifecycle states.
- `services/orchestrator/harness_runtime.py`: scoped admission, lifecycle supervision, ToolBroker, Compute Economist.
- `tests/test_core.py`: fail-closed tests for scope, budget, health, ingress, and contract behavior.
- `tools/project-state/`: Slice A compiler/source gate remains the project-state truth projection boundary.

## Integration invariant

The planner may propose work. Workers may perform only effects admitted by the deterministic boundary. The system records execution and evidence. No model, worker, evaluator, UI, or active harness promotes itself or silently becomes canonical authority.
