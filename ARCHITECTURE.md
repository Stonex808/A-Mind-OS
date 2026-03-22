# System Architecture: Refocus-OS

## Core Philosophy
Refocus-OS is currently a blueprint for a cognitive runtime secured by a layered defense fabric. The repository already includes local-first intent-ingress security hooks, concrete envelope schemas, and structured local audit storage, while the broader Message Bus, full Orchestrator runtime, and kernel-level defenses remain planned. Efficiency, modularity, deterministic reasoning, and proactive protection are the design foundations.

## Current Implementation Boundary
Before diving into the target architecture, keep the current repository status in mind:

- **Implemented now:** `services/orchestrator/local_demo.py` provides a runnable local-first orchestrator workflow backed by JSON and SQLite artifacts.
- **Implemented now:** `config/contracts/` contains versioned envelope JSON Schemas plus fixtures and a validator workflow.
- **Local demo / prototype:** `ui/shell/` provides a visible offline shell prototype in plain HTML/CSS/JS.
- **Planned / blueprint only:** the Hydra security services, the systemd service graph, and most of the broader multi-agent runtime are documented here but are not yet wired into a complete runnable stack in this repository.

For contributor onboarding, start with the orchestrator demo and shell prototype first. They are offline by default, inspectable on disk, and do not require cloud services.

## Architectural Layers

**Layer 0: Hardware & Kernel (planned)**  
A custom Debian base with standard Linux Kernel and prospective eBPF instrumentation. Performance-critical components such as attention kernels, syscall monitors, and integrity verifiers are architectural goals, not current repository features.

**Layer 1: Model Runtime (planned)**  
A high-efficiency inference server (vLLM or llama.cpp) is the planned runtime for the foundation model, including quantization, LoRA loading, and batch scheduling.

**Layer 2: Hydra Defense System (partially planned)**  
The current repository implements only the earliest local security hooks: intent sanitization/schema validation, structured local auditing, and explicit execution allowlists. Dedicated LangSec, CodeSec, and SysSec services remain planned.

**Layer 3: IPC Message Bus (planned)**  
A Unix-socket-based, schema-validated bus for inter-agent messaging is planned. Versioned, signed envelopes and Hydra inspection are design targets rather than implemented features.

**Layer 4: The Orchestrator & Services (planned)**  
The future orchestrator will fuse user and background inputs into consensus intents, decompose them into subtasks using MATPO, and manage execution via the Compute Economist. Today, only the local demo workflow and execution-policy primitives are implemented.

**Layer 5: Specialist Agents (planned)**  
Independent sandboxed workers performing tasks defined by their contracts. Each is intended to operate in a restricted namespace, communicating only through the Message Bus with authenticated envelopes.

**Layer 6: User Interface Layer (mixed)**  
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
- **Contract Registry:** Loads & validates semver JSON contracts from `/etc/refocus/contracts` or the developer mirror in `config/contracts/`, beginning with `config/contracts/envelope.v1.schema.json` and service-specific schemas.
- **Implemented now:** local intent ingress validation/sanitization hooks live in `python_core/refocus_core/intent_security.py` and can be wired into an eventual orchestrator endpoint.
- **Implemented now:** the local demo persists run artifacts and memory locally for deterministic replay and inspection.

### Hydra Defense System (`services/security/`) — planned / blueprint only
**Purpose:** Continuous adaptive protection.  
**Current state:** This area currently consists of design-oriented `agents.md` files for the security layers. No runnable LangSec, CodeSec, SysSec, or kernel-hook services are implemented in this repository yet.  
**Contributor path:** Keep security interfaces in mind, but start by iterating on the local orchestrator path and static shell prototype.  
**Target components:**
- **Kernel Hook Service:** eBPF syscall tracing + local publication.
- **LG-A (LangSec):** Prompt sanitization & injection defense.
- **LG-B (CodeSec):** Code safety validation & vulnerability scanning.
- **LG-C (SysSec):** Real-time anomaly detection + kill-switch.

### Message Bus & Semantic Spine (`ops/ipc/`) — planned / blueprint only
**Purpose:** Communication backbone + memory reference.  
**Current state:** This remains an architectural direction rather than a fully implemented bus in the repo.  
**Target components:**
- **Envelope Schema:** `config/contracts/envelope.v1.schema.json` defines ID, timestamps, src/dst, verb, payload, signature, budget, and `schema_version`. Dispatch-specific constraints live in `config/contracts/orchestrator.envelope.v1.schema.json`, `config/contracts/verifier.envelope.v1.schema.json`, and `config/contracts/langsec.envelope.v1.schema.json`.
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

### Contracts (`config/contracts/`) — mixed
**Purpose:** Shared contracts defining inputs, outputs, budgets, and verifier hooks.  
**Current state:** Concrete local envelope schemas, fixtures, and validation tooling now exist, while broader contract coverage remains incomplete.  
**Contributor path:** Build against the checked-in schemas first, then extend the registry incrementally without blocking the local-first workflow.

### Example Logic Flow: Secure Request
1. Intent Capture → 2. **Implemented now:** local sanitization/schema validation + audit → 3. **Planned later:** fusion → 4. **Planned later:** planning → 5. **Implemented now for future execution paths:** allowlist gate + audit → 6. **Planned later:** monitoring → 7. **Planned later:** verification → 8. **Planned later:** output

This remains the target end-state flow. The current runnable local loop is smaller: validate intent → persist locally → recall locally.

## Security & Integrity Enhancements
**Implemented now**
- Local intent sanitization and schema validation.
- Explicit allowlist enforcement for future command/tool execution paths.
- Local structured audit persistence in JSONL or SQLite.
- Versioned local envelope schemas and validation fixtures.

**Planned later**
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
