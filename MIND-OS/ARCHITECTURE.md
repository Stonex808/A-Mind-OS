# System Architecture: Refocus-OS

## Core Philosophy
Refocus-OS converts the Linux userspace into a cognitive runtime secured by an intelligent defense fabric. It operates through a central nervous system (Message Bus) and a brainstem (Orchestrator) that direct a colony of agents within verifiable security boundaries. Efficiency, modularity, deterministic reasoning, and proactive protection are the design foundations.

## Architectural Layers

**Layer 0: Hardware & Kernel**  
A custom Debian base with standard Linux Kernel and eBPF instrumentation. Performance-critical components such as attention kernels, syscall monitors, and integrity verifiers are implemented at the driver/eBPF level.

**Layer 1: Model Runtime**  
A high-efficiency inference server (vLLM or llama.cpp) runs the foundation model enhanced with NHA, handling quantization, LoRA loading, and batch scheduling.

**Layer 2: Hydra Defense System**  
Implements the Adaptive Integrity Shield. It continuously audits agent communications, code outputs, and syscall behaviors through the LangSec, CodeSec, and SysSec guard models.

**Layer 3: IPC Message Bus**  
A Unix-socket-based, schema-validated bus for inter-agent messaging. Each envelope is versioned, signed, and inspected by the Hydra Defense layer before being delivered. Messages include GRACE semantic embeddings for long-term retrieval and audit.

**Layer 4: The Orchestrator & Services**  
The brainstem coordinating system intent, decomposition, and scheduling. It fuses user and background inputs into consensus intents, decomposes them into subtasks using MATPO, and manages execution via the Compute Economist.

**Layer 5: Specialist Agents**  
Independent sandboxed workers performing tasks defined by their contracts. Each operates in a restricted namespace, communicating only through the Message Bus with authenticated envelopes.

**Layer 6: User Interface Layer**  
A Tauri/React HUD and Terminal provide minimal graphical surfaces for interacting with the Orchestrator, managing budgets, and visualizing security alerts.

## Core Subsystems and Logic Flow

### Orchestrator (`services/orchestrator/`)
**Purpose:** Central reasoning and coordination hub.  
**Components:**
- **Intent Fusion Network (IFN):** Weighted vector fusion of sanitized user/system intents.
- **Planner/Worker Scheduler:** MATPO for task DAG generation and assignment.
- **Compute Economist:** Budgets from `economist.yaml` to optimize token/time.
- **Contract Registry:** Loads & validates semver JSON contracts from `/etc/refocus/contracts`.

### Hydra Defense System (`services/security/`)
**Purpose:** Continuous adaptive protection.  
**Components:**
- **Kernel Hook Service:** eBPF syscall tracing + ZeroMQ publication.
- **LG-A (LangSec):** Prompt sanitization & injection defense.
- **LG-B (CodeSec):** Code safety validation & vuln scanning.
- **LG-C (SysSec):** Real-time anomaly detection + kill-switch.

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
1. Intent Capture → 2. Sanitization → 3. Fusion → 4. Planning → 5. Execution → 6. Monitoring → 7. Verification → 8. Output

## Security & Integrity Enhancements
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
