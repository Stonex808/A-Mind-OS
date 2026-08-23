# GRACE memory service

**Status:** planned. The runnable memory implementation is `python_core/memory/memory_integration.py`; do not create another local store here.

This directory preserves the future retrieval-service boundary: embeddings, hybrid search, reranking, TTLs, and audit integration. Any implementation must reuse the canonical persistence policy, keep data local by default, declare and lock new dependencies, and add evaluation evidence showing that it improves on deterministic JSON recall.

Start only after the admitted IPC slice in `TASKS.md`. Verification must cover redaction/refusal, retention, retrieval quality, restart behavior, and a no-network mode.
