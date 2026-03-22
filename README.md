# Refocus-OS

**Vision**  
An AI-first, agent-centric operating system layer built on a custom Debian base. Refocus-OS reimagines the user-computer relationship, transforming the OS from a passive tool manager into a proactive, reasoning co-pilot secured by an adaptive AI defense system. The long-term goal is still a deeply integrated local operating environment with orchestrated agents, strong verification, and layered defenses.

**Current reality**  
Today this repository is best approached as a **local-first developer sandbox** with:
- an **implemented now** orchestrator demo that stores and recalls intents locally;
- a **local demo / prototype** browser shell in plain HTML/CSS/JS;
- several **planned / blueprint only** security, systemd, and contract surfaces that document the intended full system.

Start with the runnable local path first, then read the blueprint sections to understand where the project is heading.

---

## Core Principles

### Agent-Centric Architecture
Every system capability is modeled as an autonomous agent with a defined contract and schema. The long-term plan is for agents to coordinate through the Orchestrator, negotiating for resources and executing tasks under constant supervision by the security layer.

### Long-Context, Low-Compute
The foundation model vision uses **Native Hybrid Attention (NHA)** to sustain vast, persistent context at near-linear computational cost, enabling session-long coherence without performance degradation.

### Single-Model, Multi-Role Delegation
A single optimized foundation model is intended to perform multiple roles (Planner, WebAgent, Verifier, etc.) through specialized prompts and toolsets, coordinated by **Multi-Agent Tool-Integrated Policy Optimization (MATPO)**.

### Secure by Design
The **Adaptive Integrity Shield** vision protects the system through three coordinated defense layers: **LangSec** for prompt sanitization, **CodeSec** for code verification, and **SysSec** for system call anomaly detection.

### Quiet, Headless Operation
The long-term operating mode is mostly headless, with user interaction via voice or global hotkeys and visible feedback through an **AI Terminal** and **HUD**.

### Verifiable and Self-Improving
All actions are intended to become verifiable through deterministic logs, signed envelopes, and idempotent replay data. A future **reflection daemon** can learn from operational and security logs to refine internal policies without retraining the core model.

> Contributor note: the fastest accurate on-ramp is still the fully local demo in `services/orchestrator/local_demo.py` plus the static shell prototype in `ui/shell/`. Those paths are offline by default, inspectable on disk, and do not require cloud services.

---

## Status at a Glance

| Area | Status | What exists today | Contributor starting point |
| --- | --- | --- | --- |
| `services/orchestrator/` | **implemented now** | Runnable local intent store/recall demo with JSON + SQLite artifacts. | Run `scripts/dev.sh`, then inspect `data/demo/` and `data/memory/`. |
| `services/security/` | **planned / blueprint only** | Design notes in per-layer `agents.md` files; no runnable security daemons in this repo yet. | Treat as architecture guidance while iterating on the local orchestrator path first. |
| `ui/shell/` | **local demo / prototype** | Static offline shell prototype in HTML/CSS/JS. | Serve `ui/shell/` locally after trying the orchestrator demo. |
| `systemd/units/` | **planned / blueprint only** | Unit and target templates describing intended boot order. | Use them as naming/dependency references only; do not expect the services to start end-to-end yet. |
| `config/contracts/` | **planned / blueprint only** | README describing future contract shape; no concrete contract set checked in yet. | Read the README for expected schema direction, but prototype locally without depending on a full contract registry. |

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

Interpret those layers as the **target architecture**. The runnable developer experience in this repository is currently much smaller and intentionally local-first.

---

## Subsystems & Folders

- **`services/orchestrator/` — implemented now.** Central reasoning sandbox. The local demo is the primary runnable path today; it stores validated intents locally and proves deterministic recall. See `services/orchestrator/agents.md`.
- **`services/security/` — planned / blueprint only.** Hydra Defense design docs for LG-A LangSec, LG-B CodeSec, LG-C SysSec, and the kernel hook. Use the docs as future implementation notes, not as evidence of shipped daemons yet.
- **`services/agents/` — mixed, mostly blueprint.** Specialist worker layout with example verifier structure; actual end-to-end agent runtime is still evolving.
- **`ops/ipc/` — blueprint with supporting docs.** Message bus and envelope direction. See `ops/ipc/agents.md`.
- **`memory/grace/` — implemented now for local storage primitives, broader vision still evolving.** Local JSON/SQLite-backed memory flows are already used by the demo; broader GRACE semantics remain architectural.
- **`ui/shell/` — local demo / prototype.** Visible offline shell prototype for validating interaction design before Tauri integration. See `ui/shell/agents.md`.
- **`config/` — mixed.** `economist.yaml` and related config paths define direction; `config/contracts/` is currently blueprint-oriented.
- **`systemd/units/` — planned / blueprint only.** Unit templates for the intended secure boot graph.
- **`scripts/` — implemented now.** Low-friction setup and local demo helpers.

