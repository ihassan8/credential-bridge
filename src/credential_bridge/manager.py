# src/credential_bridge/manager.py
from typing import Any, Dict, List, Type

from .backends.base import BaseSecretBackend
from .backends.env_file import EnvFileBackend
from .backends.keyring import KeyringBackend
from .backends.vault import VaultBackend
from .exceptions import BackendNotRegisteredError


class SecretsManager:
    """Facade over all registered secret backends."""

    _registry: Dict[str, Type[BaseSecretBackend]] = {}

    @classmethod
    def register_backend(cls, name: str, backend_cls: Type[BaseSecretBackend]) -> None:
        """Register a backend class under a name."""
        cls._registry[name] = backend_cls

    def __init__(self, backend: str, **kwargs: Any) -> None:
        if backend not in self._registry:
            available = list(self._registry.keys())
            raise BackendNotRegisteredError(
                f"Unknown backend '{backend}'. Available: {available}"
            )
        self._backend: BaseSecretBackend = self._registry[backend](**kwargs)

    @property
    def backend(self) -> BaseSecretBackend:
        """The underlying backend instance."""
        return self._backend

    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        self._backend.add_secret(name, secret)

    def get_secret(self, name: str) -> Dict[str, Any]:
        return self._backend.get_secret(name)

    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        self._backend.update_secret(name, secret)

    def delete_secret(self, name: str) -> None:
        self._backend.delete_secret(name)

    def list_secrets(self, path: str = "") -> List[str]:
        return self._backend.list_secrets(path)


# Register built-in backends
SecretsManager.register_backend("vault", VaultBackend)
SecretsManager.register_backend("keyring", KeyringBackend)
SecretsManager.register_backend("env", EnvFileBackend)
