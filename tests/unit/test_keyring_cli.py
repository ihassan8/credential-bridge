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
