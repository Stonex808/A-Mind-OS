# Codex Phase 1 + Phase 2 Prompt

Use this file when kicking off Codex Cloud work on A-Mind-OS.

## Instructions for Codex

Read the repository and act as a senior software architect implementing the A-Mind-OS MVP.

Before coding, read these files in order:

1. `README_MVP.md`
2. `ARCHITECTURE_MVP.md`
3. `TASKS.md`

## Mission

Audit the repository against the current MVP docs, then implement only the highest-value unfinished work from **Phase 1** and **Phase 2** in `TASKS.md`.

Focus on making the repo more runnable, more understandable, and more structurally ready for planner/worker expansion.

## Priority Targets

### Phase 1
- tighten the visible shell and repo framing
- improve shell usability and status visibility
- add contributor-friendly orientation where missing
- ensure shell-related smoke instructions are accurate

### Phase 2
- define the orchestrator backbone clearly
- add a shared task schema if one is missing
- create or improve the orchestrator service boundary
- add task routing/dispatch structure
- add structured execution logging
- add smoke tests for orchestrator task flow

## Constraints

- Prefer working code over placeholder theory.
- Keep the project local-first.
- Do not attempt full RL, full MATPO, NHA, eBPF SysSec, or other deferred architecture work.
- Do not rewrite unrelated subsystems.
- Do not rename the project.
- Keep service boundaries clean and modular.
- Update docs if implementation changes reality.

## Deliverables

Produce:

1. the code changes for the highest-value unfinished Phase 1 and Phase 2 work
2. updated docs where needed
3. tests or smoke scripts where practical
4. a summary of:
   - what was changed
   - what remains unfinished in Phase 1 and Phase 2
   - what should be done next

## Definition of a Good Result

A good result means:

- the shell is more usable or truthful
- the orchestrator boundary is clearer or more real
- the repo is easier to continue from
- no giant speculative rewrite was attempted
