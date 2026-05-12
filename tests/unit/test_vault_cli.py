# tests/unit/test_vault_cli.py
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from credential_bridge.cli.vault_cli import app

runner = CliRunner()


@pytest.fixture
def mock_vault_backend(mocker):
    backend = MagicMock()
    mocker.patch("credential_bridge.cli.vault_cli.VaultBackend", return_value=backend)
    return backend


def test_get_command_shows_secret(mock_vault_backend):
    mock_vault_backend.get_secret.return_value = {"user": "admin"}
    result = runner.invoke(
        app,
        [
            "get",
            "myapp/db",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
        ],
    )
    assert result.exit_code == 0
    assert "admin" in result.output


def test_add_command_success(mock_vault_backend):
    result = runner.invoke(
        app,
        [
            "add",
            "myapp/db",
            "--secret",
            "user=admin",
            "--secret",
            "pass=s3cr3t",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
        ],
    )
    assert result.exit_code == 0
    mock_vault_backend.add_secret.assert_called_once_with("myapp/db", {"user": "admin", "pass": "s3cr3t"})


def test_delete_command(mock_vault_backend):
    result = runner.invoke(
        app,
        [
            "delete",
            "myapp/db",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
            "--yes",
        ],
    )
    assert result.exit_code == 0
    mock_vault_backend.delete_secret.assert_called_once_with("myapp/db")


def test_backend_error_shows_error_output(mock_vault_backend):
    from credential_bridge.exceptions import VaultAuthError

    mock_vault_backend.get_secret.side_effect = VaultAuthError("bad token")
    result = runner.invoke(
        app,
        [
            "get",
            "myapp/db",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "bad",
        ],
    )
    assert result.exit_code == 1
    assert "bad token" in result.output


def test_list_command(mock_vault_backend):
    mock_vault_backend.list_secrets.return_value = ["key1", "key2"]
    result = runner.invoke(
        app,
        [
            "list",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
        ],
    )
    assert result.exit_code == 0
    assert "key1" in result.output


def test_add_command_malformed_secret_exits_with_error(mock_vault_backend):
    """A --secret value without '=' should exit 1 and show an error."""
    result = runner.invoke(
        app,
        [
            "add",
            "myapp/db",
            "--secret",
            "NOEQUALSSIGN",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
        ],
    )
    assert result.exit_code == 1
    assert "NOEQUALSSIGN" in result.output
    mock_vault_backend.add_secret.assert_not_called()


def test_update_command_malformed_secret_exits_with_error(mock_vault_backend):
    """A malformed --secret on update should exit 1 without calling the backend."""
    result = runner.invoke(
        app,
        [
            "update",
            "myapp/db",
            "--secret",
            "BADFORMAT",
            "--vault-url",
            "https://vault.example.com",
            "--vault-token",
            "s.test",
        ],
    )
    assert result.exit_code == 1
    mock_vault_backend.update_secret.assert_not_called()
