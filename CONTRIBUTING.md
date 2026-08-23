# Contributing

Start with `AGENTS.md`; it applies equally to human and AI-authored changes. Clone the repository, create one narrowly named branch unless the owner explicitly requests a direct `Main` maintenance commit, and run `scripts/verify-repo.sh` before and after the change.

Before opening a pull request, search open PRs and branches for the same outcome. Prefer updating one current PR or closing a superseded one over stacking replacements. A PR should explain the user-visible outcome, list the canonical files it changes, identify any removed overlap, and include the exact verification result.

Keep generated state under ignored `data/` paths. Never commit secrets. Update dependency manifests and lockfiles together using the ecosystem's package manager; do not hand-edit a lockfile to make an alert disappear.
