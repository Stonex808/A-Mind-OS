# A-Mind-OS

A-Mind-OS is a local-first experimental runtime for verified agent work. The repository currently ships a small, offline Python implementation: it validates an intent, routes it through one deterministic planner/worker boundary, stores bounded JSON/SQLite records, and recalls local memory. The larger Refocus-OS vision—an AI-native Debian environment with model services, hardened IPC, eBPF monitoring, and a desktop HUD—is retained as architecture and lineage, not presented as finished software.

## Current status

| Surface | Status | Source of truth |
| --- | --- | --- |
| Offline store/recall loop | Runnable | `services/orchestrator/local_demo.py` |
| Planner, workers, task schema, execution log | Runnable | `services/orchestrator/orchestrator_service.py` |
| Local persistence, redaction/refusal, retention | Runnable | `python_core/refocus_core/persistence.py` |
| Agent contract registration | Runnable | `services/orchestrator/contract_registry.py` |
| Static browser shell | Prototype | `ui/shell/` |
| Harness admission, budgets, lifecycle | Library seam | `services/orchestrator/harness_runtime.py` |
| systemd, Hydra services, eBPF, production IPC, Tauri | Planned | `ARCHITECTURE.md` and scoped `agents.md` files |

## Clone and verify on a new device

The required path has no third-party runtime dependencies. Install Git and Python 3.11 or newer, then run:

```bash
git clone https://github.com/Stonex808/A-Mind-OS.git
cd A-Mind-OS
scripts/verify-repo.sh
```

`verify-repo.sh` compiles the Python source, runs all tests, validates agent contracts, and exercises store → recall in a temporary directory. It also confirms that the separate project-state gate fails closed while its two canonical governance inputs are absent. The command must exit `0` before a change is considered complete.

To keep demo output for inspection instead of using temporary verification data:

```bash
scripts/setup.sh
scripts/dev.sh
```

Runtime files are written under `data/` and intentionally ignored by Git. The generated `ui/shell/orchestrator-feed.json` is ignored too; the static shell falls back to committed `demo-data.json` when no live feed exists.

## Persistence and privacy

`config/refocus-os.toml` defines the default local paths, run retention, and sensitive-content mode:

- `redact` (default) replaces obvious credentials and identity/payment patterns before any JSON or SQLite write.
- `refuse` performs no run, event, or memory write when obvious sensitive content is detected.
- `off` stores content unchanged and should be used only with deliberate local controls.

These files are transparent, not encrypted. Use full-disk encryption or an encrypted data volume for real personal data, and back up `data/user/` separately from the Git repository.

## Repository map

- `python_core/` — memory, ingress security, auditing, persistence, and harness contracts.
- `services/orchestrator/` — the one canonical local orchestrator implementation.
- `config/contracts/` — concrete, standard-library-validated agent contracts and task schema.
- `tests/` — the only test suite; it uses `unittest` and temporary directories.
- `ui/shell/` — offline static interaction prototype.
- `systemd/units/` and `services/security/` — future-facing blueprints, not operational services.
- `docs/lineage/`, `RESEARCH.md`, and `refocus_os_guide_Final.md` — provenance and historical design inputs, not current implementation instructions.

## Contributor authority

Read `AGENTS.md` before changing the repository. In brief: preserve one implementation per responsibility, distinguish runnable code from plans, avoid unrelated edits, check existing PRs before opening another, and run `scripts/verify-repo.sh`. `ARCHITECTURE.md` describes the current boundaries; `TASKS.md` names the next work rather than maintaining parallel roadmaps.

## Known boundary

This is pre-production software. It does not currently execute arbitrary commands, call an LLM or the network, boot the included systemd graph, or provide the promised production security daemons. Those capabilities require explicit admission, tests, and documentation before they can be described as implemented.
