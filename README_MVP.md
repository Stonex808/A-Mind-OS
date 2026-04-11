# A-Mind-OS

A-Mind-OS is the implementation repo for a local-first, AI-native operating environment inspired by the broader Refocus-OS architecture.

This repository is **not** the full finished operating system. It is the build track that turns the research vision into a practical MVP with:

- a visible shell
- a minimal orchestrator backbone
- planner/worker agent scaffolding
- local memory primitives
- early Hydra safety gates
- scripts, tests, and clear contributor flow

## Project Relationship

### Refocus-OS
Refocus-OS is the long-range architecture and research doctrine:
- agent-centric operating model
- Hydra defense vision
- ArtHippoNet memory architecture
- GRACE retrieval model
- long-term reflection and self-improvement goals

### A-Mind-OS
A-Mind-OS is the implementation track:
- repository structure
- runnable local demo paths
- UI shell and service boundaries
- phased MVP backlog
- practical constraints and tradeoffs

Use Refocus-OS to understand the vision. Use A-Mind-OS to build what can run now.

---

## Current Reality

Right now this repo is best understood as a **local-first developer sandbox moving toward a full MVP**.

### Implemented now
- local orchestrator demo with store/recall flow
- local JSON/SQLite persistence
- memory stack components under `python_core/`
- a static shell prototype under `ui/shell/`
- setup and verification scripts for the offline local path
- contract/schema groundwork under `config/contracts/`

### Partially implemented
- documentation for system layers and subsystem boundaries
- local intent ingress hardening and audit patterns
- repo structure for multi-service expansion

### Planned later
- full planner/worker runtime
- full Hydra service split
- deep SysSec/eBPF monitoring
- full Tauri/React shell
- full reflection and self-improvement loop
- production boot graph and hardened service packaging

The repo already has real pieces. It is just **not** the full Refocus-OS vision yet.

---

## MVP Goal

The MVP should prove six things:

1. the shell is visibly usable
2. the orchestrator can accept and route tasks
3. planner and workers exist in minimal working form
4. memory is stored locally in distinct categories
5. Hydra blocks obvious unsafe prompts and code
6. the repo can be booted and tested without detective work

That is the bar. Not mythical perfection.

---

## Core MVP Priorities

The practical implementation order is tracked in `TASKS.md`.

Current focus:

1. clean app shell and repo framing
2. orchestrator backbone
3. planner/worker MATPO-lite shape
4. ArtHippoNet-lite memory interfaces
5. Hydra MVP
6. UI integration
7. reflection MVP
8. packaging and contributor flow

---

## Repository Map

- `README_MVP.md`  
  Cleaned project framing, current state, quick start, and contributor orientation.

- `ARCHITECTURE_MVP.md`  
  The system structure for A-Mind-OS, with current-vs-planned boundaries.

- `TASKS.md`  
  The phased MVP backlog and immediate implementation priorities.

- `CODEX_PHASE1_2_PROMPT.md`  
  A ready-to-use prompt for Codex Cloud to continue implementation.

- `services/orchestrator/`  
  Current local orchestrator demo path and future orchestrator expansion.

- `python_core/`  
  Local memory and core logic primitives.

- `ui/shell/`  
  Visible offline shell prototype.

- `config/contracts/`  
  Shared schemas and contract groundwork.

- `scripts/`  
  Setup, dev, and verification helpers.

- `systemd/units/`  
  Future boot/deployment direction, not the current day-one path.

---

## Local-First Quick Start

Start with the local path before trying to think like a distributed systems prophet.

### 1. Prepare the repo
Run:

```bash
scripts/setup.sh
```

### 2. Run the local demo
Run:

```bash
scripts/verify-local-demo.sh
```

That is the clearest current validation path.

### 3. Inspect local artifacts
Look at:
- `data/demo/`
- `data/demo/memory/`
- `data/user/memory/`

### 4. Optionally serve the shell prototype
Run a local static server for `ui/shell/` and inspect the visible shell flow.

---

## What A-Mind-OS Is Trying to Become

A-Mind-OS is aiming toward a system where:

- natural language is a primary control surface
- agents replace fragmented app workflows
- orchestration, memory, and safety live near the system core
- the user works through one coherent shell instead of scattered tabs and disconnected tools

The important phrase there is **aiming toward**. The repo should tell the truth about what exists today while still pulling in that direction.

---

## Development Rules

When building this repo, prefer:

- working code over impressive prose
- vertical slices over isolated stubs
- local-first defaults over cloud sprawl
- clear boundaries over premature cleverness
- safety gates over unrestricted execution
- docs that match reality over fantasy roadmaps

---

## Codex Workflow

If you are using Codex Cloud on this repo:

1. read `README_MVP.md`
2. read `ARCHITECTURE_MVP.md`
3. read `TASKS.md`
4. use `CODEX_PHASE1_2_PROMPT.md`
5. implement only the highest-value unfinished parts of the current phase
6. do not rewrite unrelated systems

This repo needs disciplined iteration, not another grand rewrite.

---

## What Is Explicitly Deferred

These matter, but they should not block MVP progress:

- custom Native Hybrid Attention implementation
- full RL-based MATPO training
- eBPF-driven SysSec anomaly detection
- market-based Compute Economist
- full IFN conflict-resolution framework
- self-modifying reflection engine
- production-grade secure multi-service deployment graph

---

## Success Condition

This repository is healthy when a contributor can clone it, run the local path, understand the current architecture, and continue building from `TASKS.md` without guessing what the project actually is.

That sounds basic. It is also where half of ambitious repos die.

---

## License

Apache-2.0 (provisional, adjust if needed).
