# Planned systemd packaging

These units document the intended Refocus-derived boot graph and executable names. The referenced `/usr/local/bin/refocus-*` programs are not shipped by this repository, so the units must not be installed or described as runnable yet.

Keep them as packaging contracts until admitted IPC, authenticated services, sandboxing, and installation tooling are implemented and tested. `scripts/verify-repo.sh` is the only current startup/acceptance path.
