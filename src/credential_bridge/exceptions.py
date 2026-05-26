"""Exception hierarchy for credential-bridge."""


class CredentialBridgeError(Exception):
    """Base exception for all credential-bridge errors."""


class BackendError(CredentialBridgeError):
    """Base exception for backend-specific errors."""


class SecretNotFoundError(BackendError):
    """Raised when a requested secret does not exist in any backend."""


class VaultError(BackendError):
    """General HashiCorp Vault error."""


class VaultAuthError(VaultError):
    """Invalid token or AppRole credentials."""


class VaultConnectionError(VaultError):
    """Cannot reach Vault — bad URL or network issue."""


class VaultSecretNotFoundError(SecretNotFoundError, VaultError):
    """A requested secret path does not exist in Vault."""


class KeyringError(BackendError):
    """System keyring error."""


class KeyringSecretNotFoundError(SecretNotFoundError, KeyringError):
    """A requested secret does not exist in the keyring."""


class KeyringKeyExistsError(KeyringError):
    """A key being added already exists in the keyring."""


class EnvFileError(BackendError):
    """Error reading or writing a .env file."""


class EnvFileNotFoundError(SecretNotFoundError, EnvFileError):
    """A requested key does not exist in the .env file."""


class EnvFileKeyExistsError(EnvFileError):
    """A key being added already exists in the .env file."""


class BackendNotRegisteredError(CredentialBridgeError):
    """Backend name not found in SecretsManager registry."""


class ConfigurationError(CredentialBridgeError):
    """Required configuration is missing or invalid."""
