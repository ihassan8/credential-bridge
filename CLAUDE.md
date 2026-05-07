# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**credential-bridge** is a Python 3.8+ secrets management library with a plugin backend architecture. It supports HashiCorp Vault (KV-v2), OS system keyring, and .env files through a unified interface. Ships five CLI entry points: `cb`, `vault-cli`, `keyring-cli`, `env-cli`, and `run-wizard`.

## Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all unit tests
pytest tests/unit/

# Run a single test file or specific test
pytest tests/unit/test_manager.py
pytest tests/unit/test_vault_backend.py::TestVaultBackend::test_add_secret

# Run integration tests (requires external services)
pytest tests/integration/ -m integration

# Serve docs locally (Zensical — uses zensical.toml)
zensical serve

# Build docs
zensical build

# Lint
ruff check src/

# Type check
mypy src/
```

Version is auto-generated from git tags via `setuptools_scm` — never commit `_version.py` (it is in `.gitignore`). Run `pip install -e .` to regenerate it after tagging.

## Architecture

```
src/credential_bridge/
├── backends/
│   ├── base.py          # BaseSecretBackend ABC — 5 abstract methods + backend_name
│   ├── vault.py         # VaultBackend: HashiCorp Vault KV-v2
│   ├── keyring.py       # KeyringBackend: OS keyring (JSON-serialised dict per entry)
│   └── env_file.py      # EnvFileBackend: .env file CRUD with atomic writes
├── cli/
│   ├── main.py          # Unified `cb` entry point (Typer, composes sub-apps)
│   ├── _output.py       # Shared Rich helpers: print_success/error/result/table
│   ├── vault_cli.py     # vault-cli (Typer + Rich)
│   ├── keyring_cli.py   # keyring-cli (Typer + Rich)
│   └── env_cli.py       # env-cli (Typer + Rich)
├── exceptions.py        # Typed hierarchy: CredentialBridgeError → BackendError → ...
├── manager.py           # SecretsManager facade + class-level backend registry
├── prompt_wizard.py     # Interactive wizard (prompt_toolkit)
└── utils.py             # Config I/O (~/.vault_config.json), get_session()
```

**Key design decisions:**
- `BaseSecretBackend` enforces `backend_name` via `__init_subclass__` — forgetting to set it raises `TypeError` at class definition time.
- `SecretsManager._registry` is a class-level dict. `register_backend("name", MyBackend)` is how third-party backends plug in. Tests must use a `clean_registry` autouse fixture to isolate state.
- `VaultBackend` URL resolution: `vault_url` arg → `VAULT_ADDR` env var → `~/.vault_config.json` → `ConfigurationError`.
- `VaultBackend(persist=False)` is the default — credentials are NOT written to `~/.vault_config.json` unless `persist=True` is explicitly passed.
- `KeyringBackend` serialises the secret dict to JSON before storing (keyring stores one string per key). `get_secret` deserialises on retrieval.
- `EnvFileBackend` uses `os.replace()` for atomic writes (write to `.env.tmp`, rename). Values with spaces or special chars are double-quoted.
- All logging goes through `PyLogShield` for sensitive data masking. Both `VaultBackend` and `KeyringBackend` accept an optional `logger: PyLogShield` parameter.
- TLS verification is enabled by default (`verify=True`). Pass `cert="/path/to/ca.pem"` for custom CA bundles.
- `get_session()` sets `trust_env = False` — the requests session does NOT pick up system proxy env vars unless `proxies` is explicitly passed.
- `KeyringBackend.list_secrets()` always raises `KeyringError`; Windows Credential Manager and macOS Keychain don't expose enumeration APIs.
- `EnvFileBackend.add_secret(name, {...})` writes a `# name` comment block above the key-value pairs. `get_secret(name)` resolves either a single key or all keys under a matching comment block.
- `EnvFileBackend(load_into_environ=True)` syncs written/updated values into `os.environ` immediately.
- `VaultBackend` exposes version-management helpers beyond the abstract interface: `delete_secret_versions`, `undelete_secret_versions`, `destroy_secret_versions`, and `read_secret_metadata`.
- On Windows, `save_config()` cannot set file permissions to 0o600 and issues a `UserWarning` instead; `cli/_output.py` reconfigures stdout/stderr to UTF-8 to handle Rich's box-drawing characters.

## Exception Hierarchy

```
CredentialBridgeError
├── BackendError
│   ├── VaultError
│   │   ├── VaultAuthError          — bad token / AppRole
│   │   ├── VaultConnectionError    — unreachable server
│   │   └── VaultSecretNotFoundError — secret path does not exist
│   ├── KeyringError
│   └── EnvFileError
│       ├── EnvFileNotFoundError    — key not found
│       └── EnvFileKeyExistsError   — add_secret on existing key
├── BackendNotRegisteredError
└── ConfigurationError
```

## Backwards Compatibility

`VaultManager` and `KeyringManager` are aliases for `VaultBackend` and `KeyringBackend` in `__init__.py`. Existing code using the old names continues to work.

## Docs

MkDocs + Material theme. Content at `docs/`. API reference pages in `docs/reference/` are auto-generated from numpy-style docstrings via `mkdocstrings`. Keep docstrings in numpy format when adding or modifying public methods.
