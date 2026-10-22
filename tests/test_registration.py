"""The plugin registers its asksage--* shims through the public shim API."""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_asksage import register_shims

_SHIMS = {
    "asksage--chat_completions": "chat_completions",
    "asksage--open_responses": "open_responses",
    "asksage--messages": "messages",
    "asksage--google_generate": "google_generate",
}


@pytest.fixture()
def _registered():
    _reset_registry()  # clean registry, so only the plugin's shims are present
    register_shims()
    yield


@pytest.mark.parametrize("name,base", sorted(_SHIMS.items()))
def test_registers_asksage_shim(_registered, name, base):
    shim = get_shim(name)
    assert shim is not None
    assert shim.base == base
    assert shim.connection.base_url.startswith("https://api.asksage.ai/")
    assert shim.connection.api_key_env == "ASKSAGE_API_KEY"


def test_google_generate_overrides_auth_header(_registered):
    shim = get_shim("asksage--google_generate")
    assert shim is not None
    assert shim.connection.auth_header == "x-access-tokens"


@pytest.mark.parametrize("name", sorted(_SHIMS))
def test_the_credential_exchange_ships_with_the_shim(_registered, name):
    """A provider needs no ``token_command``: the shim declares one.

    Resolved through a real load, so the assertion covers the packaging case —
    a relative path that only exists in a source checkout would fail here.
    """
    shim = get_shim(name)
    assert shim is not None
    argv = shim.connection.token_command
    assert argv is not None and argv[0] == "python3"
    script = Path(argv[1])
    assert script.is_absolute() and script.is_file(), argv
    assert script.name == "token.py"
