# SecretsManager

`SecretsManager` is a facade that lets you work with any backend through a single, consistent interface.

## Basic usage

```python
from credential_bridge import SecretsManager

# Create with any registered backend
sm = SecretsManager("vault", vault_token="s.xxx")
sm = SecretsManager("keyring", service_name="myapp")
sm = SecretsManager("env", path=".env")

# All backends share the same 5-method API
sm.add_secret(name, secret_dict)
sm.get_secret(name)
sm.update_secret(name, secret_dict)
sm.delete_secret(name)
sm.list_secrets(path="")
```

## Register a custom backend

```python
from credential_bridge import SecretsManager
from credential_bridge.backends.base import BaseSecretBackend
from typing import Any, Dict, List


class MyCustomBackend(BaseSecretBackend):
    backend_name = "mycustom"

    def __init__(self, **kwargs):
        self.config = kwargs

    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        # your implementation
        ...

    def get_secret(self, name: str) -> Dict[str, Any]:
        ...

    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        ...

    def delete_secret(self, name: str) -> None:
        ...

    def list_secrets(self, path: str = "") -> List[str]:
        ...


SecretsManager.register_backend("mycustom", MyCustomBackend)
sm = SecretsManager("mycustom", my_option="value")
```

## Access the underlying backend

```python
sm = SecretsManager("vault", vault_token="s.xxx")
vault_backend = sm.backend  # VaultBackend instance
vault_backend.read_secret_metadata("myapp/db")  # Vault-specific method
```
