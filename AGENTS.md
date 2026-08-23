# Repository Working Agreement

This file is the canonical handoff for humans and AI contributors. Read it before editing.

## Authority order

1. The current user's explicit request.
2. This root `AGENTS.md`.
3. `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, and `TASKS.md`.
4. The nearest scoped `agents.md` for a subsystem.
5. `docs/lineage/`, `RESEARCH.md`, and `refocus_os_guide_Final.md` as historical evidence only.

If documents conflict, follow the higher source and repair or remove the stale lower source in the same focused change.

## Non-negotiable repository rules

- Keep one canonical implementation per responsibility. Extend it; do not create a parallel MVP, alternate orchestrator, duplicate schema, second test tree, or repeat roadmap.
- State `runnable`, `prototype`, or `planned` accurately. Never turn architectural intent into a shipped claim.
- Search existing branches, issues, and pull requests before starting work. Update or close overlapping work instead of opening another repeat PR.
- Keep a change scoped. Do not reformat, rename, or “improve” unrelated files.
- Do not commit runtime data, generated feeds, secrets, caches, local databases, or virtual environments.
- Do not add dependencies without a clear need, a manifest and lockfile where supported, and tests in the same change.
- Preserve the project-state fail-closed boundary; never promote fixture extracts as canonical governance data.
- Stone is final authority. No agent may self-promote a proposal, branch, artifact, or harness revision into canonical state.

## Required workflow

1. Read `README.md`, `ARCHITECTURE.md`, and `TASKS.md`.
2. Inspect `git status` and search for the existing implementation before editing.
3. Make the smallest coherent change and delete documentation it clearly supersedes.
4. Run `scripts/verify-repo.sh` from the repository root.
5. Report exactly what changed, what was verified, and what remains planned.

The required path must remain usable from a fresh clone with Git and Python 3.11+ only.
