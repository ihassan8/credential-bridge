"""Abstract base class for all secret backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSecretBackend(ABC):
    """Contract that every secrets backend must fulfil."""

    backend_name: str = ""

    @abstractmethod
    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Store a new secret. Raises if name already exists."""

    @abstractmethod
    def get_secret(self, name: str) -> Dict[str, Any]:
        """Retrieve a secret by name. Raises if not found."""

    @abstractmethod
    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Update an existing secret. Raises if not found."""

    @abstractmethod
    def delete_secret(self, name: str) -> None:
        """Delete a secret. Raises if not found."""

    @abstractmethod
    def list_secrets(self, path: str = "") -> List[str]:
        """List secret names, optionally under a path prefix."""
