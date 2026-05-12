# tests/unit/test_output.py
import pytest

from credential_bridge.cli._output import parse_secrets


def test_parse_secrets_valid():
    assert parse_secrets(["KEY=value", "FOO=bar"]) == {"KEY": "value", "FOO": "bar"}


def test_parse_secrets_value_with_equals():
    """Value may itself contain '=' — only the first '=' splits key from value."""
    assert parse_secrets(["URL=http://host?a=1"]) == {"URL": "http://host?a=1"}


def test_parse_secrets_empty_value():
    assert parse_secrets(["EMPTY="]) == {"EMPTY": ""}


def test_parse_secrets_empty_list():
    assert parse_secrets([]) == {}


def test_parse_secrets_malformed_raises_value_error():
    with pytest.raises(ValueError, match="NOEQUALSSIGN"):
        parse_secrets(["NOEQUALSSIGN"])


def test_parse_secrets_malformed_message_includes_bad_token():
    with pytest.raises(ValueError, match="KEY=value"):
        parse_secrets(["justwrong"])
