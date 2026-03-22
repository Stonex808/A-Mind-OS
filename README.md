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
2. Run `scripts/setup.sh` to validate the required local prerequisites and create the expected local data directories.
3. Run `scripts/verify-local-demo.sh` for the clearest end-to-end offline verification path, or `scripts/dev.sh` if you only want to execute the demo without the extra checks.
4. Review and adjust `config/refocus-os.toml` only if you are extending beyond the currently implemented demo path. Keep secrets out of repo-local config files or move them into encrypted storage.
5. Inspect the generated artifacts under `./data/demo/` and `./data/memory/`.

## Run the local demo

This demo is **offline by default**. It does not call any cloud service, telemetry endpoint, or LLM API.
It uses a deterministic rules file, repo-local JSON memory, and a repo-local SQLite index so you can inspect or back up every artifact.

### Required Python version

- `python3` **3.11 or newer** is required for the currently implemented local demo path.
- `scripts/setup.sh` fails fast if that requirement is not met.

### Required vs optional dependencies

Required for the currently implemented local workflow:

- `python3` 3.11+
- Standard-library modules only for `scripts/dev.sh`, `scripts/setup.sh`, `scripts/verify-local-demo.sh`, and `services/orchestrator/local_demo.py`

Optional for local development, but **not required** for the default offline demo path:

- `chromadb` + `sentence-transformers` for vector-backed memory instead of the JSON fallback
- `structlog` for structured logs
- `socat` for manual Unix socket testing with `python3 services/orchestrator/local_demo.py --socket`
- `node`, `cargo`, and Tauri dependencies for future UI/runtime work

### One clearly documented local validation path

From the repository root:

```bash
scripts/verify-local-demo.sh
```

That wrapper performs the entire offline verification flow:

1. Runs `scripts/setup.sh` to confirm Python and prepare local directories.
2. Runs `scripts/dev.sh` to store one intent and then recall it.
3. Verifies that the expected SQLite, JSON, and memory artifacts exist locally.
4. Confirms that the latest run artifacts include one `stored` result and one `recalled` result.

If you only want to execute the demo itself, you can still run:

```bash
scripts/dev.sh
```

The demo script performs the exact sequence below:

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

`scripts/setup.sh` creates or verifies the directories. After a successful local demo, you should see:

Under `./data/demo/`:

- `demo-intent.txt` — The plain-text sample intent used by `scripts/dev.sh`.
- `orchestrator.db` — SQLite index of every demo run.
- `runs/run-*.json` — Full JSON artifact per run, including verifier output and recalled context.
- `orchestrator.sock` — Only if you explicitly run socket mode.

Under `./data/memory/`:

- `episodic_local/episodes/*.json` — Repo-local episodic memory entries written by the fallback memory path.
- `semantic_local/facts.json` — Stored local facts.
- `semantic_local/concepts.json` — Stored local concepts.
- `procedural/*.json` — Learned procedures extracted from successful demo runs.

All of these files remain local and human-inspectable so contributors can back them up with standard file tools.

### Verification rules

The verifier rules live in `services/orchestrator/rules/local_rules.json`. The intent is rejected if it is empty, too long, contains banned command patterns, appears to include secrets, or does not include one of the required local-demo verbs: `remember`, `recall`, `store`, or `note`.

### Privacy and backup notes

All demo artifacts are stored as plain-text JSON or SQLite files on local disk. That keeps the system auditable and easy to back up, but it also means sensitive intents are not encrypted at rest by default. If you plan to store private data, prefer full-disk encryption, encrypted backups, or an encrypted volume for the repository data directory.


### What success looks like

A successful local validation run looks like this:

- `scripts/verify-local-demo.sh` exits with status code `0`.
- The store step returns JSON containing `"accepted": true` and `"status": "stored"`.
- The recall step returns JSON containing `"accepted": true` and `"status": "recalled"`.
- The recall payload mentions the previously saved backup path through `past_experiences`, `relevant_facts`, or both.
- `./data/demo/orchestrator.db` and at least two `./data/demo/runs/run-*.json` files exist after the run.

### Intentionally not runnable yet

The repository still contains architectural blueprints and service contracts that are **not** part of the current runnable local demo. In particular, contributors should treat these as planned or partial work rather than expecting them to boot locally today:

- The full systemd boot chain described in the architecture docs.
- Hydra security services such as LG-A, LG-C, and the kernel hook pipeline.
- eBPF/kernel instrumentation and syscall anomaly monitoring.
- The production multi-agent runtime, IPC bus, and authenticated envelope flow.
- The final Tauri-based desktop shell and global hotkey integration.

Today’s runnable path is intentionally narrower: one deterministic orchestrator demo with local verification and local persistence only.

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
