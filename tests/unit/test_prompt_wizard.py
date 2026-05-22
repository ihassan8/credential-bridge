# tests/unit/test_prompt_wizard.py
"""Tests for prompt_wizard — covers the pure logic functions, not interactive prompts."""

from unittest.mock import MagicMock


def test_is_vault_cred_valid_returns_false_without_vault_addr(monkeypatch):
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    from credential_bridge.prompt_wizard import is_vault_cred_valid

    assert is_vault_cred_valid(vault_token="s.test") is False


def test_is_vault_cred_valid_returns_false_without_credentials(monkeypatch):
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example.com")
    from credential_bridge.prompt_wizard import is_vault_cred_valid

    assert is_vault_cred_valid() is False


def test_is_vault_cred_valid_returns_true_on_successful_auth(monkeypatch, mocker):
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example.com")
    mocker.patch("credential_bridge.manager.SecretsManager")
    from credential_bridge.prompt_wizard import is_vault_cred_valid

    assert is_vault_cred_valid(vault_token="s.valid") is True


def test_is_vault_cred_valid_returns_false_on_auth_error(monkeypatch, mocker):
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example.com")
    from credential_bridge.exceptions import VaultAuthError

    mocker.patch(
        "credential_bridge.manager.SecretsManager",
        side_effect=VaultAuthError("bad token"),
    )
    from credential_bridge.prompt_wizard import is_vault_cred_valid

    assert is_vault_cred_valid(vault_token="s.bad") is False


def test_run_keyring_cli_add(mocker):
    mock_manager = MagicMock()
    _mock_cls = mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    from credential_bridge.prompt_wizard import run_keyring_cli

    run_keyring_cli("add", "svc", "mykey", "myvalue")
    mock_manager.add_secret.assert_called_once_with("mykey", {"mykey": "myvalue"})


def test_run_keyring_cli_get(mocker, capsys):
    mock_manager = MagicMock()
    mock_manager.get_secret.return_value = {"mykey": "myvalue"}
    mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    from credential_bridge.prompt_wizard import run_keyring_cli

    run_keyring_cli("get", "svc", "mykey", None)
    mock_manager.get_secret.assert_called_once_with("mykey")


def test_run_vault_cli_add(mocker):
    mock_manager = MagicMock()
    mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    from credential_bridge.prompt_wizard import run_vault_cli

    run_vault_cli("add", "svc", "myapp/db", {"user": "admin"})
    mock_manager.add_secret.assert_called_once_with("myapp/db", {"user": "admin"})


def test_run_vault_cli_get(mocker):
    mock_manager = MagicMock()
    mock_manager.get_secret.return_value = {"user": "admin"}
    mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    from credential_bridge.prompt_wizard import run_vault_cli

    run_vault_cli("get", "svc", "myapp/db", {})
    mock_manager.get_secret.assert_called_once_with("myapp/db")


def test_run_vault_cli_uses_secret_path_not_service_name(mocker):
    """Regression test: CRUD operations use secret_path, not service_name."""
    mock_manager = MagicMock()
    mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    from credential_bridge.prompt_wizard import run_vault_cli

    run_vault_cli("delete", "my-service-tag", "actual/secret/path", {})
    mock_manager.delete_secret.assert_called_once_with("actual/secret/path")
    # service_name should NOT be used as the path
    for call in mock_manager.delete_secret.call_args_list:
        assert "my-service-tag" not in str(call)


# ---------------------------------------------------------------------------
# Bug: SecretsManager construction outside try/except crashes wizard on init error
# ---------------------------------------------------------------------------


def test_run_keyring_cli_handles_init_credential_bridge_error(mocker):
    """ConfigurationError raised during SecretsManager.__init__ must be caught
    and shown via _error, not propagate as an unhandled exception."""
    from credential_bridge.exceptions import ConfigurationError

    mocker.patch("credential_bridge.manager.SecretsManager", side_effect=ConfigurationError("no config"))
    spy = mocker.patch("credential_bridge.prompt_wizard._error")
    from credential_bridge.prompt_wizard import run_keyring_cli

    run_keyring_cli("add", "svc", "mykey", "val")
    spy.assert_called_once()


def test_run_vault_cli_handles_init_credential_bridge_error(mocker):
    """ConfigurationError raised during SecretsManager.__init__ must be caught
    and shown via _error, not propagate as an unhandled exception."""
    from credential_bridge.exceptions import ConfigurationError

    mocker.patch("credential_bridge.manager.SecretsManager", side_effect=ConfigurationError("no vault url"))
    mocker.patch("credential_bridge.prompt_wizard.load_config", return_value={})
    spy = mocker.patch("credential_bridge.prompt_wizard._error")
    from credential_bridge.prompt_wizard import run_vault_cli

    run_vault_cli("add", "svc", "myapp/db", {})
    spy.assert_called_once()


# ---------------------------------------------------------------------------
# Bug: _save_vault_token / _save_vault_approle persist "" for vault_addr
# ---------------------------------------------------------------------------