### Boot Targets (`systemd/units/`)
These files currently document the intended secure boot sequence rather than a fully wired local deployment:
- `refocus-pre.target` → `kernel_hook.service`, `lg_c_syssec.service`  
- `refocus-core.target` → `lg_a_langsec.service`, `orchestrator.service`  
- `refocus-agents.target` → `verifier_trm.service`, workers  
- `refocus-ui.target` → HUD

Use the local scripts first; treat the systemd graph as a roadmap for future service packaging.

---

## Local-First Quick Start

If you only do one thing as a contributor, do this path first:

1. Clone or extract this repo.
2. Run `scripts/setup.sh` to prepare a local development environment.
3. Review `config/refocus-os.toml` and keep secrets out of the repository; the local demo works without cloud credentials.
4. Run `scripts/dev.sh` to exercise the implemented orchestrator path.
5. Inspect `./data/demo/` and `./data/memory/` to understand how state is stored locally.
6. Optionally serve `ui/shell/` to explore the visible shell prototype.

This path is **offline by default**, uses plain JSON and SQLite files that are easy to audit and back up, and keeps the current contributor experience low-friction.

---

## Example Logic Flow: Secure User Request

This is the **target flow** the architecture is designed to support:

1. **Intent Capture:** User selects code and presses **Alt+Enter**.  
2. **Sanitization:** LG‑A screens for injection.  
3. **Fusion:** Orchestrator IFN fuses sanitized intent with context.  
4. **Planning:** MATPO builds a task DAG.  
5. **Execution:** Authenticated envelopes sent to agents via Bus.  
6. **Monitoring:** eBPF stream scored by LG‑C.  
7. **Verification:** TRM + CodeSec validate outputs.  
8. **Output:** HUD shows verified result; anomalies trigger quarantine.

For the **current runnable path**, use `scripts/dev.sh`, which exercises a smaller local loop: validate intent → store to local memory → recall locally.

---

## Security & Integrity

Long-term controls remain central to the vision:

- ed25519 per‑agent keys, rotating nonces.  
- eBPF syscall whitelists per agent.  
- Hash‑linked audit chains for task logs.  
- Startup attestation: kernel_hook → LG‑C → LG‑A → Orchestrator → Agents → UI.  
- Circuit breakers & quarantine zones for misbehavior.

**Current contributor guidance:** the local demo already avoids cloud calls and stores all artifacts locally, but demo data is not encrypted at rest. If you place sensitive data in `data/`, prefer full-disk encryption, encrypted backups, or an encrypted volume.

---

## Observability

The long-term HUD surfaces latency percentiles, token burn, anomaly rates, memory use, verifier pass rates, plus **Max Tokens**, **Max Time**, **Max Depth**, and **Kill All Workers**.

Today, observability is primarily file-based: inspect generated JSON run artifacts and the local SQLite database from the demo path.

---

## Data Hygiene

The GRACE vision includes PII redaction, TTLs, and hot/warm/cold vector tiers for semantic logs.

Today, local artifacts remain intentionally simple and inspectable. That lowers friction and helps backups, but it also means contributors must decide whether repository-local JSON/SQLite files are appropriate for the data they place there.

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

- **Start local-first:** run the orchestrator demo and shell prototype before touching blueprint-only subsystems.
- **Contracts First:** define/validate JSON contracts in `/config/contracts` once concrete contracts exist.
- **Agent Stubs:** implement sockets + health endpoints, then register with Orchestrator.
- **Policy Tuning:** adjust `config/economist.yaml` budgets.
- **Security Gates:** when the security services become concrete, all PRs should run LangSec/CodeSec checks and unit tests for envelope schema.

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
