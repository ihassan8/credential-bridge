# tests/unit/test_env_file_backend.py
import os
import sys
from pathlib import Path

import pytest

from credential_bridge.backends.env_file import EnvFileBackend
from credential_bridge.exceptions import EnvFileNotFoundError


@pytest.fixture
def backend(tmp_path):
    return EnvFileBackend(path=tmp_path / ".env")


@pytest.fixture
def populated_backend(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=value\n", encoding="utf-8")
    return EnvFileBackend(path=env_file)


def test_backend_name():
    assert EnvFileBackend.backend_name == "env"


def test_add_secret_creates_file(backend, tmp_path):
    backend.add_secret("DB_HOST", {"DB_HOST": "localhost"})
    content = (tmp_path / ".env").read_text()
    assert "DB_HOST=localhost" in content


def test_add_secret_writes_group_comment(backend, tmp_path):
    backend.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})
    content = (tmp_path / ".env").read_text()
    assert "# database" in content
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content


def test_add_secret_raises_if_key_exists(populated_backend):
    from credential_bridge.exceptions import EnvFileKeyExistsError

    with pytest.raises(EnvFileKeyExistsError):
        populated_backend.add_secret("EXISTING", {"EXISTING": "new_value"})


def test_get_secret_returns_dict(populated_backend):
    result = populated_backend.get_secret("EXISTING")
    assert result == {"EXISTING": "value"}


def test_get_secret_raises_if_not_found(populated_backend):
    with pytest.raises(EnvFileNotFoundError):
        populated_backend.get_secret("MISSING")


def test_update_secret_changes_value(populated_backend, tmp_path):
    populated_backend.update_secret("EXISTING", {"EXISTING": "updated"})
    content = (tmp_path / ".env").read_text()
    assert "EXISTING=updated" in content
    assert "EXISTING=value" not in content


def test_update_secret_is_partial(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\nB=2\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file)
    backend.update_secret("A", {"A": "updated"})
    content = env_file.read_text()
    assert "A=updated" in content
    assert "B=2" in content


def test_update_secret_raises_if_no_key_exists(backend):
    with pytest.raises(EnvFileNotFoundError, match="not found"):
        backend.update_secret("MISSING", {"MISSING": "val"})


def test_delete_secret(populated_backend, tmp_path):
    populated_backend.delete_secret("EXISTING")
    content = (tmp_path / ".env").read_text()
    assert "EXISTING" not in content


def test_delete_secret_raises_if_not_found(populated_backend):
    with pytest.raises(EnvFileNotFoundError):
        populated_backend.delete_secret("MISSING")


def test_list_secrets(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\nB=2\nC=3\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file)
    assert sorted(backend.list_secrets()) == ["A", "B", "C"]


def test_load_into_environ_on_add(tmp_path, monkeypatch):
    import os

    env_file = tmp_path / ".env"
    backend = EnvFileBackend(path=env_file, load_into_environ=True)
    backend.add_secret("MY_VAR", {"MY_VAR": "hello"})
    assert os.environ.get("MY_VAR") == "hello"
    monkeypatch.delenv("MY_VAR", raising=False)


def test_write_uses_tmp_file(backend, tmp_path, mocker):
    """Verify atomic write: os.replace is called with a .env.tmp source path."""
    replaced_src = []
    original_replace = os.replace

    def track_replace(src, dst):
        replaced_src.append(str(src))
        return original_replace(src, dst)

    mocker.patch("credential_bridge.backends.env_file.os.replace", track_replace)
    backend.add_secret("KEY", {"KEY": "val"})
    assert any(".env.tmp" in p for p in replaced_src)


def test_add_secret_quotes_value_with_spaces(backend, tmp_path):
    backend.add_secret("GREETING", {"GREETING": "hello world"})
    content = (tmp_path / ".env").read_text()
    assert 'GREETING="hello world"' in content
    # Reading it back should return the unquoted value
    result = backend.get_secret("GREETING")
    assert result == {"GREETING": "hello world"}


def test_env_full_crud(tmp_path):
    from credential_bridge.backends.env_file import EnvFileBackend

    backend = EnvFileBackend(path=tmp_path / ".env")

    # Add
    backend.add_secret("DB_HOST", {"DB_HOST": "localhost"})
    assert backend.get_secret("DB_HOST") == {"DB_HOST": "localhost"}

    # Update
    backend.update_secret("DB_HOST", {"DB_HOST": "remotehost"})
    assert backend.get_secret("DB_HOST") == {"DB_HOST": "remotehost"}

    # List
    assert "DB_HOST" in backend.list_secrets()

    # Delete
    backend.delete_secret("DB_HOST")
    with pytest.raises(EnvFileNotFoundError):
        backend.get_secret("DB_HOST")


def test_env_multi_key_group(tmp_path):
    from credential_bridge.backends.env_file import EnvFileBackend

    backend = EnvFileBackend(path=tmp_path / ".env")

    backend.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})
    assert backend.get_secret("DB_HOST") == {"DB_HOST": "localhost"}
    assert backend.get_secret("DB_PORT") == {"DB_PORT": "5432"}
    assert "DB_HOST" in backend.list_secrets()
    assert "DB_PORT" in backend.list_secrets()


