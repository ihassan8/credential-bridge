# Unified CLI (cb)

The `cb` command provides a single entry point for all backend operations.

## Installation

After `pip install credential-bridge`, the `cb` command is available:

```bash
cb --help
```

## Command structure

```
cb vault   add|get|update|delete|list  [options]
cb keyring add|get|update|delete       [options]
cb env     add|get|update|delete|list  [options]
cb wizard
```

## Quick examples

```bash
# Vault — add a secret
cb vault add myapp/db --secret user=admin --secret pass=s3cr3t \
  --vault-url https://vault.example.com --vault-token s.xxx

# Keyring — get a secret
cb keyring get github_token --service-name dev

# .env — list all keys
cb env list

# Launch interactive wizard
cb wizard
```

## Environment variables

| Variable | Used by | Description |
|---|---|---|
| `VAULT_ADDR` | vault subcommand | Vault server URL |
| `VAULT_TOKEN` | vault subcommand | Vault authentication token |
| `VAULT_ROLE_ID` | vault subcommand | AppRole role ID |
| `VAULT_SECRET_ID` | vault subcommand | AppRole secret ID |
