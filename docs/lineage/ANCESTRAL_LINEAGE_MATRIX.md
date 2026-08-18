# A-Mind Ancestral Lineage Matrix

**Slice:** ancestral lineage / provenance  
**Created:** 2026-08-17 HST  
**Historical parent:** `lineage/historical-main-2026-04-11` at `180646279109716818285162a94df23d50201fa0`  
**Original former-Main commit:** `abaa1e1b22db5ab5f485197b43006ea3788d7fff`  
**Primary ancestry source:** uploaded `refocus_os_guide.md`, SHA-256 `8028d98a9bdfce7f01a820e6252983173fff7f9fbdcb04c95e180ecb390e25c2`

## Purpose

This slice records architectural ancestry without declaring every ancestor canonical. It separates four questions:

1. Did the idea exist in Refocus-OS documentation?
2. Was a corresponding surface present in historical Main?
3. What is the modern A-Mind equivalent?
4. What is the current disposition?

`canonical` means part of the active architecture/runtime boundary. `interface canonical` means the contract is retained while a production backend remains replaceable. `legacy` means provenance/reference only. `research` means deliberately downstream. `superseded` means a newer mechanism owns the responsibility.

## Matrix

| Refocus ancestor | Refocus evidence / role | Historical Main evidence | New A-Mind equivalent | Disposition |
|---|---|---|---|---|
| Unified logging/config | Shared structured logging and configuration intended for all services | `python_core/refocus_core/logging.py`, `config/refocus-os.toml` | Existing local logging/config plus future observability contracts | **Retained utility / superseded where newer contracts exist** |
| System Monitor | CPU, memory, GPU and per-agent metrics feeding scheduling and debugging | Architecture/config reference exists; no verified complete production monitor in former Main | `LifecycleSupervisor` health state + `ComputeEconomist` accounting; later metrics backend can feed them | **Interface canonical; metrics backend deferred** |
| Process Manager | Spawn, track, heartbeat, terminate and supervise agent processes | Process lifecycle appears primarily as architecture/systemd intent rather than a verified end-to-end manager in former Main | `services/orchestrator/harness_runtime.py::LifecycleSupervisor` | **Interface canonical; OS process adapter deferred** |
| Tool Registry / execution service | Named tools, schemas, execution statistics and worker tool access | Contract/allowlist/security primitives exist, but no safe complete canonical broker was verified | `ToolBroker` requiring scoped deterministic `AdmissionDecision` | **Canonical boundary** |
| Arbitrary shell executor | Refocus guide included a supposedly sandboxed command path using shell execution | Historical security docs emphasize allowlists, but do not make arbitrary shell strings canonical | No equivalent; tool implementations must be registered callables/adapters behind admission | **Rejected legacy implementation** |
| Planner / Worker roles | Planner decomposes/co-ordinates worker work; workers execute bounded tasks | Former Main documents MATPO/planner-worker direction | PR #17 `planner_worker.py` plus PR #16 TaskEnvelope/orchestrator spine | **Canonical MVP runtime** |
| Agent role/message contracts | Planner/Worker roles plus spawn/assign/complete message shapes | Versioned contract directory and orchestrator envelope concepts | TaskEnvelope + PlannerDecision/WorkerRequest/WorkerResult and later typed IPC | **Canonical, progressively typed** |
| Compute Economist | Tracks GPU/CPU/inference resources and prevents oversubscription | `config/economist.yaml` and architecture references | `ComputeEconomist` with hard token/time/tool/worker ceilings | **Canonical runtime seam** |
| Priority scheduling | Priority queue plus age/resource-aware scheduling | Planned architecture, not verified as a complete scheduler in former Main | Task backbone now; richer scheduling remains evolvable Harness control flow under fixed ceilings | **Partial canonical / future M4 evolution** |
| Intent fusion | Orchestrator described as implementing intent fusion before coordination | Former Main architecture names IFN/intent fusion as future work | Deterministic intent gateway/admission before effect; probabilistic fusion may exist upstream | **Concept retained; implementation not yet canonical** |
| Shared-memory IPC | Low-latency Rust/Python metrics exchange | Historical Main contains IPC/message-bus design but no reason to freeze shared memory as universal transport | Replaceable transport behind typed contracts; ACP/MCP/A2A only where boundaries justify them | **Legacy mechanism, contract concept retained** |
| Structured audit / traces | Services log activity and metrics for inspection | `python_core/refocus_core/audit.py`, local JSON/SQLite artifacts | Append-first execution evidence; Harness PromotionReceipt/trace lineage | **Canonical principle; implementation hardening ongoing** |
| Self-improvement traces | MATPO traces and later reflection intended to support improvement | Reflection/NHA/ArtHippoNet appear as roadmap concepts | HarnessVersion/HarnessDelta + isolated evaluation + Stone promotion | **Superseded by governed Harness evolution model** |
| Hydra Defense System | eBPF + LangSec/CodeSec/SysSec layered security roadmap | `services/security/*`, `systemd/units/*` are design-oriented surfaces | Capability/admission kernel now; Hydra remains a possible deeper defense layer | **Research / later implementation** |
| ArtHippoNet memory | Planned later memory system | Memory modules exist, but ArtHippoNet itself is roadmap-level | A-Mind memory/Librarian contracts and MemoryMutationContract lineage | **Legacy research ancestor** |
| Reflection & Self-Improvement phase | Planned after memory/security layers | Reflection is architectural rather than proven autonomous evolution | `RP-01R-H` bounded Harness evolution, no self-promotion | **Research governed by Harness** |
| OS-kernel-like Orchestrator | Refocus guide explicitly treats orchestrator as system brain/kernel coordinating agents/resources | Former Main places Orchestrator at the center of the intended runtime | Native A-Mind Harness: orchestrator + planner/workers + lifecycle + admitted tools + deterministic governance boundary | **Canonical architectural lineage** |

## Major lineage transitions

```text
Refocus-OS architecture/build guide
    |
    +-- monitoring + process lifecycle + tool registry + planner/workers + economist
    |
Historical A-Mind-OS / former Main
    |
    +-- local-first memory, contracts, audit/security primitives, orchestrator blueprint
    |
    +-- PR #16: TaskEnvelope + dispatcher + service/logging spine
    +-- PR #17: explicit planner/worker runtime + shell feed
    +-- PR #18: guarded Slice A project-state source gate
    |
Canonical Slice A Mainline (2026-08-17)
    |
    +-- runtime-immutable constitutional Harness boundary
    +-- typed harness lineage/promotion/rollback records
    +-- LifecycleSupervisor
    +-- admitted ToolBroker
    +-- ComputeEconomist hard resource ceilings
```

## What did not cross the boundary

The ancestry is evidence, not a cargo cult. The following are deliberately not promoted merely because they appeared earlier:

- arbitrary `shell=True` tool execution;
- comments in place of actual filesystem policy enforcement;
- claims that prototype components are production-ready without current tests/evidence;
- shared memory as a mandatory universal IPC choice;
- Hydra, ArtHippoNet, NHA, or autonomous self-improvement as completed features;
- any fixture, partial Matrix, or partial Registry as canonical governance truth.

## Provenance rule

Future lineage edits should append evidence and refine dispositions. They should not rewrite an ancestor to make it look more modern than it was. When an old concept resembles a modern one, record the relationship as ancestry, convergence, or supersession and preserve the differences.
