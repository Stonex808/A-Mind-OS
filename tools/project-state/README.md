# A-Mind Project State Integration Gate

This directory records the fail-closed production placement for Slice A.

The full verified Slice A source and repository overlay are preserved in the checkpoint release bundle. Production compilation requires complete canonical inputs at:

- `governance/01_AUTHORITY_MATRIX.yaml`
- `governance/02_PROJECT_REGISTRY.yaml`

The standalone v1.1.0 extracts are fixtures only. They must never be copied into these paths or represented as the complete canonical stores.

Run the source gate before compiling project-state views:

```bash
python tools/project-state/scripts/check_canonical_sources.py
```
