# HUD & AI Terminal (Tauri/React) — agents.md

**Status:** local demo / prototype  
**Best contributor on-ramp:** run the orchestrator local demo first, then serve `ui/shell/` with `python -m http.server 4173 --directory ui/shell` to test the visible offline shell.  
**Current runnable scope:** a static HTML/CSS/JS prototype that demonstrates intent entry, local activity, visible controls, and an emergency stop without backend coupling.  
**Long-term scope:** a Tauri/React HUD with signed real-time bindings to the orchestrator.

**Role:** Minimal Surface for Intents, Budgets, Alerts  
**Dependencies (target architecture):** Node.js, npm/yarn, Rust, Cargo, Tauri CLI, React, TypeScript

## Execution Plan
1. Keep the current static prototype obvious, keyboard-friendly, and offline-first.
2. Scaffold transparent frameless Tauri app.
3. Panels: AI Terminal, Task Log, Security Alerts.
4. Bind **Super** (voice listen) and **Alt+Enter** (intent capture).
5. WebSocket to Orchestrator with ed25519 handshake.
6. Tray indicator + budget sliders.

## Verification
- Current prototype: local page loads, visible controls work, and `Ctrl+Enter` submits a local intent entry.
- Future scope: Alt+Enter sends signed intent.
- Future scope: HUD mirrors Orchestrator state in real time.
