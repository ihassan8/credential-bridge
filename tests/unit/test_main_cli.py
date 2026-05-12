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
