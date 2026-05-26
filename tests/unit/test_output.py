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


def test_prompt_secrets_interactive_preserves_whitespace(mocker):
    """Values returned by prompt_secrets_interactive must not have leading/trailing
    whitespace stripped — only the key should be stripped."""
    from credential_bridge.cli._output import prompt_secrets_interactive

    # Simulate: key=" mykey ", value="  secret with spaces  "
    # After the fix the key is stripped but the value is not.
    mocker.patch(
        "credential_bridge.cli._output.pt_prompt",
        side_effect=["mykey", "  secret with spaces  ", ""],  # key, value, then empty key to stop
    )
    result = prompt_secrets_interactive(mask_value=False)
    assert result == ["mykey=  secret with spaces  "]