def test_get_secret_by_group_name(tmp_path):
    """get_secret with a group label returns all keys under that # comment block."""
    backend = EnvFileBackend(path=tmp_path / ".env")
    backend.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})
    result = backend.get_secret("database")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_delete_secret_by_group_name(tmp_path):
    """delete_secret with a group label removes all keys and the comment header."""
    backend = EnvFileBackend(path=tmp_path / ".env")
    backend.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})
    backend.delete_secret("database")
    with pytest.raises(EnvFileNotFoundError):
        backend.get_secret("DB_HOST")
    with pytest.raises(EnvFileNotFoundError):
        backend.get_secret("DB_PORT")
    content = (tmp_path / ".env").read_text()
    assert "# database" not in content
    assert "DB_HOST" not in content


def test_delete_secret_by_group_name_raises_if_group_missing(backend):
    with pytest.raises(EnvFileNotFoundError):
        backend.delete_secret("nonexistent_group")


def test_load_into_environ_on_update(tmp_path, monkeypatch):
    import os

    env_file = tmp_path / ".env"
    env_file.write_text("MY_VAR=hello\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file, load_into_environ=True)
    backend.update_secret("MY_VAR", {"MY_VAR": "world"})
    assert os.environ.get("MY_VAR") == "world"
    monkeypatch.delenv("MY_VAR", raising=False)


def test_load_into_environ_on_delete(tmp_path, monkeypatch):
    import os

    env_file = tmp_path / ".env"
    env_file.write_text("MY_VAR=hello\n", encoding="utf-8")
    monkeypatch.setenv("MY_VAR", "hello")
    backend = EnvFileBackend(path=env_file, load_into_environ=True)
    backend.delete_secret("MY_VAR")
    assert os.environ.get("MY_VAR") is None


def test_repr(tmp_path):
    env_file = tmp_path / ".env"
    backend = EnvFileBackend(path=env_file)
    r = repr(backend)
    assert r.startswith("EnvFileBackend(path=")
    assert ".env" in r


def test_list_secrets_with_path_filter(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_HOST=localhost\nAPP_PORT=5432\nDB_NAME=mydb\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file)
    assert set(backend.list_secrets("APP_")) == {"APP_HOST", "APP_PORT"}
    assert backend.list_secrets("DB_") == ["DB_NAME"]
    assert backend.list_secrets("MISSING_") == []


def test_list_secrets_no_filter_returns_all(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=1\nBAR=2\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file)
    assert set(backend.list_secrets()) == {"FOO", "BAR"}
    assert set(backend.list_secrets("")) == {"FOO", "BAR"}


# ---------------------------------------------------------------------------
# Issue A: delete_secret must not remove an unrelated top-of-file comment
# ---------------------------------------------------------------------------

def test_delete_does_not_remove_top_of_file_comment(tmp_path):
    """A comment at the top of the file (no blank line before it) must survive
    when the key immediately below it is deleted."""
    env_file = tmp_path / ".env"
    env_file.write_text("# Important config\nMY_KEY=value\n", encoding="utf-8")
    backend = EnvFileBackend(path=env_file)
    backend.delete_secret("MY_KEY")
    content = env_file.read_text()
    assert "# Important config" in content
    assert "MY_KEY" not in content


def test_delete_removes_group_header_when_last_key_removed(tmp_path):
    """Deleting the last key in a group created by add_secret must also remove
    the group's comment header (preceded by a blank line)."""
    backend = EnvFileBackend(path=tmp_path / ".env")
    backend.add_secret("db", {"DB_URL": "localhost"})
    backend.delete_secret("DB_URL")
    content = (tmp_path / ".env").read_text()
    assert "# db" not in content
    assert "DB_URL" not in content


# ---------------------------------------------------------------------------
# Issue C: add_secret must refuse duplicate group names
# ---------------------------------------------------------------------------

def test_add_secret_raises_if_group_name_already_exists(tmp_path):
    """Calling add_secret twice with the same group name (but different keys)
    must raise EnvFileKeyExistsError rather than creating a duplicate header."""
    from credential_bridge.exceptions import EnvFileKeyExistsError

    backend = EnvFileBackend(path=tmp_path / ".env")
    backend.add_secret("database", {"DB_HOST": "localhost"})
    with pytest.raises(EnvFileKeyExistsError, match="database"):
        backend.add_secret("database", {"DB_PORT": "5432"})


# ---------------------------------------------------------------------------
# Issue J: _write_lines must create the .tmp file with restricted permissions
# ---------------------------------------------------------------------------

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file permissions not enforced on Windows")
def test_tmp_file_created_with_restricted_permissions(tmp_path, mocker):
    """The .env.tmp file must be created with 0o600 permissions so that
    plaintext secrets are not readable by other users, even on crash."""
    recorded = []
    original_replace = os.replace

    def capture_permissions(src, dst):
        recorded.append(os.stat(src).st_mode & 0o777)
        return original_replace(src, dst)

    mocker.patch("credential_bridge.backends.env_file.os.replace", side_effect=capture_permissions)
    backend = EnvFileBackend(path=tmp_path / ".env")
    backend.add_secret("KEY", {"KEY": "val"})
    assert recorded, "os.replace was never called"
    assert recorded[0] == 0o600, f"Expected 0o600, got 0o{recorded[0]:o}"
