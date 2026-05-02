# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**credential-bridge** is a Python library (Production/Stable) that provides a unified interface for secrets management across HashiCorp Vault (KV2) and the OS system keyring. It ships three entry points: `keyring-cli`, `vault-cli`, and `run-wizard`.

## Development Setup

```bash
# Install in editable mode with optional image support
pip install -e ".[image]"

# Install dev dependencies
pip install -r requirements.txt

# Serve docs locally
mkdocs serve
```

Version is auto-generated from git tags via `setuptools_scm` — there is no hardcoded version string to update.

## Architecture

```
credential_bridge/
├── vault_manager.py      # VaultManager: wraps hvac for HashiCorp Vault KV2 ops
├── keyring_manager.py    # KeyringManager: wraps the keyring library for OS secrets
├── utils.py              # Config I/O (~/.vault_config.json), domain→Vault URL routing,
│                         # error classes (VaultManagerError, KeyringManagerError),
│                         # session/proxy helpers
├── prompt_wizard.py      # Interactive menu wizard (prompt_toolkit); caches credentials,
│                         # calls both managers
└── cli/
    ├── vault_cli.py      # argparse CLI for VaultManager
    └── keyring_cli.py    # argparse CLI for KeyringManager
```

**Key design choices:**
- Runtime Vault address is resolved from domain-based routing logic in `utils.py`, falling back to an environment variable, then `~/.vault_config.json`.
- `PyLogShield` is used project-wide to mask sensitive values in log output — all logging should go through it, not the stdlib logger directly.
- Auth to Vault supports two flows: JWT token or AppRole (`role_id` + `secret_id`). Token refresh/TTL management lives in `VaultManager`.

## Docs

Documentation lives in `docs/` and is built with MkDocs + Material theme (`mkdocs.yml`). API reference pages under `docs/reference/` are auto-generated from numpy-style docstrings via `mkdocstrings`. Keep docstrings in numpy format when adding or modifying public methods.
