# Refocus-OS

**Vision**  
Refocus-OS is a research repository for an AI-first, agent-centric operating system layer built around a custom Debian base. Today, this repository is primarily a design/specification repo with one local Python memory subsystem you can run and inspect offline. The full orchestrated OS, security pipeline, message bus, and desktop UI described below are not wired into a working end-to-end platform yet.

---

## Current State

What is actually implemented in this repository today:

- **Architecture and subsystem specs** for the intended operating-system design live in `ARCHITECTURE.md`, `services/**/agents.md`, `ops/ipc/agents.md`, `memory/grace/agents.md`, and the systemd unit files.
- **A runnable local Python memory package** lives in `python_core/` and implements episodic, semantic, and procedural memory primitives through the `ArtHippoNet` interface.
- **Local persistence** for the Python memory stack is implemented using JSON files under `./data/memory/**`, plus local Chroma persistence when its dependency is installed.
- **A demo/test entry point** exists at `python_core/test_complete_memory.py` to exercise the current memory stack locally.
- **Bootstrap/dev helper scripts** exist in `scripts/`, but `scripts/dev.sh` is a placeholder runner that prints the intended startup sequence rather than launching a complete platform.
- **Configuration scaffolding** exists in `config/` for future orchestrator, model runtime, and security settings.

If you are evaluating this repo for trustworthiness, the safest summary is: **the memory subsystem is the main runnable implementation; most other areas are blueprints, contracts, or boot-time scaffolding.**

---

## What is still a blueprint

The following parts are described in the repository but are **not** implemented here as a complete, integrated system yet:

- **Orchestrator:** planning, intent fusion, scheduling, agent coordination, and economist-style resource management are documented, but there is no working orchestrator service implementation in `services/orchestrator/` yet.
- **IPC / message bus:** signed envelopes, schema-validated bus traffic, and GRACE-backed semantic routing are specified in `ops/ipc/`, but there is no production-ready Unix-socket bus implementation in this repo.
- **Security layers:** LangSec, CodeSec, SysSec, and kernel-hook components are documented under `services/security/` and represented in `systemd/units/`, but the repository currently provides specifications rather than an operational defense stack.
- **UI / end-user shell:** the HUD, AI Terminal, hotkeys, and voice-control workflow are described under `ui/shell/`, but there is no shipped Tauri/React application in this repository yet.

Because of that, references to hotkeys, silent background agents, secure startup chains, or verified end-to-end request handling should be read as **target architecture**, not as behavior you can expect from the repository today.

---

## Core Principles

### Agent-Centric Architecture
The planned system treats each capability as an autonomous agent with a defined contract and schema. The intended design has agents coordinate through an orchestrator and operate under security supervision.

### Long-Context, Low-Compute
The architecture targets long-context inference techniques such as **Native Hybrid Attention (NHA)** to support persistent context efficiently.

### Single-Model, Multi-Role Delegation
The design proposes using a single foundation model for multiple roles (Planner, WebAgent, Verifier, etc.) through specialized prompts and toolsets.

### Secure by Design
The target platform includes an **Adaptive Integrity Shield** with **LangSec**, **CodeSec**, and **SysSec** layers.

### Quiet, Headless Operation
The intended user experience is headless-first with lightweight visibility through a HUD and terminal-style controls.

### Verifiable and Self-Improving
The roadmap includes deterministic logs, signed envelopes, replay data, and reflection loops for policy refinement.

---

## System Architecture (Planned)

See **ARCHITECTURE.md** for the fuller design document. At a high level, the repository proposes:

- **Layer 0 – Hardware & Kernel:** Debian base + Linux kernel + eBPF instrumentation.
- **Layer 1 – Model Runtime:** local inference server with quantization, adapters, and batching.
- **Layer 2 – Hydra Defense System:** LangSec / CodeSec / SysSec.
- **Layer 3 – IPC Message Bus:** Unix-socket bus with signed envelopes and validation.
- **Layer 4 – Orchestrator & Services:** planning, budgeting, routing, and service registry.
- **Layer 5 – Specialist Agents:** sandboxed workers with explicit contracts.
- **Layer 6 – UI Layer:** HUD, AI Terminal, hotkeys, and voice controls.

