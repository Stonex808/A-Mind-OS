# PHONE-ONLY WORKFLOW (Termux + Acode)

1. `pkg install python git openssh`
2. `pip install jsonschema structlog`  # (chromadb if you add it later)
3. `cd ~/A-Mind-OS`
4. `bash scripts/setup.sh`
5. `cd services/orchestrator`
6. `python local_demo.py --stdin`   # or `--socket`

**Pro tip:** Use Acode for editing, Termux for git push. All stdlib except the two above.
Data dir is gitignored — create it manually first run.
