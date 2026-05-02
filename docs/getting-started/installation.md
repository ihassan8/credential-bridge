# Installation

## Requirements

- Python 3.8+
- pip

## Install from PyPI

```bash
pip install credential-bridge
```

## Development install

```bash
git clone https://github.com/vertex-ai-automations/credential-bridge
cd credential-bridge
pip install -e ".[dev]"
```

## Verify installation

```bash
cb --help
```

You should see the unified CLI with vault, keyring, env, and wizard subcommands.

## Backend prerequisites

=== "HashiCorp Vault"
    - A running HashiCorp Vault server
    - Set `VAULT_ADDR` environment variable: `export VAULT_ADDR=https://vault.example.com`
    - A valid token or AppRole credentials

=== "System Keyring"
    - Windows: Windows Credential Manager (built-in)
    - Linux: `python3-secretstorage` + a running D-Bus Secret Service (e.g. GNOME Keyring)
    - macOS: macOS Keychain (built-in)

=== ".env File"
    - No prerequisites — just a writable directory
