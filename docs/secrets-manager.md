# SecretsManager

`SecretsManager` is a facade that routes operations to any registered backend through a single consistent API.

## Basic usage

```python
from credential_bridge import SecretsManager

# Pick a backend — all backends share the same 5 methods
sm = SecretsManager("vault",   vault_token="s.xxx")
sm = SecretsManager("keyring", service_name="myapp")
sm = SecretsManager("env",     path=".env")

# Uniform API across all backends
sm.add_secret("myapp/db", {"user": "admin", "pass": "s3cr3t"})
result = sm.get_secret("myapp/db")
sm.update_secret("myapp/db", {"pass": "new_pass"})
sm.delete_secret("myapp/db")
keys = sm.list_secrets()
```

## Switching backends

```python
# Development: .env file
sm = SecretsManager("env", path=".env")

# Production: swap to Vault — no other code changes needed
sm = SecretsManager("vault", vault_url="https://vault.example.com", vault_token="s.xxx")
```

## Accessing backend-specific methods

The `backend` property exposes the underlying instance for operations beyond the five-method contract:

```python
sm = SecretsManager("vault", vault_token="s.xxx")

# Access Vault-specific operations
vault = sm.backend
meta = vault.read_secret_metadata("myapp/db")
vault.delete_secret_versions("myapp/db", [1, 2])
```

## Registered backends

| Name | Class | Key constructor args |
|---|---|---|
| `"vault"` | `VaultBackend` | `vault_url`, `vault_token` or `vault_role_id`+`vault_secret_id` |
| `"keyring"` | `KeyringBackend` | `service_name` |
| `"env"` | `EnvFileBackend` | `path` |

## Custom backends

Implement `BaseSecretBackend` and register it:

```python
from typing import Any, Dict, List
from credential_bridge import SecretsManager
from credential_bridge.backends.base import BaseSecretBackend


class AWSSecretsBackend(BaseSecretBackend):
    backend_name = "aws"

    def __init__(self, region: str = "us-east-1", **kwargs: Any) -> None:
        import boto3
        self.client = boto3.client("secretsmanager", region_name=region)

    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        import json
        self.client.create_secret(Name=name, SecretString=json.dumps(secret))

    def get_secret(self, name: str) -> Dict[str, Any]:
        import json
        resp = self.client.get_secret_value(SecretId=name)
        return json.loads(resp["SecretString"])

    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        import json
        self.client.update_secret(SecretId=name, SecretString=json.dumps(secret))

    def delete_secret(self, name: str) -> None:
        self.client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)

    def list_secrets(self, path: str = "") -> List[str]:
        resp = self.client.list_secrets()
        return [s["Name"] for s in resp["SecretList"]]


# Register once at application startup
SecretsManager.register_backend("aws", AWSSecretsBackend)

# Use exactly like any built-in backend
sm = SecretsManager("aws", region="eu-west-1")
sm.add_secret("myapp/database", {"user": "admin", "pass": "s3cr3t"})
```

!!! info "backend_name required"
    Every `BaseSecretBackend` subclass must define a non-empty `backend_name` class attribute. Omitting it raises `TypeError` at class definition time.

## Error handling

```python
from credential_bridge import (
    SecretsManager,
    BackendNotRegisteredError,
    CredentialBridgeError,
)

try:
    sm = SecretsManager("unknown")
except BackendNotRegisteredError as e:
    print(f"Backend not found: {e}")

try:
    sm = SecretsManager("vault", vault_token="s.xxx")
    sm.get_secret("myapp/db")
except CredentialBridgeError as e:
    print(f"Operation failed: {e}")
```

## Thread safety

`SecretsManager._registry` is a class-level dict shared across all instances and all threads. `register_backend()` is safe to call at module load time but should not be called concurrently during operation.
