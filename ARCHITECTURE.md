# System Architecture: Refocus-OS

## Core Philosophy
Refocus-OS converts the Linux userspace into a cognitive runtime secured by an intelligent defense fabric. The long-term target is a central nervous system (Message Bus) and a brainstem (Orchestrator) that direct a colony of agents within verifiable security boundaries. Efficiency, modularity, deterministic reasoning, and proactive protection are the design foundations.

## Current Implementation Boundary
Before diving into the target architecture, keep the current repository status in mind:

- **Implemented now:** `services/orchestrator/local_demo.py` provides a runnable local-first orchestrator workflow backed by JSON and SQLite artifacts.
- **Local demo / prototype:** `ui/shell/` provides a visible offline shell prototype in plain HTML/CSS/JS.
- **Planned / blueprint only:** the Hydra security services, the systemd service graph, and the contract registry are documented here but are not yet wired into a complete runnable stack in this repository.

For contributor onboarding, start with the orchestrator demo and shell prototype first. They are offline by default, inspectable on disk, and do not require cloud services.

## Architectural Layers

**Layer 0: Hardware & Kernel**  
A custom Debian base with standard Linux Kernel and eBPF instrumentation. Performance-critical components such as attention kernels, syscall monitors, and integrity verifiers are intended to live at the driver/eBPF level.

**Layer 1: Model Runtime**  
A high-efficiency inference server (vLLM or llama.cpp) is the planned runtime for the foundation model, including quantization, LoRA loading, and batch scheduling.

**Layer 2: Hydra Defense System**  
Implements the Adaptive Integrity Shield. In the target design, it continuously audits agent communications, code outputs, and syscall behaviors through the LangSec, CodeSec, and SysSec guard models.

**Layer 3: IPC Message Bus**  
A Unix-socket-based, schema-validated bus for inter-agent messaging. Each envelope is intended to be versioned, signed, and inspected by the Hydra Defense layer before delivery. Messages include GRACE semantic embeddings for long-term retrieval and audit.

**Layer 4: The Orchestrator & Services**  
The brainstem coordinating system intent, decomposition, and scheduling. The full design fuses user and background inputs into consensus intents, decomposes them into subtasks using MATPO, and manages execution via the Compute Economist.

**Layer 5: Specialist Agents**  
Independent sandboxed workers performing tasks defined by their contracts. Each is intended to operate in a restricted namespace, communicating only through the Message Bus with authenticated envelopes.

**Layer 6: User Interface Layer**  
The long-term UI is a Tauri/React HUD and Terminal for interacting with the Orchestrator, managing budgets, and visualizing security alerts. The currently runnable UI is a simpler static prototype in `ui/shell/`.

## Core Subsystems and Logic Flow

### Orchestrator (`services/orchestrator/`) — implemented now
**Purpose:** Central reasoning and coordination hub.  
**Current state:** The local demo is the main runnable subsystem in this repository. It validates intents against local rules, stores them in local JSON/SQLite-backed memory, and supports deterministic recall without cloud calls.  
**Contributor path:** Run `scripts/dev.sh` first, then inspect `data/demo/` and `data/memory/` before extending the broader orchestrator design.  
**Target components:**
- **Intent Fusion Network (IFN):** Weighted vector fusion of sanitized user/system intents.
- **Planner/Worker Scheduler:** MATPO for task DAG generation and assignment.
- **Compute Economist:** Budgets from `economist.yaml` to optimize token/time.
- **Contract Registry:** Loads & validates semver JSON contracts from `/etc/refocus/contracts`.

### Hydra Defense System (`services/security/`) — planned / blueprint only
**Purpose:** Continuous adaptive protection.  
**Current state:** This area currently consists of design-oriented `agents.md` files for the security layers. No runnable LangSec, CodeSec, SysSec, or kernel-hook services are implemented in this repository yet.  
**Contributor path:** Keep security interfaces in mind, but start by iterating on the local orchestrator path and static shell prototype.  
**Target components:**
- **Kernel Hook Service:** eBPF syscall tracing + ZeroMQ publication.
- **LG-A (LangSec):** Prompt sanitization & injection defense.
- **LG-B (CodeSec):** Code safety validation & vuln scanning.
- **LG-C (SysSec):** Real-time anomaly detection + kill-switch.

