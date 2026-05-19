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


def test_add_command_malformed_secret_exits_with_error(mock_env_backend):
    """A --secret value without '=' should exit 1 and show an error."""
    result = runner.invoke(app, ["add", "GROUP", "--secret", "NOEQUALSSIGN"])
    assert result.exit_code == 1
    assert "NOEQUALSSIGN" in result.output
    mock_env_backend.add_secret.assert_not_called()


def test_update_command_malformed_secret_exits_with_error(mock_env_backend):
    result = runner.invoke(app, ["update", "MY_KEY", "--secret", "BADFORMAT"])
    assert result.exit_code == 1
    mock_env_backend.update_secret.assert_not_called()


# ---------------------------------------------------------------------------
# Issue K: interactive add/update must mask secret values (not echo plaintext)
# ---------------------------------------------------------------------------

def test_add_command_interactive_masks_secret_input(mocker, mock_env_backend):
    """prompt_secrets_interactive must be called without mask_value=False so
    that typed secrets are hidden (consistent with vault-cli and keyring-cli)."""
    mock_prompt = mocker.patch(
        "credential_bridge.cli.env_cli.prompt_secrets_interactive",
        return_value=["KEY=val"],
    )
    runner.invoke(app, ["add", "GROUP"])
    mock_prompt.assert_called_once()
    _, kwargs = mock_prompt.call_args
    assert kwargs.get("mask_value") is not False, (
        "env-cli add called prompt_secrets_interactive with mask_value=False"
    )


def test_update_command_interactive_masks_secret_input(mocker, mock_env_backend):
    """Same masking requirement for the update command."""
    mock_prompt = mocker.patch(
        "credential_bridge.cli.env_cli.prompt_secrets_interactive",
        return_value=["KEY=val"],
    )
    runner.invoke(app, ["update", "MY_KEY"])
    mock_prompt.assert_called_once()
    _, kwargs = mock_prompt.call_args
    assert kwargs.get("mask_value") is not False, (
        "env-cli update called prompt_secrets_interactive with mask_value=False"
    )
