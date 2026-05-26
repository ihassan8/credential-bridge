# tests/unit/test_keyring_cli.py
import pytest
from typer.testing import CliRunner

from credential_bridge.cli.keyring_cli import app

runner = CliRunner()


@pytest.fixture
def mock_keyring_backend(mocker):
    backend = mocker.MagicMock()
    mocker.patch("credential_bridge.cli.keyring_cli.KeyringBackend", return_value=backend)
    return backend


def test_add_command(mock_keyring_backend):
    result = runner.invoke(app, ["add", "mykey", "--secret", "mykey=s3cr3t", "--service-name", "svc"])
    assert result.exit_code == 0
    mock_keyring_backend.add_secret.assert_called_once()


def test_get_command(mock_keyring_backend):
    mock_keyring_backend.get_secret.return_value = {"mykey": "s3cr3t"}
    result = runner.invoke(app, ["get", "mykey", "--service-name", "svc"])
    assert result.exit_code == 0
    assert "s3cr3t" in result.output


def test_delete_command(mock_keyring_backend):
    result = runner.invoke(app, ["delete", "mykey", "--service-name", "svc", "--yes"])
    assert result.exit_code == 0
    mock_keyring_backend.delete_secret.assert_called_once_with("mykey")


def test_update_command(mock_keyring_backend):
    mock_keyring_backend.get_secret.return_value = {"mykey": "old"}
    result = runner.invoke(app, ["update", "mykey", "--secret", "mykey=new", "--service-name", "svc"])
    assert result.exit_code == 0
    mock_keyring_backend.update_secret.assert_called_once()


def test_add_command_malformed_secret_exits_with_error(mock_keyring_backend):
    """A --secret value without '=' should exit 1 and show an error."""
    result = runner.invoke(app, ["add", "mykey", "--secret", "NOEQUALSSIGN", "--service-name", "svc"])
    assert result.exit_code == 1
    assert "NOEQUALSSIGN" in result.output
    mock_keyring_backend.add_secret.assert_not_called()


def test_update_command_malformed_secret_exits_with_error(mock_keyring_backend):
    result = runner.invoke(app, ["update", "mykey", "--secret", "BADFORMAT", "--service-name", "svc"])
    assert result.exit_code == 1
    mock_keyring_backend.update_secret.assert_not_called()


def test_list_not_supported(mock_keyring_backend):
    """list command should exit 1 with an informative error message."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "not supported" in result.output.lower() or "Unsupported" in result.output


def test_delete_cancelled_exits_zero(mock_keyring_backend):
    """Cancelling a delete confirmation should exit 0 (not 1)."""
    result = runner.invoke(app, ["delete", "mykey", "--service-name", "svc"], input="n\n")
    assert result.exit_code == 0
    mock_keyring_backend.delete_secret.assert_not_called()


def test_get_invalid_output_format(mock_keyring_backend):
    """An unknown --output value should exit 1 before calling the backend."""
    result = runner.invoke(app, ["get", "mykey", "--output", "xml", "--service-name", "svc"])
    assert result.exit_code == 1
    mock_keyring_backend.get_secret.assert_not_called()