### Message Bus & Semantic Spine (`ops/ipc/`) — planned / blueprint only
**Purpose:** Communication backbone + memory reference.  
**Current state:** This remains an architectural direction rather than a fully implemented bus in the repo.  
**Target components:**
- **Envelope Schema:** ID, timestamps, src/dst, verb, payload, signature, budget.
- **GRACE Service:** Embedding index for intents, logs, rationale.

### Specialist Agents (`services/agents/`) — planned / blueprint only
**Purpose:** Contracted workers under verification.  
**Current state:** Repo structure and documentation exist, but the broader multi-agent runtime is not yet implemented end to end.  
**Target components:**
- Tool wrappers; TRM verifier; local task-specific sanity checks.

### Memory & Reflection (`memory/`) — mixed, local-first components exist now
**Purpose:** Context persistence, audit, self-improvement.  
**Current state:** The local demo already persists memory artifacts under `data/memory/`. Broader reflection and semantic-spine capabilities remain part of the long-term architecture.  
**Target components:**
- **NHA Kernels, ArtHippoNet, Reflection Daemon.**

### User Shell (`ui/shell/`) — local demo / prototype
**Purpose:** Visible, low-friction interface for intent capture and status display.  
**Current state:** A static prototype exists today using plain HTML/CSS/JS. It is intentionally simple, offline by default, and useful for validating UI flow before a Tauri/React implementation.  
**Contributor path:** Serve `ui/shell/` locally after running the orchestrator demo so you can evaluate the local-first UX with no hidden setup.  
**Target components:**
- Tauri/React HUD.
- AI Terminal.
- Budget controls and security alerts.
- Global hotkey + voice integrations.

### Systemd Units (`systemd/units/`) — planned / blueprint only
**Purpose:** Secure boot ordering and service packaging.  
**Current state:** The repository includes unit and target templates that express the intended dependency graph, but they are not a complete working deployment of the full stack.  
**Contributor path:** Use these files as references for naming and future ordering, but use `scripts/dev.sh` and a local static server for today's development path.

### Contracts (`config/contracts/`) — planned / blueprint only
**Purpose:** Shared contracts defining inputs, outputs, budgets, and verifier hooks.  
**Current state:** Only a README describing the expected contract shape is present today; a concrete contract set is not yet checked in.  
**Contributor path:** Keep the contract model in mind, but do not block local-first prototyping on a not-yet-populated registry.

### Example Logic Flow: Secure Request
1. Intent Capture → 2. Sanitization → 3. Fusion → 4. Planning → 5. Execution → 6. Monitoring → 7. Verification → 8. Output

This remains the target end-state flow. The current runnable local loop is smaller: validate intent → persist locally → recall locally.

## Security & Integrity Enhancements
- ed25519 agent keys; rotating nonces.
- eBPF syscall whitelists per agent.
- Hash-linked audit chains.
- Attestation: kernel_hook → LG‑C → LG‑A → Orchestrator → Agents → UI.
- Isolation: circuit breakers; quarantine zones.

These remain core design goals. For the implemented local-first path today, the most important practical trade-off is that JSON/SQLite artifacts are easy to inspect and back up but are not encrypted at rest by default.

## Observability
Latency percentiles, token burn, anomaly rates, memory use, verifier pass rates. The future HUD exposes Max Tokens/Time/Depth and Kill All Workers.

In the current implementation, inspect generated JSON run artifacts and SQLite files for observability.

## Data Hygiene
GRACE targets PII redaction, TTLs, hot/warm/cold vector tiers.

Today, data hygiene depends on contributor discipline because local artifacts stay intentionally simple and transparent.

## Boot Targets
`refocus-pre.target` → kernel_hook, LG-C  
`refocus-core.target` → LG-A, Orchestrator  
`refocus-agents.target` → Verifier, Workers  
`refocus-ui.target` → HUD

All units express the intended future dependency graph; they are not yet the recommended day-one developer path.
