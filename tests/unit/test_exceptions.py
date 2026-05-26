import pytest

from credential_bridge.exceptions import (
    BackendError,
    BackendNotRegisteredError,
    ConfigurationError,
    CredentialBridgeError,
    EnvFileError,
    EnvFileNotFoundError,
    KeyringError,
    VaultAuthError,
    VaultConnectionError,
    VaultError,
)


def test_vault_auth_error_is_vault_error():
    assert issubclass(VaultAuthError, VaultError)


def test_vault_error_is_backend_error():
    assert issubclass(VaultError, BackendError)


def test_backend_error_is_credential_bridge_error():
    assert issubclass(BackendError, CredentialBridgeError)


def test_env_file_not_found_is_env_file_error():
    assert issubclass(EnvFileNotFoundError, EnvFileError)


def test_backend_not_registered_is_credential_bridge_error():
    assert issubclass(BackendNotRegisteredError, CredentialBridgeError)


def test_configuration_error_is_credential_bridge_error():
    assert issubclass(ConfigurationError, CredentialBridgeError)


def test_exceptions_are_catchable_as_base():
    with pytest.raises(CredentialBridgeError):
        raise VaultAuthError("bad token")


def test_keyring_error_is_backend_error():
    assert issubclass(KeyringError, BackendError)


def test_vault_connection_error_is_vault_error():
    assert issubclass(VaultConnectionError, VaultError)


def test_env_file_error_is_backend_error():
    assert issubclass(EnvFileError, BackendError)


def test_env_file_key_exists_error_is_env_file_error():
    from credential_bridge.exceptions import EnvFileError, EnvFileKeyExistsError

    assert issubclass(EnvFileKeyExistsError, EnvFileError)


def test_vault_secret_not_found_is_vault_error():
    from credential_bridge.exceptions import VaultError, VaultSecretNotFoundError

    assert issubclass(VaultSecretNotFoundError, VaultError)


def test_keyring_key_exists_error_is_keyring_error():
    from credential_bridge.exceptions import KeyringError, KeyringKeyExistsError

    assert issubclass(KeyringKeyExistsError, KeyringError)


def test_keyring_key_exists_error_is_catchable_as_backend_error():
    from credential_bridge.exceptions import BackendError, KeyringKeyExistsError

    with pytest.raises(BackendError):
        raise KeyringKeyExistsError("already exists")


def test_keyring_key_exists_error_exported_from_package():
    from credential_bridge import KeyringKeyExistsError

    assert KeyringKeyExistsError is not None


def test_not_found_exceptions_catchable_as_secret_not_found_error():
    """Fix X4: all three 'not found' exceptions must be catchable as SecretNotFoundError."""
    from credential_bridge.exceptions import (
        EnvFileNotFoundError,
        KeyringSecretNotFoundError,
        SecretNotFoundError,
        VaultSecretNotFoundError,
    )

    for exc_cls in (VaultSecretNotFoundError, KeyringSecretNotFoundError, EnvFileNotFoundError):
        assert issubclass(exc_cls, SecretNotFoundError), (
            f"{exc_cls.__name__} should be a subclass of SecretNotFoundError"
        )
        with pytest.raises(SecretNotFoundError):
            raise exc_cls("not found")


def test_secret_not_found_error_is_backend_error():
    from credential_bridge.exceptions import BackendError, SecretNotFoundError

    assert issubclass(SecretNotFoundError, BackendError)


def test_secret_not_found_error_exported_from_package():
    from credential_bridge import SecretNotFoundError

    assert SecretNotFoundError is not None
