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

The memory stack is **local-first**: Chroma stores vectors on disk, procedures/episodes/concepts are saved as JSON, and no
telemetry is enabled. To make setup reproducible, create a fresh virtual environment from the repo root and install the exact
packages you need:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "chromadb==0.5.23" "sentence-transformers==3.4.1"
python -m pip install "structlog==24.4.0"  # optional structured logging
```

Dependency notes:

- `chromadb` provides the local vector index under `./data/memory/**/chroma`.
- `sentence-transformers` provides the embedding model used by episodic and semantic memory.
- `structlog` is optional. If it is not installed, the code falls back to Python's standard `logging` module.

Offline/reproducible setup guidance:

1. While online, run a one-time warm-up so `SentenceTransformer("all-MiniLM-L6-v2")` downloads its model weights into the local cache.
2. Reuse that cache offline by keeping `~/.cache/torch` and `~/.cache/huggingface` available, or pre-seed those directories on the target machine.
3. If you need fully repeatable workstation setup, export wheels once (`python -m pip download ... -d ./vendor/wheels`) and install later with `python -m pip install --no-index --find-links ./vendor/wheels ...`.

### Running the Memory Demo

From the repository root:

```bash
python -m python_core.test_complete_memory
```

### Running Deterministic Memory Tests

The automated tests use temporary local directories and fake in-memory vector/embedding backends so they do **not** require network
access or downloaded models:

```bash
pytest python_core/tests/test_memory_stack.py
```

### Local Data Safety: Backup, Encryption, Retention

All memory data stays under `./data/memory/`. That is convenient for backups, but it also means **anyone with filesystem access can
read it unless you protect it**. Recommended local-only practices:

- **Backups:** copy `./data/memory/` with standard local tools such as `tar`, `rsync`, or your encrypted backup workflow. Test restores regularly.
- **Encryption at rest:** prefer a full-disk-encrypted volume or an encrypted container for `./data/memory/` if episodes may contain prompts, observations, or secrets.
- **Retention:** set a simple deletion policy for old episodes and logs. Human-readable JSON is easy to audit, but it also makes long-term accumulation easy to overlook.
- **Secret hygiene:** avoid storing tokens, credentials, or raw personal data in task descriptions, observations, tags, or logs. Optional structured logs can also capture context, so keep log levels conservative on shared machines.

---


## Local Shell Prototype

A minimal visible prototype now lives in `ui/shell/` and runs entirely offline with plain HTML, CSS, and JavaScript. It is intentionally simple so the interaction model can be validated before wiring in Tauri or backend services.

### What the prototype includes

- A large labeled intent input with `Ctrl+Enter` submit support.
- A visible submit button plus clear/load-demo controls.
- A local activity log fed from `ui/shell/demo-data.json` and updated in-browser.
- A memory panel showing local notes only.
- A large emergency-stop control that disables submission with no hidden steps.
- Obvious labels, focus states, and keyboard navigation for all controls.

### Run it locally

```bash
python -m http.server 4173 --directory ui/shell
```

Then open `http://localhost:4173` in your browser. A lightweight local server is recommended because browsers often block `fetch()` calls for JSON files when pages are opened directly with the `file://` protocol.

### Walkthrough

1. Start a local static server in `ui/shell/` and open the page in your browser.
2. Review the hero status badges to confirm the prototype is offline-only and telemetry-free.
3. Type into **Intent input** or choose **Load demo intent** to populate an example request.
4. Press **Ctrl+Enter** or click **Submit intent** to append a sanitized entry to the top of the activity log.
5. Browse the **Memory panel** to see the local-only context this prototype exposes.
6. Use **Clear emergency stop** to simulate a halt: the intent field is disabled until you release the stop state.

### Screenshots

Screenshot capture is pending in this environment because the required browser screenshot tool was not available during this run. Once available, add current captures from `ui/shell/` here.

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
