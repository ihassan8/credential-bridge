# Vault CLI

The `cb vault` subcommand manages secrets in HashiCorp Vault.

## Global options

These options apply to every `cb vault` subcommand:

| Flag | Env var | Description |
|---|---|---|
| `--vault-url URL` | `VAULT_ADDR` | Vault server URL |
| `--vault-token TOKEN` | `VAULT_TOKEN` | Token authentication |
| `--vault-role-id ID` | `VAULT_ROLE_ID` | AppRole role ID |
| `--vault-secret-id ID` | `VAULT_SECRET_ID` | AppRole secret ID |
| `--mount-point MP` | — | KV-v2 mount point (default: `secret`) |
| `--service-name NAME` | — | Logging tag (default: `default_service`) |

## add

Add a new secret. Fails if the secret already exists.

```bash
cb vault add myapp/database \
  --secret user=admin \
  --secret pass=s3cr3t \
  --vault-token s.xxx
```

**Flags:**

| Flag | Required | Description |
|---|---|---|
| `NAME` | Yes | Secret path (e.g. `myapp/database`) |
| `--secret KEY=VALUE` | Yes (repeatable) | Key-value pair to store |

## get

Retrieve a secret and display it as JSON.

```bash
cb vault get myapp/database --vault-token s.xxx
```

Output:

```json
{
  "user": "admin",
  "pass": "s3cr3t"
}
```

## update

Update one or more fields of an existing secret (patch — unspecified fields are unchanged).

```bash
cb vault update myapp/database --secret pass=new-pass --vault-token s.xxx
```

## delete

Permanently delete a secret (all versions).

```bash
cb vault delete myapp/database --yes --vault-token s.xxx
```

**Flags:**

| Flag | Description |
|---|---|
| `--yes` | Skip confirmation prompt |

## list

List all secret keys at a given path.

```bash
cb vault list myapp/          # list keys under myapp/
cb vault list                 # list keys at mount root
```

Output:

```
myapp/database
myapp/cache
myapp/api
```
