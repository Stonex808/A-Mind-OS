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
- **Layer 3 – IPC Message Bus:** Unix‑socket bus with schema‑validated, signed envelopes; GRACE embeddings for retrieval/audit.  
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
4. `scripts/dev.sh` — run the fully local demo workflow (store one intent, then recall it).
5. Inspect the generated artifacts under `./data/demo/` and `./data/memory/`.

## Run the local demo

This demo is **offline by default**. It does not call any cloud service, telemetry endpoint, or LLM API.
It uses a deterministic rules file, repo-local JSON memory, and a repo-local SQLite index so you can inspect or back up every artifact.

### One-command demo

From the repository root:

```bash
scripts/dev.sh
```

The script performs the exact sequence below:

1. Creates `./data/demo/demo-intent.txt` with a plain-text intent beginning with `remember`.
2. Runs `python3 services/orchestrator/local_demo.py --intent-file ./data/demo/demo-intent.txt` to verify and store the intent locally.
3. Pipes `recall backup path` into `python3 services/orchestrator/local_demo.py --stdin` to prove deterministic recall through the memory layer.
4. Leaves all artifacts on disk for inspection.

### Direct commands

Store from a local file:

```bash
python3 services/orchestrator/local_demo.py --intent-file ./data/demo/demo-intent.txt
```

Store or recall from stdin:

```bash
printf 'recall backup path
' | python3 services/orchestrator/local_demo.py --stdin
```

Serve a simple local Unix socket:

```bash
python3 services/orchestrator/local_demo.py --socket
```

When socket mode is active, send a single line intent from another shell:

```bash
printf 'remember the maintenance window is sunday
' | socat - UNIX-CONNECT:./data/demo/orchestrator.sock
```

### Local artifacts

- `./data/demo/orchestrator.db` — SQLite index of every demo run.
- `./data/demo/runs/*.json` — Full JSON artifact per run, including verifier output and recalled context.
- `./data/memory/episodic_local/` — Episodic memory JSON files used by the demo.
- `./data/memory/semantic_local/` — Semantic memory JSON files used by the demo.
- `./data/memory/procedural/` — Learned procedures extracted from successful demo runs.

### Verification rules

The verifier rules live in `services/orchestrator/rules/local_rules.json`. The intent is rejected if it is empty, too long, contains banned command patterns, appears to include secrets, or does not include one of the required local-demo verbs: `remember`, `recall`, `store`, or `note`.

### Privacy and backup notes

All demo artifacts are stored as plain-text JSON or SQLite files on local disk. That keeps the system auditable and easy to back up, but it also means sensitive intents are not encrypted at rest by default. If you plan to store private data, prefer full-disk encryption, encrypted backups, or an encrypted volume for the repository data directory.

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
