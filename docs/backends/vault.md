# HashiCorp Vault Backend

## When to use

`VaultBackend` is the right choice whenever you need centralised, auditable secrets
management across a team or in a production environment. Vault provides KV-v2
multi-version storage, token and lease rotation, fine-grained access policies, and a
full audit log — none of which are available from local alternatives. If you are
already using HashiCorp tooling, or you are running workloads in a CI/CD pipeline that
has Vault configured, this backend gives you first-class integration with zero
additional infrastructure.

## Prerequisites

Set `VAULT_ADDR` in your environment so you don't have to pass the URL on every call:

```bash
export VAULT_ADDR=https://vault.example.com
```

The `VAULT_TOKEN` and `VAULT_ROLE_ID` / `VAULT_SECRET_ID` environment variables are
also read automatically if the corresponding constructor arguments are omitted.

## Authentication

=== "Token"

    ```python
    from credential_bridge import VaultBackend

    # Explicit arguments
    backend = VaultBackend(
        vault_url="https://vault.example.com",
        vault_token="s.your-token",
    )

    # From environment — no arguments needed when VAULT_ADDR and VAULT_TOKEN are set
    import os
    os.environ["VAULT_ADDR"] = "https://vault.example.com"
    os.environ["VAULT_TOKEN"] = "s.your-token"
    backend = VaultBackend()
    ```

=== "AppRole"

    ```python
    from credential_bridge import VaultBackend

    backend = VaultBackend(
        vault_url="https://vault.example.com",
        vault_role_id="your-role-id",
        vault_secret_id="your-secret-id",
    )
    ```

    AppRole credentials can also be supplied via the `VAULT_ROLE_ID` and
    `VAULT_SECRET_ID` environment variables.

