# src/credential_bridge/manager.py
import threading
from typing import Any, Dict, List, Type

from .backends.base import BaseSecretBackend
from .backends.env_file import EnvFileBackend
from .backends.keyring import KeyringBackend
from .backends.vault import VaultBackend
from .exceptions import BackendNotRegisteredError

_registry_lock = threading.Lock()


class SecretsManager:
    """Facade over all registered secret backends."""

    _registry: Dict[str, Type[BaseSecretBackend]] = {}

    @classmethod
    def register_backend(cls, name: str, backend_cls: Type[BaseSecretBackend]) -> None:
        """Register a backend class under *name*.

        Thread-safe. Registering backends at module load time (import time) is
        strongly recommended to avoid contention in multi-threaded applications.
        """
        with _registry_lock:
            cls._registry[name] = backend_cls

    def __init__(self, backend: str, **kwargs: Any) -> None:
        if backend not in self._registry:
            available = list(self._registry.keys())
            raise BackendNotRegisteredError(f"Unknown backend '{backend}'. Available: {available}")
        self._backend: BaseSecretBackend = self._registry[backend](**kwargs)

    @property
    def backend(self) -> BaseSecretBackend:
        """The underlying backend instance."""
        return self._backend

    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Store *secret* under *name*. Delegates to the active backend.

        See the underlying backend's add_secret for per-backend behavior —
        notably, idempotency differs (Vault overwrites, Keyring and EnvFile
        raise on existing names).
        """
        self._backend.add_secret(name, secret)

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Retrieve the secret stored under *name*. Delegates to the active backend.

        Raises the backend's per-type NotFound exception if absent — e.g.
        VaultSecretNotFoundError, KeyringSecretNotFoundError, EnvFileNotFoundError.
        """
        return self._backend.get_secret(name)

    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Update the secret stored under *name*. Delegates to the active backend.

        See the backend's update_secret for merge-vs-replace semantics: Vault
        merges keys, Keyring replaces the whole dict, EnvFile replaces each
        supplied key in place.
        """
        self._backend.update_secret(name, secret)

    def delete_secret(self, name: str) -> None:
        """Delete the secret stored under *name*. Delegates to the active backend."""
        self._backend.delete_secret(name)

    def list_secrets(self, path: str = "") -> List[str]:
        """List secret names, optionally under *path*. Delegates to the active backend.

        See BaseSecretBackend.list_secrets for the per-backend meaning of *path*.
        """
        return self._backend.list_secrets(path)


# Register built-in backends
SecretsManager.register_backend("vault", VaultBackend)
SecretsManager.register_backend("keyring", KeyringBackend)
SecretsManager.register_backend("env", EnvFileBackend)

# Module-level alias so callers can do:
#   from credential_bridge.manager import register_backend
register_backend = SecretsManager.register_backend
