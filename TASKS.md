# A-Mind-OS MVP Backlog

This file converts the broader Refocus-OS vision into a practical implementation roadmap for A-Mind-OS.

The goal is to prioritize what can be built and validated now without pretending the full long-range architecture already exists.

---

## Project Framing

### Refocus-OS
- research doctrine
- systems architecture
- long-range design vision

### A-Mind-OS
- implementation track
- runnable MVP
- visible shell and working service boundaries

---

## Current Priority Rule

When choosing what to build next, prefer:

1. runnable code over abstract architecture
2. vertical slices over isolated stubs
3. local-first paths over cloud complexity
4. clear interfaces over premature optimization
5. safety gates over unrestricted execution

---

## Phase 1: Repository and App Shell

### Goals
- establish clean project framing
- make the current state obvious
- ensure the visible shell is runnable
- define service boundaries for future work

### Tasks
- [ ] align README.md with actual MVP implementation goals
- [ ] align ARCHITECTURE.md with current vs planned boundaries
- [ ] add contributor-friendly repo map
- [ ] verify local shell prototype runs cleanly
- [ ] add or improve shell tabs/panels for Chat, Tasks, Files, Logs, Settings
- [ ] add status/health indicators in the shell
- [ ] add smoke test instructions for the shell

### Deliverable
A visible shell and clean documentation that reflect reality instead of only aspiration.

---

## Phase 2: Orchestrator Backbone

### Goals
- create the system spine
- formalize task intake and routing
- establish structured execution logging

### Tasks
- [ ] define shared task schema
- [ ] implement orchestrator service boundary
- [ ] implement task queue or dispatcher
- [ ] add planner role interface
- [ ] add worker registry interface
- [ ] persist structured execution logs
- [ ] add smoke tests for orchestrator task flow

### Deliverable
A minimal orchestrator that can receive a task, route it, log it, and return a result.

---

## Phase 3: Planner and Worker Agents (MATPO-lite)

### Goals
- implement the planner/worker execution shape
- isolate worker context
- avoid pretending RL exists yet

### Tasks
- [ ] create planner agent interface
- [ ] create at least two worker agents
- [ ] isolate worker inputs/outputs
- [ ] add worker result summarization back to planner
- [ ] define simple task delegation flow
- [ ] add tests for planner-to-worker handoff

### Suggested First Workers
- [ ] `research_worker`
- [ ] `code_worker`
- [ ] `memory_worker`

### Deliverable
A working planner/worker architecture without full reinforcement learning.

---

## Phase 4: Memory MVP (ArtHippoNet-lite)

### Goals
- create practical memory interfaces
- separate memory types clearly
- keep persistence local and inspectable

### Tasks
- [ ] define episodic memory interface
- [ ] define semantic memory interface
- [ ] define procedural memory interface
- [ ] implement local persistence for each
- [ ] connect orchestrator logging to episodic memory
- [ ] connect reusable successful flows to procedural memory
- [ ] add tests for storage and recall

### Deliverable
A local-first memory layer with three distinct storage types.

---

## Phase 5: Hydra MVP

### Goals
- create a real safety layer for the MVP
- focus on prompt and code safety first
- defer deep runtime anomaly detection

### Tasks
- [ ] implement LangSec middleware for prompt screening
- [ ] implement CodeSec middleware for generated code screening
- [ ] define SysSec placeholder interface for future work
- [ ] add allowlist-based execution gate
- [ ] add audit logs for blocked and allowed actions
- [ ] add tests for obvious malicious input patterns

### Deliverable
A practical Hydra MVP that can block obvious bad prompts and code before execution.

---

## Phase 6: UI Integration

### Goals
- connect visible UI to real backend services
- stop relying only on mock/static data

### Tasks
- [ ] connect shell to orchestrator endpoints
- [ ] show live task states in UI
- [ ] show logs/events in UI
- [ ] show memory summaries in UI
- [ ] show blocked actions and safety notices in UI
- [ ] add settings panel for local/runtime configuration

### Deliverable
A visible shell backed by actual service data.

---

## Phase 7: Reflection MVP

### Goals
- restore one of the most important missing ideas from Refocus-OS
- allow the system to learn from outcomes in simple ways

### Tasks
- [ ] define success/failure evaluation record
- [ ] log task outcomes consistently
- [ ] generate simple reflection summaries after runs
- [ ] extract reusable steps into procedural memory
- [ ] mark future RL/self-improvement as later phase

### Deliverable
A basic reflection loop that records what worked and what failed.

---

## Phase 8: Packaging and Developer Flow

### Goals
- make the project easier to boot and contribute to
- reduce repo confusion and setup friction

### Tasks
- [ ] add or improve setup scripts
- [ ] add run scripts for shell and services
- [ ] add environment template/config examples
- [ ] add contributor guide
- [ ] add local smoke test script
- [ ] document current limitations clearly

### Deliverable
A repo that other contributors or agents can navigate without guessing.

---

## Explicitly Deferred

These belong to the long-term roadmap, but should not block MVP progress:

- [ ] custom Native Hybrid Attention implementation
- [ ] full RL-based MATPO training
- [ ] eBPF-driven SysSec anomaly detection
- [ ] market-based Compute Economist
- [ ] full IFN conflict-resolution framework
- [ ] self-modifying reflection engine
- [ ] production-grade systemd-secured multi-service boot graph

---

## Suggested Immediate Next Task for Codex

Use this repo task prompt:

> Audit the repository against README.md, ARCHITECTURE.md, and TASKS.md. Then implement only the highest-value unfinished part of Phase 1 and Phase 2 without rewriting unrelated systems. Prefer working shell improvements, orchestrator scaffolding, tests, and documentation accuracy.

---

## Definition of MVP Success

The MVP is successful when all of the following are true:

- the shell is visibly usable
- the orchestrator can accept and route tasks
- planner and workers exist in minimal working form
- memory is stored locally in distinct categories
- Hydra blocks obvious unsafe prompts/code
- logs and outcomes are visible and inspectable
- the repo can be booted and tested without detective work