!!! warning "Token and AppRole are mutually exclusive"
    Providing both a `vault_token` **and** AppRole credentials raises
    `ConfigurationError`. Choose one method per `VaultBackend` instance.

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `vault_url` | `str \| None` | `None` | Vault server URL. See [URL resolution order](#url-resolution-order). |
| `vault_token` | `str \| None` | `None` | Token auth. Mutually exclusive with AppRole. |
| `vault_role_id` | `str \| None` | `None` | AppRole role ID. Requires `vault_secret_id`. |
| `vault_secret_id` | `str \| None` | `None` | AppRole secret ID. Requires `vault_role_id`. |
| `service_name` | `str` | `"default_service"` | Logging tag only — not used in Vault API calls. |
| `mount_point` | `str \| None` | current OS username | KV-v2 mount point. Defaults to the current OS username (`getpass.getuser()`). Pass an explicit string to override. |
| `proxies` | `dict \| None` | `None` | HTTP proxy settings passed to the `requests` session. |
| `cert` | `str \| None` | `None` | Path to a custom CA certificate. `None` uses the system CA bundle. |
| `log_level` | `LogLevel \| str` | `LogLevel.WARNING` | Minimum log level for the internal logger. |
| `logger` | `PyLogShield \| None` | `None` | Provide your own `PyLogShield` logger instance. |
| `mask` | `bool` | `True` | Mask secret values in log output. |
| `persist` | `bool` | `False` | Save credentials to `~/.vault_config.json` for future sessions. |

## URL resolution order

The Vault server address is resolved in this order, stopping at the first match:

1. `vault_url` constructor argument
2. `VAULT_ADDR` environment variable
3. `vault_addr` key in `~/.vault_config.json`
4. `ConfigurationError` — no address could be found

## The `persist` parameter

By default (`persist=False`) credentials are **not** written to disk. Pass
`persist=True` to save the Vault address and credentials to
`~/.vault_config.json` so that future `VaultBackend()` calls with no arguments
can authenticate without repeating them.

```python
# Save credentials once
backend = VaultBackend(
    vault_url="https://vault.example.com",
    vault_token="s.your-token",
    persist=True,   # writes to ~/.vault_config.json
)

# Subsequent calls need no arguments
backend = VaultBackend()
```

!!! warning "File permissions"
    On POSIX systems the config file is created with mode `0600` (owner read/write
    only). On Windows, normal NTFS write permissions are used and a `UserWarning` is
    emitted — consider restricting access manually.

## Custom TLS certificate

Pass `cert` to verify the Vault server against a custom CA bundle instead of the
system trust store:

```python
backend = VaultBackend(
    vault_url="https://vault.internal",
    vault_token="s.xxx",
    cert="/path/to/internal-ca.pem",
)
```

TLS verification is always enabled — there is no option to disable it.

## CRUD operations

### add_secret

Writes a new KV-v2 secret or creates a new version if the path already exists.

```python
backend.add_secret("myapp/database", {"user": "admin", "pass": "s3cr3t"})
```

CLI equivalent:

```bash
cb vault add myapp/database --secret user=admin --secret pass=s3cr3t --vault-token s.xxx
```

### get_secret

Returns the latest version of a secret as a `dict`.

```python
secret = backend.get_secret("myapp/database")
# {"user": "admin", "pass": "s3cr3t"}
print(secret["user"])  # admin
```

Raises `VaultSecretNotFoundError` if the path does not exist.

CLI equivalent:

```bash
cb vault get myapp/database --vault-token s.xxx
```

### update_secret

Patches an existing secret — only the keys you supply are changed; all other
fields in the current version are preserved.

```python
backend.update_secret("myapp/database", {"pass": "new_pass"})
# {"user": "admin", "pass": "new_pass"}  — user is unchanged
```

Raises `VaultSecretNotFoundError` if the path does not exist.

CLI equivalent:

```bash
cb vault update myapp/database --secret pass=new_pass --vault-token s.xxx
```

### delete_secret

Permanently deletes a secret **and all its versions**. This is equivalent to
`delete_metadata_and_all_versions` in the Vault API and cannot be undone.

```python
backend.delete_secret("myapp/database")
```

CLI equivalent:

```bash
cb vault delete myapp/database --yes --vault-token s.xxx
```

### list_secrets

Lists secret keys under a path prefix. Pass an empty string (the default) to
list the root of the current mount point.

```python
keys = backend.list_secrets("myapp/")   # ["database", "cache"]
keys = backend.list_secrets()           # list root of mount_point
```

CLI equivalent:

```bash
cb vault list myapp/
cb vault list
```

## Version management

KV-v2 keeps a history of every write. The following methods let you manage
individual versions without touching others.

### Soft delete

Marks versions as deleted. The data is preserved and can be restored with
`undelete_secret_versions`.

```python
backend.delete_secret_versions("myapp/db", [1, 2])
```

### Undelete (restore)

Restores previously soft-deleted versions.

```python
backend.undelete_secret_versions("myapp/db", [1])
```

### Permanent destroy

Irreversibly removes the data for specific versions. Unlike `delete_secret`, other
versions of the same path are not affected.

```python
backend.destroy_secret_versions("myapp/db", [2])
```

## Metadata and config operations

### read_secret_metadata

Returns version history, creation time, and custom metadata for a secret path.

```python
meta = backend.read_secret_metadata("myapp/db")
# {
#   "data": {
#     "versions": { "1": {...}, "2": {...} },
#     "current_version": 2,
#     ...
#   }
# }
```

### get_config

Returns the KV engine configuration for the current mount point (e.g. maximum
number of versions to keep).

```python
cfg = backend.get_config()
```

## Token refresh behaviour

Before every operation `VaultBackend` calls `_refresh_token_if_needed()`, which
looks up the current token's TTL. If the TTL is below **5 minutes** (300 seconds)
the token is automatically renewed in place, so long-running processes don't need
to handle token expiry manually. If the renewal fails because the token is non-renewable, a `VaultAuthError` is raised. If Vault is unreachable during the refresh check (network error, timeout, server down), a `VaultConnectionError` is raised immediately — the error is not silently swallowed.

## Error handling

```python
from credential_bridge import (
    VaultAuthError,
    VaultConnectionError,
    VaultSecretNotFoundError,
    VaultError,
    ConfigurationError,
)

try:
    secret = backend.get_secret("myapp/missing")
except VaultSecretNotFoundError:
    print("Secret path does not exist")
except VaultAuthError:
    print("Token expired or invalid")
except VaultConnectionError:
    print("Cannot reach Vault server")
except VaultError as e:
    print(f"Other Vault error: {e}")
except ConfigurationError as e:
    print(f"Configuration problem: {e}")
```

### Common errors

| Exception | Cause | Resolution |
|---|---|---|
| `ConfigurationError` | No Vault URL found (checked first, before any other setup), both Token and AppRole provided, or invalid logger type | Set `VAULT_ADDR` / pass `vault_url=`; choose one auth method |
| `VaultAuthError` | Token invalid or expired; AppRole credentials rejected; Forbidden response | Obtain a fresh token or verify AppRole credentials |
| `VaultConnectionError` | Server unreachable — bad URL, network issue, or Vault sealed | Check `VAULT_ADDR`, network connectivity, and Vault status |
| `VaultSecretNotFoundError` | Path does not exist in KV-v2 (`InvalidPath` from hvac) | Verify the path with `list_secrets()` |
| `VaultError` | Any other Vault operation failure | Inspect the exception message for details |

`VaultSecretNotFoundError`, `VaultAuthError`, and `VaultConnectionError` are all
subclasses of `VaultError`, which is itself a subclass of `BackendError`.
