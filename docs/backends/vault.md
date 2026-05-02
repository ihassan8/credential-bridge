# HashiCorp Vault Backend

Use `VaultBackend` when you need centralized, auditable secrets management for teams or production systems.

## Authentication

=== "Token"

    ```python
    from credential_bridge import VaultBackend

    backend = VaultBackend(
        vault_url="https://vault.example.com",  # or set VAULT_ADDR env var
        vault_token="s.your-token",             # or set VAULT_TOKEN env var
    )
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

!!! security "VAULT_ADDR environment variable"
    Set `VAULT_ADDR` in your environment instead of hardcoding the URL:
    ```bash
    export VAULT_ADDR=https://vault.example.com
    ```

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `vault_url` | `str \| None` | `None` | Vault server URL. Falls back to `VAULT_ADDR` env var. |
| `vault_token` | `str \| None` | `None` | Vault token. Mutually exclusive with AppRole. |
| `vault_role_id` | `str \| None` | `None` | AppRole role ID. |
| `vault_secret_id` | `str \| None` | `None` | AppRole secret ID. |
| `service_name` | `str` | `"default_service"` | Used as a logging tag only. |
| `mount_point` | `str` | `"secret"` | KV-v2 mount point. |
| `cert` | `str \| None` | `None` | SSL certificate path. |
| `proxies` | `dict \| None` | `None` | HTTP proxy settings. |
| `mask` | `bool` | `True` | Mask secret values in logs. |

## Operations

```python
# Add
backend.add_secret("myapp/database", {"user": "admin", "pass": "s3cr3t"})

# Get
secret = backend.get_secret("myapp/database")
print(secret["user"])  # admin

# Update (patch — only specified keys changed)
backend.update_secret("myapp/database", {"pass": "new-pass"})

# Delete (permanently removes all versions)
backend.delete_secret("myapp/database")

# List secrets at a path
keys = backend.list_secrets("myapp/")  # ["database", "cache"]
keys = backend.list_secrets()           # list root of mount_point
```

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `ConfigurationError: Vault URL not configured` | Neither `vault_url` nor `VAULT_ADDR` is set | Set `VAULT_ADDR` env var or pass `vault_url=` |
| `VaultAuthError: Token authentication failed` | Token is invalid or expired | Obtain a new token from Vault UI |
| `VaultConnectionError: Cannot connect` | Server unreachable | Check `VAULT_ADDR` and network |
| `ConfigurationError: No authentication method` | No token or AppRole provided | Pass `vault_token=` or both AppRole credentials |

## CLI equivalent

```bash
cb vault add myapp/db --secret user=admin --secret pass=s3cr3t
cb vault get myapp/db
cb vault update myapp/db --secret pass=new-pass
cb vault delete myapp/db --yes
cb vault list myapp/
```
