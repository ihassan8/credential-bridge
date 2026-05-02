# tests/unit/test_env_cli.py
import pytest
from typer.testing import CliRunner
from credential_bridge.cli.env_cli import app

runner = CliRunner()


@pytest.fixture
def mock_env_backend(mocker):
    backend = mocker.MagicMock()
    mocker.patch("credential_bridge.cli.env_cli.EnvFileBackend", return_value=backend)
    return backend


def test_add_command(mock_env_backend):
    result = runner.invoke(app, ["add", "DB_HOST", "--secret", "DB_HOST=localhost"])
    assert result.exit_code == 0
    mock_env_backend.add_secret.assert_called_once()


def test_get_command(mock_env_backend):
    mock_env_backend.get_secret.return_value = {"DB_HOST": "localhost"}
    result = runner.invoke(app, ["get", "DB_HOST"])
    assert result.exit_code == 0
    assert "localhost" in result.output


def test_list_command(mock_env_backend):
    mock_env_backend.list_secrets.return_value = ["A", "B", "C"]
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "A" in result.output


def test_delete_command(mock_env_backend):
    result = runner.invoke(app, ["delete", "DB_HOST", "--yes"])
    assert result.exit_code == 0
    mock_env_backend.delete_secret.assert_called_once_with("DB_HOST")


def test_custom_path_passed_to_backend(mocker):
    backend = mocker.MagicMock()
    mock_cls = mocker.patch("credential_bridge.cli.env_cli.EnvFileBackend", return_value=backend)
    backend.list_secrets.return_value = []
    runner.invoke(app, ["list", "--path", "/custom/.env"])
    mock_cls.assert_called_once_with(path="/custom/.env")
