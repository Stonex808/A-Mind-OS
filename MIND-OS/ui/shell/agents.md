    # HUD & AI Terminal (Tauri/React) — agents.md

    **Role:** Minimal Surface for Intents, Budgets, Alerts  
    **Dependencies:** Node.js, npm/yarn, Rust, Cargo, Tauri CLI, React, TypeScript

    ## Execution Plan
    1. Scaffold transparent frameless Tauri app.
2. Panels: AI Terminal, Task Log, Security Alerts.
3. Bind **Super** (voice listen) and **Alt+Enter** (intent capture).
4. WebSocket to Orchestrator with ed25519 handshake.
5. Tray indicator + budget sliders.

    ## Verification
    - Alt+Enter sends signed intent
- HUD mirrors Orchestrator state in real time
