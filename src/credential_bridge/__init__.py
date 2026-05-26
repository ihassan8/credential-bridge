# src/credential_bridge/__init__.py
from ._version import __version__
from .backends import BaseSecretBackend, EnvFileBackend, KeyringBackend, VaultBackend
from .exceptions import (
    BackendError,
    BackendNotRegisteredError,
    ConfigurationError,
    CredentialBridgeError,
    EnvFileError,
    EnvFileKeyExistsError,
    EnvFileNotFoundError,
    KeyringError,
    KeyringKeyExistsError,
    KeyringSecretNotFoundError,
    SecretNotFoundError,
    VaultAuthError,
    VaultConnectionError,
    VaultError,
    VaultSecretNotFoundError,
)
from .manager import SecretsManager, register_backend
from .utils import get_session, get_vault_credentials

# Backwards-compatibility aliases
VaultManager = VaultBackend
KeyringManager = KeyringBackend

__all__ = [
    "__version__",
    "SecretsManager",
    "register_backend",
    "BaseSecretBackend",
    "VaultBackend",
    "KeyringBackend",
    "EnvFileBackend",
    "CredentialBridgeError",
    "BackendError",
    "SecretNotFoundError",
    "VaultError",
    "VaultAuthError",
    "VaultConnectionError",
    "VaultSecretNotFoundError",
    "KeyringError",
    "KeyringKeyExistsError",
    "KeyringSecretNotFoundError",
    "EnvFileError",
    "EnvFileKeyExistsError",
    "EnvFileNotFoundError",
    "BackendNotRegisteredError",
    "ConfigurationError",
    "VaultManager",
    "KeyringManager",
    "get_session",
    "get_vault_credentials",
]