This section describes the **planned stack**, not a fully working implementation currently available in the repo.

---

## Repository Layout

- **services/orchestrator/** – Orchestrator design notes and agent instructions.
- **services/security/** – Security-layer design notes for LangSec, CodeSec, SysSec, and kernel hooks.
- **services/agents/** – Specialist-agent documentation such as `verifier_trm`.
- **ops/ipc/** – Message-bus and envelope design notes.
- **memory/grace/** – GRACE memory/audit architecture notes.
- **python_core/** – The main currently runnable code: ArtHippoNet memory components and demo script.
- **ui/shell/** – UI/HUD design notes.
- **config/** – TOML/YAML configuration scaffolding.
- **systemd/units/** – Unit and target definitions for the intended boot graph.
- **scripts/** – Local helper scripts; setup is real, dev runner is currently illustrative.

---

## Quickstart for the runnable local pieces

This quickstart only covers the parts that are currently runnable from this repository.

### 1) Check local tool availability

```bash
./scripts/setup.sh
```

What this does today:
- confirms whether `python3` is installed;
- reports optional `node` and `cargo` availability;
- does **not** install or launch the full platform.

### 2) Install the Python memory dependencies

Create a local virtual environment if you want isolation, then install the packages used by the memory demo:

```bash
pip install chromadb sentence-transformers
pip install structlog  # optional, enables structured logs
```

Privacy/security notes:
- The code configures Chroma with `anonymized_telemetry=False`, so it is intended to stay local-first.
- `SentenceTransformer('all-MiniLM-L6-v2')` may download model weights the first time you run it. Cache those files locally for later offline reuse.
- Data written under `./data/memory/` is plain local storage. Back it up like normal application data, and encrypt the host volume if the stored memories are sensitive.

### 3) Run the local memory demo

```bash
python -m python_core.test_complete_memory
```

This exercises the implemented memory stack:
- episodic storage;
- semantic fact learning;
- procedural extraction;
- integrated recall;
- local statistics reporting.

### 4) Optional: inspect the placeholder dev script

```bash
./scripts/dev.sh
```

This currently prints the intended service startup order. It is useful for understanding the target boot flow, but it does **not** start a working orchestrator/security/UI stack.

---

## Boot Targets (planned systemd graph)

The repository includes unit files that describe the intended boot order:

- `refocus-pre.target` → `kernel_hook.service`, `lg_c_syssec.service`
- `refocus-core.target` → `lg_a_langsec.service`, `orchestrator.service`
- `refocus-agents.target` → `verifier_trm.service`, workers
- `refocus-ui.target` → HUD

These units are useful as architecture scaffolding, but they should not be read as proof that those services are fully implemented in this repository.

---

## Development Workflow

- **Contracts first:** define and review JSON contracts in `config/contracts/`.
- **Memory implementation:** extend the runnable Python memory modules in `python_core/`.
- **Architecture work:** use the service, IPC, and UI directories to evolve specs into concrete implementations.
- **Security hygiene:** keep data local, avoid checking secrets into config files, and treat `./data/memory/` as sensitive if it stores real user material.

---

## Roadmap

| Milestone | Scope | Concrete repo locations |
| --- | --- | --- |
| M1 | Stabilize the current local memory subsystem and persistence model | `python_core/memory/`, `python_core/test_complete_memory.py`, `config/` |
| M2 | Turn IPC/bus specifications into a minimal working local message bus | `ops/ipc/`, `config/contracts/` |
| M3 | Implement an actual orchestrator service around the existing contracts | `services/orchestrator/`, `systemd/units/orchestrator.service` |
| M4 | Convert security-layer specs into runnable local services and enforcement hooks | `services/security/`, `systemd/units/lg_a_langsec.service`, `systemd/units/lg_c_syssec.service`, `systemd/units/kernel_hook.service` |
| M5 | Ship a visible local UI/HUD tied to the implemented services | `ui/shell/`, `systemd/units/hud.service` |

---

## Contributing

PRs are welcome. The most helpful contributions right now are the ones that:

- tighten the README and architecture docs so implemented vs planned work is obvious;
- add tests or packaging around `python_core/`;
- turn one blueprint area at a time into a small, local-first implementation.

---

## License

Apache-2.0 (provisional; update as needed).
