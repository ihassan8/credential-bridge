# tests/conftest.py

import pytest


@pytest.fixture
def tmp_env_file(tmp_path):
    """A temporary .env file path (not yet created)."""
    return tmp_path / ".env"


@pytest.fixture
def populated_env_file(tmp_path):
    """A .env file with initial content."""
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING_KEY=existing_value\n", encoding="utf-8")
    return env_file


@pytest.fixture(autouse=True)
def clean_registry():
    """Isolate SecretsManager._registry state between all tests."""
    from credential_bridge.manager import SecretsManager

    original = dict(SecretsManager._registry)
    yield
    SecretsManager._registry = original
