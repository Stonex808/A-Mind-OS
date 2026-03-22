# Refocus-OS

**Vision**  
An AI-first, agent-centric operating system layer built on a custom Debian base. Refocus-OS reimagines the user-computer relationship, transforming the OS from a passive tool manager into a proactive, reasoning co-pilot secured by an adaptive AI defense system. It operates primarily headless, context-aware, and hardened against intelligent threats.

---

## Core Principles

### Agent-Centric Architecture
Every system capability is implemented as an autonomous agent with a defined contract and schema. Agents communicate and coordinate through the Orchestrator, negotiating for resources and executing tasks silently under constant supervision by the security layer.

### Long-Context, Low-Compute
The foundation model uses **Native Hybrid Attention (NHA)** to sustain vast, persistent context at near-linear computational cost, enabling session-long coherence without performance degradation.

### Single-Model, Multi-Role Delegation
A single optimized foundation model performs multiple roles (Planner, WebAgent, Verifier, etc.) through specialized prompts and toolsets, coordinated by **Multi-Agent Tool-Integrated Policy Optimization (MATPO)**.

### Secure by Design
The **Adaptive Integrity Shield** protects the system through three coordinated defense layers: **LangSec** for prompt sanitization, **CodeSec** for code verification, and **SysSec** for system call anomaly detection.

### Quiet, Headless Operation
Agents run as silent background services with minimal visual noise. User interaction occurs via voice or global hotkeys, with the **AI Terminal** and **HUD** providing real-time visibility into active intents and resource budgets.

### Verifiable and Self-Improving
All actions are verifiable through deterministic logs, signed envelopes, and idempotent replay data. A **reflection daemon** learns from operational and security logs to refine internal policies continuously without retraining the core model.

**Current Status:** Blueprint and boot specification phase. This repository defines the architectural plan, agent directives, and subsystem contracts necessary for multi-agent implementation.

> Pro Tip: Press **Alt + Enter** to auto-capture the current selection as an intent and send it to the Orchestrator—no manual steps.

---

## System Architecture (Bird’s‑Eye)

See **ARCHITECTURE.md** for deep detail. High level summary:

- **Layer 0 – Hardware & Kernel:** Debian base + Linux kernel + eBPF instrumentation for attention kernels, syscall monitors, integrity verifiers.  
- **Layer 1 – Model Runtime:** High‑efficiency inference server (vLLM or llama.cpp) with NHA, quantization, LoRA loading, and batch scheduling.  
- **Layer 2 – Hydra Defense System:** Adaptive Integrity Shield (LangSec / CodeSec / SysSec) auditing prompts, code, and syscalls.  
- **Layer 3 – IPC Message Bus:** Unix‑socket bus with schema‑validated, signed envelopes; GRACE embeddings for retrieval/audit. Start with `config/contracts/envelope.v1.schema.json`, then service-specific contracts such as `config/contracts/orchestrator.envelope.v1.schema.json`, `config/contracts/verifier.envelope.v1.schema.json`, and `config/contracts/langsec.envelope.v1.schema.json`.  
- **Layer 4 – Orchestrator & Services:** Intent fusion, MATPO planner, Compute Economist, contract registry.  
- **Layer 5 – Specialist Agents:** Sandboxed workers bound by per‑agent contracts & whitelists.  
- **Layer 6 – UI Layer:** Tauri/React HUD + AI Terminal, global hotkeys, voice controls.

---

## Subsystems & Folders

