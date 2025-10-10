# Refocus-OS Project Overview

This document provides a comprehensive overview of the Refocus-OS project, an AI-first, agent-centric operating system layer. It serves as a guide for developers and contributors, outlining the project's architecture, key components, and development conventions, all grounded in state-of-the-art research.

## Project Overview

Refocus-OS is an ambitious project to create an AI-native operating system layer on top of a custom Debian base. It reimagines the user-computer relationship by transforming the OS from a passive tool manager into a proactive, reasoning co-pilot. The system is designed to be headless, context-aware, and hardened against intelligent threats.

The core of Refocus-OS is a monolithic, agent-centric architecture where every system capability is implemented as an autonomous agent. These agents communicate and coordinate through a central Orchestrator, operating under the constant supervision of an adaptive AI defense system. This design choice is a deliberate move to leverage high-performance, low-latency Inter-Process Communication (IPC) mechanisms.

## Architecture

The system is built on a layered architecture:

*   **Layer 0: Hardware & Kernel:** A custom Debian base with a Linux kernel and eBPF instrumentation.
*   **Layer 1: Model Runtime:** A high-efficiency inference server for the foundation model.
*   **Layer 2: Hydra Defense System:** An adaptive integrity shield with LangSec, CodeSec, and SysSec guard models.
*   **Layer 3: IPC Message Bus:** A two-tiered IPC system with shared memory for high-performance communication and Unix domain sockets for general-purpose messaging.
*   **Layer 4: The Orchestrator & Services:** The central reasoning and coordination hub.
*   **Layer 5: Specialist Agents:** Independent, sandboxed workers that perform specific tasks.
*   **Layer 6: User Interface Layer:** A Tauri/React-based HUD and AI Terminal.

For a more detailed explanation of the architecture, please refer to the `ARCHITECTURE.md` and `RESEARCH.md` files.

## Key Components

*   **Unified LLM Core with Native Hybrid Attention (NHA):** The LLM core is a single, unified model that uses a hybrid attention mechanism inspired by the Qwen3-Next architecture (Gated DeltaNet + Gated Attention) to achieve extreme efficiency and long-context capabilities.
*   **MATPO-based Agent Core:** The Agent Core is built on the Multi-Agent Tool-Integrated Policy Optimization (MATPO) framework, which allows for the instantiation of multiple agent roles (Planner and Workers) within the single LLM instance.
*   **Orchestrator (`services/orchestrator/`):** The central reasoning and scheduling hub of the system, influenced by the DRAMA framework, using a Planner-Critic model for dynamic resource allocation.
*   **Hydra Defense System (`services/security/`):** A three-layered defense system consisting of:
    *   **LangSec (LG-A):** A two-stage model for prompt sanitization and injection defense.
    *   **CodeSec (LG-B):** For generated code safety analysis.
    *   **SysSec (LG-C):** A hybrid Transformer/GNN architecture for real-time syscall anomaly detection.
*   **ArtHippoNet Cognitive Architecture (`memory/`):** A human-inspired tripartite memory system with Episodic, Semantic, and Procedural memory.
*   **GRACE Service (`ops/ipc/`):** An advanced three-stage retrieval pipeline with hybrid search, reranking, and graph-augmented retrieval.
*   **UI Layer (`ui/shell/`):** A minimal graphical surface for interacting with the system.

## Building and Running

The project is still in the blueprint and boot specification phase. The following scripts are available for setting up the development environment and running the services:

*   **`scripts/setup.sh`:** Checks for the required dependencies (Python, Node.js, Rust).
*   **`scripts/dev.sh`:** A placeholder script that outlines the order in which the services should be started.

The system is designed to be deployed using `systemd` unit files, which can be found in the `systemd/units/` directory.

## Development Conventions

*   **Contracts First:** The development process starts with defining and validating JSON contracts for the agents in the `/config/contracts` directory.
*   **Security Gates:** All pull requests are required to pass LangSec/CodeSec checks and unit tests for the envelope schema.
*   **Policy Tuning:** The `config/economist.yaml` file is used to adjust the resource budgets for the agents.
*   **Trust and Transparency:** The project integrates formal verification (AgentGuard) for safety and Explainable AI (XAI) for transparency.

## Roadmap

The project has a clear roadmap with the following milestones:

*   **M1:** IPC bus, signed envelope schema, and GRACE MVP.
*   **M2:** Orchestrator IFN, MATPO planner, and economist budgets.
*   **M3:** Hydra Defense (LG-A/B/C), kernel hook, and kill-switch.
*   **M4:** Tauri HUD, AI Terminal bindings, and hotkeys.
*   **M5:** Reflection daemon and self-tuning policies.

For more information, please refer to the `README.md`, `ARCHITECTURE.md`, and `RESEARCH.md` files.
