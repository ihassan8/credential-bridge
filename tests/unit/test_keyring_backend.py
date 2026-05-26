import json
from unittest.mock import MagicMock

import pytest

from credential_bridge.backends.keyring import KeyringBackend
from credential_bridge.exceptions import KeyringError


@pytest.fixture
def mock_logger(mocker):
    logger = MagicMock()
    mocker.patch("credential_bridge.backends.keyring.get_logger", return_value=logger)
    return logger


@pytest.fixture
def backend(mocker, mock_logger):
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=None)
    return KeyringBackend(service_name="test_service")


def test_backend_name():
    assert KeyringBackend.backend_name == "keyring"


def test_add_secret_serializes_to_json(mocker, mock_logger):
    mock_set = mocker.patch("credential_bridge.backends.keyring.keyring.set_password")
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=None)
    backend = KeyringBackend(service_name="svc")
    backend.add_secret("mykey", {"user": "admin", "pass": "s3cr3t"})
    mock_set.assert_called_once_with("svc", "mykey", json.dumps({"user": "admin", "pass": "s3cr3t"}))


def test_get_secret_deserializes_from_json(mocker, mock_logger):
    stored = json.dumps({"user": "admin"})
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    backend = KeyringBackend(service_name="svc")
    result = backend.get_secret("mykey")
    assert result == {"user": "admin"}


def test_get_secret_raises_when_not_found(mocker, mock_logger):
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=None)
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringError, match="not found"):
        backend.get_secret("missing")


def test_update_secret_raises_when_not_found(mocker, mock_logger):
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=None)
    backend = KeyringBackend(service_name="svc")
    # update_secret now delegates to get_secret; the message comes from
    # KeyringSecretNotFoundError raised by get_secret ("not found").
    with pytest.raises(KeyringError, match="not found"):
        backend.update_secret("missing", {"x": "y"})


def test_delete_secret(mocker, mock_logger):
    stored = json.dumps({"user": "admin"})
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    mock_del = mocker.patch("credential_bridge.backends.keyring.keyring.delete_password")
    backend = KeyringBackend(service_name="svc")
    backend.delete_secret("mykey")
    mock_del.assert_called_once_with("svc", "mykey")


def test_delete_secret_raises_if_not_found(mocker, mock_logger):
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=None)
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringError, match="not found"):
        backend.delete_secret("missing_key")


def test_list_secrets_raises_not_implemented(mocker, mock_logger):
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringError, match="not supported"):
        backend.list_secrets()


def test_update_secret_success(mocker, mock_logger):
    stored = json.dumps({"user": "admin"})
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    mock_set = mocker.patch("credential_bridge.backends.keyring.keyring.set_password")
    backend = KeyringBackend(service_name="svc")
    backend.update_secret("mykey", {"user": "newadmin"})
    mock_set.assert_called_once_with("svc", "mykey", json.dumps({"user": "newadmin"}))


def test_add_secret_raises_if_key_already_exists(mocker, mock_logger):
    """add_secret raises KeyringKeyExistsError (a subclass of KeyringError) if key already exists."""
    from credential_bridge.exceptions import KeyringKeyExistsError

    stored = json.dumps({"user": "admin"})
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringKeyExistsError, match="already exists"):
        backend.add_secret("mykey", {"user": "new"})


def test_add_secret_key_exists_catchable_as_keyring_error(mocker, mock_logger):
    """KeyringKeyExistsError is catchable as the broader KeyringError."""
    stored = json.dumps({"user": "admin"})
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringError):
        backend.add_secret("mykey", {"user": "new"})


def test_list_secrets_raises_keyring_error(mocker, mock_logger):
    """list_secrets raises KeyringError (not NotImplementedError)."""
    backend = KeyringBackend(service_name="svc")
    with pytest.raises(KeyringError, match="not supported"):
        backend.list_secrets()


def test_update_secret_merges_keys(mocker, mock_logger):
    """update_secret merges the supplied dict into the existing one; unmentioned
    keys must survive the call (Fix K1)."""
    stored = json.dumps({"a": "1", "b": "2"})
    # get_password is called by get_secret (inside update_secret) each time
    mocker.patch("credential_bridge.backends.keyring.keyring.get_password", return_value=stored)
    mock_set = mocker.patch("credential_bridge.backends.keyring.keyring.set_password")
    backend = KeyringBackend(service_name="svc")
    backend.update_secret("mykey", {"b": "new"})
    expected = json.dumps({"a": "1", "b": "new"})
    mock_set.assert_called_once_with("svc", "mykey", expected)