- **services/orchestrator/** – Central reasoning & scheduling hub. See `services/orchestrator/agents.md`.
- **services/security/** – Hydra Defense (LG‑A LangSec, LG‑B CodeSec, LG‑C SysSec, Kernel Hook). Per‑folder `agents.md` files.
- **services/agents/** – Specialist workers (example: `verifier_trm`). Contracted via `/config/contracts`. See each `agents.md`.
- **ops/ipc/** – Message Bus & Envelope schema; GRACE semantic spine. See `ops/ipc/agents.md`.
- **memory/grace/** – Embeddings, retrieval, audit logging, reflection plumbing. See `memory/grace/agents.md`.
- **ui/shell/** – Tauri/React HUD & AI Terminal bindings. See `ui/shell/agents.md`.
- **config/** – `economist.yaml` budgets, agent contracts, policy knobs.
- **systemd/units/** – Boot targets and unit templates.
- **scripts/** – Setup/dev helpers.

### Boot Targets (systemd)
- `refocus-pre.target` → `kernel_hook.service`, `lg_c_syssec.service`  
- `refocus-core.target` → `lg_a_langsec.service`, `orchestrator.service`  
- `refocus-agents.target` → `verifier_trm.service`, workers  
- `refocus-ui.target` → HUD

Sequential secure startup enforced via unit dependencies.

---

## Example Logic Flow: Secure User Request

1. **Intent Capture:** User selects code and presses **Alt+Enter**.  
2. **Sanitization:** LG‑A screens for injection.  
3. **Fusion:** Orchestrator IFN fuses sanitized intent with context.  
4. **Planning:** MATPO builds a task DAG.  
5. **Execution:** Authenticated envelopes sent to agents via Bus.  
6. **Monitoring:** eBPF stream scored by LG‑C.  
7. **Verification:** TRM + CodeSec validate outputs.  
8. **Output:** HUD shows verified result; anomalies trigger quarantine.

---

## Security & Integrity

- ed25519 per‑agent keys, rotating nonces.  
- eBPF syscall whitelists per agent.  
- Hash‑linked audit chains for task logs.  
- Startup attestation: kernel_hook → LG‑C → LG‑A → Orchestrator → Agents → UI.  
- Circuit breakers & quarantine zones for misbehavior.

---

## Observability

Track latency percentiles, token burn, anomaly rates, memory use, verifier pass rates. HUD exposes **Max Tokens**, **Max Time**, **Max Depth**, and **Kill All Workers**.

---

## Data Hygiene

GRACE redacts PII, enforces TTLs, and manages hot/warm/cold vector tiers for semantic logs.

---

## Getting Started (Scaffold)

1. Clone or extract this repo.
2. `scripts/setup.sh` — prepare envs, install deps.
3. Review and adjust `config/refocus-os.toml` to fit your deployment (system limits, LLM runtime socket path, security toggles). The defaults ship with headless, local-first assumptions—keep secrets out of the file or rotate it into encrypted storage if needed.
4. `scripts/dev.sh` — run local services (orchestrator, security, HUD).
5. Open the HUD and press **Alt+Enter** to test the intent loop.

> Pro Tip: On supported editors, **Alt+Enter** auto-initiates the demo workflow end-to-end.

---

## Python Core (ArtHippoNet Memory)

The `python_core` package implements the ArtHippoNet memory stack (episodic, semantic, and procedural stores). Everything runs locally
and persists to `./data/memory/**` using human-readable JSON so you can audit or back up data with standard tools.

### Local Dependencies

Install the memory dependencies into your virtual environment:

```bash
pip install chromadb sentence-transformers
pip install structlog  # optional, enables structured JSON logs
pip install jsonschema  # required for local contract validation
```

These libraries do not phone home when configured as above (`anonymized_telemetry=False`). The first use of
`SentenceTransformer('all-MiniLM-L6-v2')` will try to download model weights; fetch them once while online, then cache them in
`~/.cache/torch` for offline reuse or distribute the files across machines as needed.

### Running the Memory Demo

From the repository root:

```bash
python -m python_core.test_complete_memory
```

The script exercises episodic storage, semantic fact learning, and procedural extraction. Data is kept locally under
`./data/memory/` so remember to secure that directory if it contains sensitive material (e.g., encrypt the folder or keep it on
an encrypted volume).

---

## Development Workflow

- **Contracts First:** Define/validate JSON contracts in `/config/contracts`, especially `config/contracts/envelope.v1.schema.json`, `config/contracts/orchestrator.envelope.v1.schema.json`, `config/contracts/verifier.envelope.v1.schema.json`, and `config/contracts/langsec.envelope.v1.schema.json`. Validate local fixtures from `config/contracts/examples/` before wiring new services.  
- **Agent Stubs:** Implement sockets + health endpoints, then register with Orchestrator.  
- **Policy Tuning:** Adjust `config/economist.yaml` budgets.  
- **Security Gates:** All PRs run LangSec/CodeSec checks and unit tests for envelope schema.

---

## Roadmap (Milestones)

- M1: IPC bus + signed envelope schema + GRACE MVP  
- M2: Orchestrator IFN + MATPO planner + economist budgets  
- M3: Hydra Defense (LG‑A/B/C) + kernel hook + kill‑switch  
- M4: Tauri HUD + AI Terminal bindings + hotkeys  
- M5: Reflection daemon + self‑tuning policies

---

## Contributing

PRs welcome. Keep changes modular, contracts versioned (semver), and wire-once through the Bus. Contributors should update the local contract set in `config/contracts/envelope.v1.schema.json`, `config/contracts/orchestrator.envelope.v1.schema.json`, `config/contracts/verifier.envelope.v1.schema.json`, and `config/contracts/langsec.envelope.v1.schema.json` before adding new services.

## License

Apache-2.0 (provisional; change as needed).
