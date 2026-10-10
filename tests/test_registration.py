"""The plugin registers its asksage--* shims through the public shim API."""

from __future__ import annotations

import pytest

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_asksage import register_shims

_SHIMS = {
    "asksage--openai_chat": "openai_chat",
    "asksage--openai_responses": "openai_responses",
    "asksage--anthropic": "anthropic",
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
