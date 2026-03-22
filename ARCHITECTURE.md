# System Architecture: Refocus-OS

## Core Philosophy
Refocus-OS is currently a blueprint for a cognitive runtime secured by a layered defense fabric. The repository already includes local-first intent-ingress security hooks and structured audit storage, while the broader Message Bus, Orchestrator, and kernel-level defenses remain planned. Efficiency, modularity, deterministic reasoning, and proactive protection are the design foundations.

## Architectural Layers

**Layer 0: Hardware & Kernel (planned)**  
A custom Debian base with standard Linux Kernel and prospective eBPF instrumentation. Performance-critical components such as attention kernels, syscall monitors, and integrity verifiers are architectural goals, not current repository features.

**Layer 1: Model Runtime**  
A high-efficiency inference server (vLLM or llama.cpp) runs the foundation model enhanced with NHA, handling quantization, LoRA loading, and batch scheduling.

**Layer 2: Hydra Defense System**  
The current repository implements only the earliest local security hooks: intent sanitization/schema validation, structured local auditing, and explicit execution allowlists. Dedicated LangSec, CodeSec, and SysSec services remain planned.

**Layer 3: IPC Message Bus (planned)**  
A Unix-socket-based, schema-validated bus for inter-agent messaging is planned. Versioned, signed envelopes and Hydra inspection are design targets rather than implemented features.

**Layer 4: The Orchestrator & Services (planned)**  
The future orchestrator will fuse user and background inputs into consensus intents, decompose them into subtasks using MATPO, and manage execution via the Compute Economist. Today, only the local ingress validation and execution-policy primitives are implemented.

**Layer 5: Specialist Agents**  
Independent sandboxed workers performing tasks defined by their contracts. Each operates in a restricted namespace, communicating only through the Message Bus with authenticated envelopes.

**Layer 6: User Interface Layer**  
A Tauri/React HUD and Terminal provide minimal graphical surfaces for interacting with the Orchestrator, managing budgets, and visualizing security alerts.

## Core Subsystems and Logic Flow

### Orchestrator (`services/orchestrator/`)
**Purpose:** Planned central reasoning and coordination hub.  
**Components:**
- **Implemented now:** local intent ingress validation/sanitization hooks live in `python_core/refocus_core/intent_security.py` and can be wired into an eventual orchestrator endpoint.
- **Planned later — Intent Fusion Network (IFN):** weighted vector fusion of sanitized user/system intents.
- **Planned later — Planner/Worker Scheduler:** MATPO for task DAG generation and assignment.
- **Planned later — Compute Economist:** budgets from `economist.yaml` to optimize token/time.
- **Planned later — Contract Registry:** loads and validates semver JSON contracts from `/etc/refocus/contracts`.

### Hydra Defense System (`services/security/`)
**Purpose:** Continuous adaptive protection, currently at an early local-first stage.  
**Components:**
- **Implemented now:** local schema validation, sanitization, execution allowlists, and JSONL/SQLite audit logging.
- **Planned later — Kernel Hook Service:** eBPF syscall tracing + local publication.
- **Planned later — LG-A (LangSec):** prompt sanitization & injection defense daemon.
- **Planned later — LG-B (CodeSec):** code safety validation & vulnerability scanning.
- **Planned later — LG-C (SysSec):** real-time anomaly detection + kill-switch.

### Message Bus & Semantic Spine (`ops/ipc/`)
**Purpose:** Communication backbone + memory reference.  
**Components:**
- **Envelope Schema:** ID, timestamps, src/dst, verb, payload, signature, budget.
- **GRACE Service:** Embedding index for intents, logs, rationale.

### Specialist Agents (`services/agents/`)
**Purpose:** Contracted workers under verification.  
**Components:**
- Tool wrappers; TRM verifier; local task-specific sanity checks.

### Memory & Reflection (`memory/`)
**Purpose:** Context persistence, audit, self-improvement.  
**Components:**
- **NHA Kernels, ArtHippoNet, Reflection Daemon.**

### Example Logic Flow: Secure Request
1. Intent Capture → 2. **Implemented now:** local sanitization/schema validation + audit → 3. **Planned later:** fusion → 4. **Planned later:** planning → 5. **Implemented now for future execution paths:** allowlist gate + audit → 6. **Planned later:** monitoring → 7. **Planned later:** verification → 8. **Planned later:** output

## Security & Integrity Enhancements
**Implemented now**
- Local intent sanitization and schema validation.
- Explicit allowlist enforcement for future command/tool execution paths.
- Local structured audit persistence in JSONL or SQLite.

**Planned later**
- ed25519 agent keys; rotating nonces.
- eBPF syscall whitelists per agent.
- Hash-linked audit chains.
- Attestation: kernel_hook → LG‑C → LG‑A → Orchestrator → Agents → UI.
- Isolation: circuit breakers; quarantine zones.

## Observability
Latency percentiles, token burn, anomaly rates, memory use, verifier pass rates. HUD exposes Max Tokens/Time/Depth and Kill All Workers.

## Data Hygiene
GRACE redacts PII, TTLs, hot/warm/cold vector tiers.

## Boot Targets
refocus-pre.target → kernel_hook, LG-C  
refocus-core.target → LG-A, Orchestrator  
refocus-agents.target → Verifier, Workers  
refocus-ui.target → HUD

All units follow systemd dependency graph ensuring sequential secure startup.
