"""The plugin registers its asksage--* shims through the public shim API."""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_rosetta.shims import get_shim, load_providers_from_dir
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_asksage import register_shims

#: The directory the package ships and the entry point loads.
_PROVIDERS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "llm_rosetta_shim_asksage"
    / "providers"
)

_SHIMS = {
    "asksage--chat_completions": "chat_completions",
    "asksage--open_responses": "open_responses",
    "asksage--messages": "messages",
    "asksage--google_generate": "google_generate",
    "asksage--embeddings": "openai",
}

#: Every leaf forwards to the vendor's host; only the lane root below it
#: distinguishes them.
_EXPECTED_HOST = "https://api.asksage.ai"


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
def test_every_leaf_stays_on_the_asksage_host(_registered, name):
    """A leaf's base URL is the vendor host plus its own lane root."""
    shim = get_shim(name)
    assert shim is not None
    base_url = shim.connection.base_url
    assert base_url is not None
    assert base_url.startswith(f"{_EXPECTED_HOST}/server/")


def test_the_embeddings_leaf_is_a_typed_endpoint(_registered):
    """The lane is an embeddings one, served by the OpenAI wire dialect."""
    shim = get_shim("asksage--embeddings")
    assert shim is not None
    assert shim.model_type == "embeddings"
    assert shim.format == "openai"
    # `base_url` already carries `/openai/v1` and the gateway concatenates
    # `{base_url}{default_path}`, so the path is the bare tail; `/v1/embeddings`
    # here would append a second `/v1`.
    assert shim.connection.base_url == f"{_EXPECTED_HOST}/server/openai/v1"
    assert shim.connection.default_path == "/embeddings"


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
    assert script.name == "mint_token.py"
    # The exchange takes the account key as input; without this the key the
    # operator enters in the panel would never reach the command.
    assert shim.connection.token_command_env == "ASKSAGE_API_KEY"


@pytest.mark.parametrize("name", sorted(_SHIMS))
def test_the_credential_comes_from_the_vendor_manifest(_registered, name):
    """The manifest holds the credential once; each leaf only adds its URL."""
    shim = get_shim(name)
    assert shim is not None
    assert shim.manifest is not None
    assert shim.manifest.path.name == "provider.yaml"
    assert shim.connection.api_key_env == "ASKSAGE_API_KEY"
    assert shim.connection.token_command_env == "ASKSAGE_API_KEY"
    script = Path(shim.connection.token_command[1])
    assert script.name == "mint_token.py" and script.is_file()


def test_the_embeddings_endpoint_is_disabled_with_the_minting_reason(_registered):
    """The inherited ``token_command`` is refused by the typed endpoint's gate.

    Non-LLM endpoints install a static key only, so the gateway drops the
    provider and records why.  Pinned here: once typed endpoints share the
    minting (Oaklight/llm-rosetta#1401) this test has to be rewritten, which is
    the point — an operator-visible change should not slip through silently.
    """
    from llm_rosetta_gateway.config import GatewayConfig

    raw: dict = {
        "embeddings_providers": {
            "asksage": {"embeddings_shim": "asksage--embeddings", "api_key": "x"},
        }
    }

    cfg = GatewayConfig(raw)

    assert "asksage" not in cfg.embeddings_providers
    marker = raw["embeddings_providers"]["asksage"]["_auto_disabled_endpoints"]
    assert "mints its credential with a token_command" in marker["embeddings"]["reason"]


def test_the_shipped_directory_registers_every_leaf():
    """Load the files, not the entry point: this is what ships and what loads.

    ``register_shims`` needs an installed package and reaches the directory
    through the entry point.  This walks ``providers/`` the way the gateway's
    loader does, so a leaf the loader skips — an unknown ``model_type``, a
    manifest read as a shim — fails here rather than glowing green on a
    registry that some other call filled.
    """
    _reset_registry()

    loaded = load_providers_from_dir(_PROVIDERS)

    assert sorted(shim.name for shim in loaded) == sorted(_SHIMS)
    assert get_shim("asksage--embeddings") is not None
