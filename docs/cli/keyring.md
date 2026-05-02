# Keyring CLI

The `cb keyring` subcommand manages secrets in the OS credential store (Windows Credential Manager, macOS Keychain, or Linux Secret Service).

## Global options

| Flag | Default | Description |
|---|---|---|
| `--service-name NAME` | `default_service` | Groups secrets under this service name |

## add

Store a new secret in the keyring. Fails if the key already exists.

```bash
cb keyring add github_token \
  --secret github_token=ghp_xxx \
  --service-name dev
```

**Flags:**

| Flag | Required | Description |
|---|---|---|
| `NAME` | Yes | Key name to store |
| `--secret KEY=VALUE` | Yes (repeatable) | Key-value pair(s) to store |
| `--service-name NAME` | No | Service namespace |

## get

Retrieve a secret from the keyring and display it as JSON.

```bash
cb keyring get github_token --service-name dev
```

Output:

```json
{
  "github_token": "ghp_xxx"
}
```

## update

Replace the value of an existing keyring entry.

```bash
cb keyring update github_token \
  --secret github_token=ghp_new \
  --service-name dev
```

## delete

Remove a secret from the keyring.

```bash
cb keyring delete github_token --service-name dev --yes
```

**Flags:**

| Flag | Description |
|---|---|
| `--yes` | Skip confirmation prompt |

## Notes

!!! warning "No list support"
    `cb keyring list` is not available. The underlying OS APIs do not support
    enumerating keys by service name.
