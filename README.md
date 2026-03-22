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

### Security Roadmap with Early Local Protections
The long-term design centers on the **Adaptive Integrity Shield**: **LangSec** for intent sanitization, **CodeSec** for code verification, and **SysSec** for system monitoring. **Implemented now:** local intent sanitization/schema validation plus local audit logging and allowlist-based execution gates in `python_core/refocus_core/`. **Planned later:** dedicated LangSec/CodeSec/SysSec daemons, eBPF monitoring, and verifier enforcement.

### Quiet, Headless Operation
Agents run as silent background services with minimal visual noise. User interaction occurs via voice or global hotkeys, with the **AI Terminal** and **HUD** providing real-time visibility into active intents and resource budgets.

### Auditable by Design, with Verifiability Planned
**Implemented now:** structured local audit logging in JSONL or SQLite for intent-ingress and future execution-policy decisions. **Planned later:** deterministic replay data, signed envelopes, verifier-backed approvals, and reflection daemons that learn from operational logs.

**Current Status:** Mostly blueprint and boot-specification phase, with a small set of concrete local Python security primitives for intent ingress, audit logging, and execution allowlists. See `SECURITY.md` for exact guarantees and non-goals.

> Pro Tip: Press **Alt + Enter** to auto-capture the current selection as an intent and send it to the Orchestrator—no manual steps.

---

## System Architecture (Bird’s‑Eye)

See **ARCHITECTURE.md** for deep detail. High level summary:

- **Layer 0 – Hardware & Kernel (planned):** Debian base + Linux kernel + prospective eBPF instrumentation for attention kernels, syscall monitors, and integrity verifiers.  
- **Layer 1 – Model Runtime (planned):** High‑efficiency inference server (vLLM or llama.cpp) with NHA, quantization, LoRA loading, and batch scheduling.  
- **Layer 2 – Hydra Defense System (partially planned):** today the repo includes local intent sanitization/schema validation and local audit/allowlist hooks; dedicated LangSec / CodeSec / SysSec services remain planned.  
- **Layer 3 – IPC Message Bus (planned):** Unix‑socket bus with schema‑validated, signed envelopes; GRACE embeddings for retrieval/audit.  
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
2. **Implemented now — Ingress hardening:** local hooks can sanitize text, validate schema, and write an audit record before planning.  
3. **Planned later — Fusion:** Orchestrator IFN fuses sanitized intent with context.  
4. **Planned later — Planning:** MATPO builds a task DAG.  
5. **Implemented now for future paths — Execution gate:** any command/tool request should pass an explicit allowlist check and audit log.  
6. **Planned later — Monitoring:** eBPF stream scored by LG‑C.  
7. **Planned later — Verification:** TRM + CodeSec validate outputs.  
8. **Planned later — Output:** HUD shows verified result; anomalies trigger quarantine.

---

## Security & Integrity

**Implemented now**
- Local intent sanitization and schema validation hooks at ingress.  
- Explicit allowlist checks for future tool/command execution paths.  
- Structured local audit logging to JSONL or SQLite.  

**Planned later**
- ed25519 per‑agent keys and rotating nonces.  
- eBPF syscall whitelists per agent.  
- Hash‑linked audit chains for task logs.  
- Startup attestation: kernel_hook → LG‑C → LG‑A → Orchestrator → Agents → UI.  
- Circuit breakers and quarantine zones for misbehavior.

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

- **Contracts First:** Define/validate JSON contracts in `/config/contracts`.  
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

PRs welcome. Keep changes modular, contracts versioned (semver), and wire-once through the Bus.

## License

Apache-2.0 (provisional; change as needed).
