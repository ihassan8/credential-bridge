# tests/unit/test_main_cli.py
from typer.testing import CliRunner

from credential_bridge.cli.main import app

runner = CliRunner()


def test_cb_has_vault_subcommand():
    result = runner.invoke(app, ["vault", "--help"])
    assert result.exit_code == 0


def test_cb_has_keyring_subcommand():
    result = runner.invoke(app, ["keyring", "--help"])
    assert result.exit_code == 0


def test_cb_has_env_subcommand():
    result = runner.invoke(app, ["env", "--help"])
    assert result.exit_code == 0


def test_cb_root_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "vault" in result.output
    assert "keyring" in result.output
    assert "env" in result.output


def test_wizard_keyboard_interrupt_exits_zero(mocker):
    """KeyboardInterrupt during wizard should exit with code 0."""
    mocker.patch("credential_bridge.prompt_wizard.main", side_effect=KeyboardInterrupt)
    result = runner.invoke(app, ["wizard"])
    assert result.exit_code == 0


def test_wizard_exception_exits_one(mocker):
    """Unexpected exceptions from the wizard should exit with code 1."""
    mocker.patch("credential_bridge.prompt_wizard.main", side_effect=RuntimeError("boom"))
    result = runner.invoke(app, ["wizard"])
    assert result.exit_code == 1
