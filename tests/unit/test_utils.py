from pathlib import Path

import pytest

import credential_bridge.utils as u


def test_config_file_uses_home_directory():
    assert u.CONFIG_FILE == Path.home() / ".vault_config.json"


def test_load_config_returns_empty_dict_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "CONFIG_FILE", tmp_path / "missing.json")
    assert u.load_config() == {}


def test_save_and_load_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "CONFIG_FILE", tmp_path / ".vault_config.json")
    data = {"vault_token": "s.test"}
    u.save_config(data)
    assert u.load_config() == data


def test_get_session_returns_requests_session():
    import requests

    session = u.get_session()
    assert isinstance(session, requests.Session)
    assert session.verify is True


def test_get_session_with_cert():
    session = u.get_session(cert="/path/to/cert.pem")
    assert session.verify == "/path/to/cert.pem"


def test_no_vault_addr_enum_in_utils():
    assert not hasattr(u, "VaultAddr")


def test_no_get_vault_addr_in_utils():
    assert not hasattr(u, "get_vault_addr")


def test_get_vault_credentials_returns_tuple(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "CONFIG_FILE", tmp_path / ".vault_config.json")
    u.save_config({"vault_token": "s.test", "vault_role_id": None, "vault_secret_id": None})
    token, role_id, secret_id = u.get_vault_credentials()
    assert token == "s.test"
    assert role_id is None


def test_load_config_raises_on_corrupt_json(tmp_path, monkeypatch):
    """Fix X2: corrupt JSON must raise ConfigurationError, not bare json.JSONDecodeError."""
    from credential_bridge.exceptions import ConfigurationError

    corrupt = tmp_path / ".vault_config.json"
    corrupt.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(u, "CONFIG_FILE", corrupt)
    with pytest.raises(ConfigurationError, match="invalid JSON"):
        u.load_config()


def test_save_config_is_atomic_on_non_windows(tmp_path, monkeypatch):
    """Fix X3: on non-Windows, save_config writes via a .tmp file then os.replace."""
    import sys

    monkeypatch.setattr(u, "CONFIG_FILE", tmp_path / ".vault_config.json")
    monkeypatch.setattr(sys, "platform", "linux")
    data = {"vault_token": "s.atomic"}
    u.save_config(data)
    # The final file must exist with the correct contents.
    import json

    result = json.loads((tmp_path / ".vault_config.json").read_text(encoding="utf-8"))
    assert result == data
    # The temp file must have been cleaned up by os.replace.
    assert not (tmp_path / ".vault_config.json.tmp").exists()
