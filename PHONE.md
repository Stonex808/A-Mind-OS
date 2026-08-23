# Phone-only workflow (Termux + editor)

The canonical path needs only Git and Python 3.11+:

```bash
pkg install git python
git clone https://github.com/Stonex808/A-Mind-OS.git
cd A-Mind-OS
scripts/verify-repo.sh
```

Use `scripts/dev.sh` to keep demo artifacts under `data/`. No `pip`, Node, Rust, or manually created data directory is required for the current offline path.
