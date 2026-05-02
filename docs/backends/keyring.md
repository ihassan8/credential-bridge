# System Keyring Backend

Use `KeyringBackend` to store credentials in the OS credential store: Windows Credential Manager, macOS Keychain, or Linux Secret Service.

## Usage

```python
from credential_bridge import KeyringBackend

backend = KeyringBackend(service_name="myapp")

# Add
backend.add_secret("github_token", {"github_token": "ghp_xxx"})

# Get
secret = backend.get_secret("github_token")
print(secret["github_token"])  # ghp_xxx

# Update
backend.update_secret("github_token", {"github_token": "ghp_new"})

# Delete
backend.delete_secret("github_token")
```

## Multi-field secrets

```python
backend.add_secret("database", {"user": "admin", "pass": "s3cr3t", "host": "localhost"})
secret = backend.get_secret("database")
# {"user": "admin", "pass": "s3cr3t", "host": "localhost"}
```

The dict is serialized as JSON before storing, so any JSON-serializable dict is supported.

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `service_name` | `str` | `"default_service"` | Groups secrets under this service name. |
| `mask` | `bool` | `True` | Mask secret values in logs. |

## Platform limitations

!!! warning "list_secrets() not supported"
    `list_secrets()` raises `NotImplementedError` on all platforms. Windows Credential Manager
    and macOS Keychain do not expose key enumeration APIs.

!!! cross-platform "Linux setup"
    On headless Linux, install `python3-secretstorage` and ensure a D-Bus Secret Service
    (e.g. GNOME Keyring or KeePass with Secret Service plugin) is running.

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `KeyringError: not found` | Key doesn't exist | Use `add_secret()` first |
| `KeyringError: does not exist` | Calling `update_secret()` on missing key | Use `add_secret()` first |

## CLI equivalent

```bash
cb keyring add github_token --secret github_token=ghp_xxx --service-name myapp
cb keyring get github_token --service-name myapp
cb keyring update github_token --secret github_token=ghp_new --service-name myapp
cb keyring delete github_token --service-name myapp --yes
```
