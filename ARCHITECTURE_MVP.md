# A-Mind-OS Architecture

This document describes the implementation-facing architecture for A-Mind-OS.

Refocus-OS remains the broader systems doctrine. A-Mind-OS is the practical build track that turns those ideas into a local-first MVP.

The key rule for reading this file is simple:

- **current** means it exists in some runnable or inspectable form in this repo
- **planned** means it belongs to the target architecture, not the present implementation

---

## 1. Architecture Purpose

A-Mind-OS is being built as a personal AI operating environment where:

- a unified shell replaces scattered tool-hopping
- an orchestrator becomes the execution spine
- planner and worker agents handle bounded tasks
- memory is structured instead of improvised
- safety checks happen before execution, not only after damage

This is not yet a full AI-native operating system. It is an MVP track moving toward one.

---

## 2. Current Implementation Boundary

### Current
- local orchestrator demo path
- local JSON/SQLite persistence
- memory primitives in `python_core/`
- static shell prototype in `ui/shell/`
- setup/dev/verification scripts
- contract groundwork in `config/contracts/`

### Planned
- full orchestrator service graph
- planner/worker runtime across bounded services
- dedicated Hydra LangSec/CodeSec/SysSec services
- deeper IPC/message bus layer
- Tauri/React production shell
- reflection loop and self-improvement path
- hardened deployment/runtime packaging

This boundary matters because the repo should stay honest.

---

## 3. Architectural Principles

### Local-first by default
The primary build path should run locally and remain inspectable on disk.

### Vertical slices beat disconnected stubs
A thin end-to-end path is more valuable than ten elegant dead ends.

### Safety before autonomy
Prompt, code, and execution gates should exist before worker freedom expands.

### Clean boundaries
Each subsystem should have a clear role, interface, and failure surface.

### Docs must match reality
If a subsystem is planned, say planned. Do not cosplay completion.

---

## 4. Layered System View

## Layer 0: Base System
**Status:** planned

The long-range target is a Linux-based substrate with deeper system integration. For the MVP, assume a normal local development environment rather than a custom OS image.

**Near-term role:**
- local machine runtime
- file system access
- process execution for demos and future services

---

## Layer 1: Model Runtime
**Status:** planned / partial by abstraction

The architecture assumes a model runtime will eventually sit behind the orchestrator. For MVP purposes, this should be treated as a replaceable runtime boundary rather than a solved problem.

**Target role:**
- local or fallback model execution
- prompt routing
- bounded inference interfaces
- future batching and performance controls

**Do not block MVP on:**
- custom model architecture work
- NHA implementation
- advanced inference optimization research

---

## Layer 2: Hydra Safety Layer
**Status:** early / partial

Hydra is one of the core differentiators, but the full vision is not implemented yet.

### Hydra MVP should include
- LangSec-style prompt screening
- CodeSec-style code screening
- allowlist-based execution control
- structured audit logs for allowed and blocked actions

### Hydra later can include
- SysSec runtime anomaly detection
- kernel/eBPF hooks
- verifier daemons
- broader quarantine and kill-switch behavior

For MVP, Hydra should be a **real gate**, not just a pretty diagram.

---

## Layer 3: Contracts and IPC Boundary
**Status:** partial

The repo already contains schema groundwork. The full message bus is still future-facing.

### Near-term role
- shared task/envelope schemas
- clear service input/output contracts
- orchestrator-to-worker handoff structures
- validation before execution

### Later role
- authenticated envelopes
- richer message bus behavior
- broader multi-service communication fabric

For now, treat contracts as the source of truth for service boundaries.

---

## Layer 4: Orchestrator Backbone
**Status:** partial, highest-priority growth area

The orchestrator is the spine of A-Mind-OS.

### Current role
- local demo path for validated intent storage and recall
- seed for structured execution flow

### MVP target role
- receive tasks
- validate and normalize task input
- delegate to planner
- route work to workers
- persist execution logs
- return results to the shell

### Later role
- richer Intent Fusion behavior
- Compute Economist logic
- more advanced routing and budgeting

If the repo grows one subsystem next, this should be it.

---

## 5. Agent System

**Status:** planned / MVP next-step

The target shape is planner + workers. The MVP version should be MATPO-lite rather than fake sci-fi.

### Planner
The planner handles:
- top-level task interpretation
- subtask decomposition
- worker selection
- result synthesis

### Workers
Workers handle bounded execution in isolated contexts.

### Recommended first workers
- `research_worker`
- `code_worker`
- `memory_worker`

### MVP requirement
- explicit planner interface
- explicit worker registry
- context isolation
- summarized worker results returned to planner

### Not required yet
- RL training
- true MATPO optimization
- self-improving agent policy loops

---

## 6. Memory System (ArtHippoNet-lite)

**Status:** partial foundation exists, architecture still expanding

Memory should be treated as three distinct categories, not one random pile.

### Episodic memory
Stores:
- runs
- sessions
- outcomes
- execution history

### Semantic memory
Stores:
- learned facts
- retrieved knowledge
- summarized references
- durable context

### Procedural memory
Stores:
- reusable workflows
- successful action patterns
- repeatable task recipes

### MVP requirement
- separate interfaces for all three
- local persistence
- orchestrator logs feeding episodic memory
- successful flows feeding procedural memory

The system starts becoming intelligent when it stops forgetting useful structure.

---

## 7. UI Shell

**Status:** current prototype exists

The shell is the visible face of the system.

### Current
- static offline prototype in `ui/shell/`

### MVP target
- tabs or panels for Chat, Tasks, Files, Logs, Settings
- visible task state
- visible safety notices
- visible memory summaries
- visible service health indicators

### Later
- Tauri/React packaging
- richer terminal features
- hotkeys, voice, and deeper runtime controls

The UI should not just look clever. It should reveal what the system is actually doing.

---

## 8. Reflection Loop

**Status:** planned, important, currently missing as a real subsystem

This is one of the major ideas that should return to the implementation track.

### MVP reflection should do
- record success/failure outcomes
- summarize what worked
- summarize what failed
- extract reusable steps into procedural memory

### Later reflection can do
- policy tuning
- richer scoring
- self-improvement loops
- research-grade adaptation

Without reflection, the system can act. It cannot meaningfully evolve.

---

## 9. Current MVP Flow

The MVP flow should look like this:

1. user submits a task from the shell
2. input passes through Hydra MVP gates
3. orchestrator validates and normalizes the task
4. planner decides whether to answer directly or delegate
5. worker executes bounded work
6. result returns to planner
7. orchestrator logs the run
8. memory is updated
9. shell displays result, logs, and safety status

That is the backbone worth building now.

---

## 10. Immediate Implementation Order

Use `TASKS.md` as the operational source of truth.

Recommended order:

1. shell cleanup and repo framing
2. orchestrator backbone
3. planner/worker interfaces
4. memory MVP
5. Hydra MVP
6. UI integration
7. reflection MVP
8. packaging and contributor ergonomics

---

## 11. Explicitly Deferred

The following belong to the long-range vision and should not stall the MVP:

- Native Hybrid Attention implementation
- full RL-based MATPO
- eBPF SysSec anomaly detection
- market-based Compute Economist
- full Intent Fusion conflict logic
- self-modifying reflection engine
- hardened production boot graph

---

## 12. Architecture Success Condition

A-Mind-OS architecture is in good shape when:

- the current boundary is obvious
- the next subsystem to build is obvious
- the planner/worker/memory/safety path is obvious
- contributors do not have to reverse-engineer the repo's identity from scattered files

That is the whole game here: less fog, more spine.