def test_save_vault_token_persists_none_when_vault_addr_unset(monkeypatch, mocker):
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    mock_save = mocker.patch("credential_bridge.prompt_wizard.save_config")
    mocker.patch("credential_bridge.prompt_wizard.load_config", return_value={})
    from credential_bridge.prompt_wizard import _save_vault_token

    _save_vault_token("s.test")
    saved = mock_save.call_args[0][0]
    assert saved.get("vault_addr") is None, f"Expected None, got {saved.get('vault_addr')!r}"


def test_save_vault_approle_persists_none_when_vault_addr_unset(monkeypatch, mocker):
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    mock_save = mocker.patch("credential_bridge.prompt_wizard.save_config")
    mocker.patch("credential_bridge.prompt_wizard.load_config", return_value={})
    from credential_bridge.prompt_wizard import _save_vault_approle

    _save_vault_approle("role-id", "secret-id")
    saved = mock_save.call_args[0][0]
    assert saved.get("vault_addr") is None, f"Expected None, got {saved.get('vault_addr')!r}"


def test_save_vault_token_preserves_existing_vault_addr_when_env_unset(monkeypatch, mocker):
    """Regression: saving a token must not clobber a previously-saved vault_addr
    just because VAULT_ADDR is not exported in the current shell."""
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    mock_save = mocker.patch("credential_bridge.prompt_wizard.save_config")
    mocker.patch(
        "credential_bridge.prompt_wizard.load_config",
        return_value={"vault_addr": "https://vault.example.com"},
    )
    from credential_bridge.prompt_wizard import _save_vault_token

    _save_vault_token("s.test")
    saved = mock_save.call_args[0][0]
    assert saved.get("vault_addr") == "https://vault.example.com"


def test_save_vault_approle_preserves_existing_vault_addr_when_env_unset(monkeypatch, mocker):
    """Regression: same as above for AppRole credentials."""
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    mock_save = mocker.patch("credential_bridge.prompt_wizard.save_config")
    mocker.patch(
        "credential_bridge.prompt_wizard.load_config",
        return_value={"vault_addr": "https://vault.example.com"},
    )
    from credential_bridge.prompt_wizard import _save_vault_approle

    _save_vault_approle("role-id", "secret-id")
    saved = mock_save.call_args[0][0]
    assert saved.get("vault_addr") == "https://vault.example.com"


# ---------------------------------------------------------------------------
# Bug: service_name is silently dropped by VaultBackend; should be mount_point
# ---------------------------------------------------------------------------


def test_run_vault_cli_passes_service_name_as_mount_point(mocker):
    """The wizard's 'service_name' (mount-point tag) must reach SecretsManager
    as mount_point, not service_name, because VaultBackend ignores service_name."""
    mock_manager = MagicMock()
    mock_cls = mocker.patch("credential_bridge.manager.SecretsManager", return_value=mock_manager)
    mocker.patch("credential_bridge.prompt_wizard.load_config", return_value={})
    from credential_bridge.prompt_wizard import run_vault_cli

    run_vault_cli("add", "my-mount", "myapp/db", {"user": "admin"}, vault_token="s.test")
    _, kwargs = mock_cls.call_args
    assert kwargs.get("mount_point") == "my-mount"
    assert "service_name" not in kwargs


# ---------------------------------------------------------------------------
# New: run_env_cli dispatch helper (extracted from configure_env)
# ---------------------------------------------------------------------------


def test_run_env_cli_add(mocker):
    mock_backend = MagicMock()
    mocker.patch("credential_bridge.prompt_wizard.EnvFileBackend", return_value=mock_backend)
    from credential_bridge.prompt_wizard import run_env_cli

    run_env_cli("add", ".env", "mygroup", {"KEY": "val"})
    mock_backend.add_secret.assert_called_once_with("mygroup", {"KEY": "val"})


def test_run_env_cli_get(mocker):
    mock_backend = MagicMock()
    mock_backend.get_secret.return_value = {"KEY": "val"}
    mocker.patch("credential_bridge.prompt_wizard.EnvFileBackend", return_value=mock_backend)
    from credential_bridge.prompt_wizard import run_env_cli

    run_env_cli("get", ".env", "KEY", {})
    mock_backend.get_secret.assert_called_once_with("KEY")


def test_run_env_cli_delete(mocker):
    mock_backend = MagicMock()
    mocker.patch("credential_bridge.prompt_wizard.EnvFileBackend", return_value=mock_backend)
    from credential_bridge.prompt_wizard import run_env_cli

    run_env_cli("delete", ".env", "KEY", {})
    mock_backend.delete_secret.assert_called_once_with("KEY")


def test_run_env_cli_handles_credential_bridge_error(mocker):
    from credential_bridge.exceptions import EnvFileNotFoundError

    mock_backend = MagicMock()
    mock_backend.get_secret.side_effect = EnvFileNotFoundError("not found")
    mocker.patch("credential_bridge.prompt_wizard.EnvFileBackend", return_value=mock_backend)
    spy = mocker.patch("credential_bridge.prompt_wizard._error")
    from credential_bridge.prompt_wizard import run_env_cli

    run_env_cli("get", ".env", "MISSING", {})
    spy.assert_called_once()
