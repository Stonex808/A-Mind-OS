    # GRACE Memory Service — agents.md

    **Role:** Embeddings, Retrieval, & Audit Spine  
    **Dependencies:** python >= 3.11, sentence‑transformers, faiss-cpu or chromadb

    ## Execution Plan
    1. Load embedding model; init index & metadata store.
2. Implement `/embed`, `/log_and_embed`, `/search` APIs.
3. Enforce PII‑redaction, TTLs, hot/warm/cold tiers.
4. Unit: `grace.service` with `Restart=always`.

    ## Verification
    - Embeddings correct dims
- Semantic search retrieves expected entries
