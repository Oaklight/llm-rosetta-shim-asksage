# llm-rosetta-shim-asksage

AskSage provider shims for [llm-rosetta](https://github.com/Oaklight/llm-rosetta),
delivered as a **plugin package** rather than as built-in shims.

The `asksage--*` shims left llm-rosetta core in 0.14.0
([#666](https://github.com/Oaklight/llm-rosetta/issues/666)); this package is now
their only source. Declare it in the gateway config and existing provider
entries keep their names:

```jsonc
{ "shims": { "presets": ["asksage"] } }
```

`shims.presets` expands to this repository's archive path via llm-rosetta's
catalogue; the equivalent explicit entry is `{"url": "...", "path":
"src/llm_rosetta_shim_asksage/providers"}`. The repository is public, so no
`token_env` is needed.

## Shims

| Shim | Model type | Format |
|:---|:---|:---|
| `asksage--chat_completions` | `llm` | `chat_completions` |
| `asksage--open_responses` | `llm` | `open_responses` |
| `asksage--messages` | `llm` | `messages` |
| `asksage--google_generate` | `llm` | `google_generate` |
| `asksage--embeddings` | `embeddings` | `openai` |

`asksage--embeddings` targets the embeddings lane asksage-proxy adds by hand at
`POST /server/openai/v1/embeddings` (Oaklight/asksage-proxy PR #10), so its base
is the same `/server/openai/v1` root as the chat lane and its path is
`/embeddings`.

`asksage--messages` targets `/server/anthropic`.  Measured 2026-11-06 against
the ANL deployment, that path answers HTTP 200 with an OpenAI `chat.completion`
body rather than a Messages envelope, so an ANL provider should use
`asksage--chat_completions` and let the gateway convert the client's Messages
request into the upstream chat lane.

The pre-0.14 spellings `asksage--openai_chat`, `asksage--openai_responses` and
`asksage--anthropic` no longer resolve: this package registers the canonical
names only. Update a legacy spelling to the canonical name above.

All use AskSage's API-key env `ASKSAGE_API_KEY`; the `google_generate` leaf
overrides the auth header to `x-access-tokens`, the `chat_completions` and
`open_responses` leaves add field renames, and the `embeddings` leaf declares
only its base URL and path. Unlike the argo/alcf packages, these transforms use
only absolute imports.

## Credentials

AskSage's inference lanes take a short-lived access token minted by
`POST {host}/user/get-token-with-api-key`, and that token is the credential this
package sends by default. The exchange ships with this package — the vendor
manifest declares `connection.token_command: [python3, token.py]`, which every
leaf inherits — so a provider needs no `token_command` of its own: the gateway
runs the exchange at startup, on the declared interval and after an upstream
401. A provider that names its own command still wins.

Measured 2026-11-06 against the ANL deployment: the raw account key is accepted
directly by the OpenAI lanes.  `POST /server/openai/v1/chat/completions` and
`POST /server/openai/v1/responses` both answer 200 with a real body, and
`/server/openai/v1/embeddings` passes authentication and then answers 503
`Embedding service unavailable` (a bogus key gets the `Token is invalid [2]`
envelope on the same path, so the 503 is the service, not the credential).
That makes the earlier statement that the inference lanes refuse the key stale
for this account.  The minted-token default is unchanged.

The manifest also declares `connection.token_command_env: ASKSAGE_API_KEY`, so the
account key an operator enters in the admin panel is handed to the exchange in that
variable — it is the command's input, and the minted token is what goes upstream.
Exporting `ASKSAGE_API_KEY` (or `ASKSAGE_TOKEN_API_KEY` / `ASK_SAGE_API`) in the
gateway's environment still works and feeds the same variable.

The gateway's non-LLM endpoints install a static key only, so an embeddings
provider configured through `asksage--embeddings` inherits the manifest's
`token_command` and the gateway disables that endpoint with the reason
`mints its credential with a token_command; non-LLM endpoints support a static
key only`.  The leaf keeps that inherited credential on purpose: a per-leaf
exception would be deleted again once typed endpoints share the minting
([#1401](https://github.com/Oaklight/llm-rosetta/issues/1401)).  Until then,
declare the endpoint without the shim:

```jsonc
{
  "embeddings_providers": {
    "asksage": {
      "format": "openai",
      "base_url": "https://api.asksage.anl.gov/server/openai/v1",
      "embeddings_path": "/embeddings",
      "api_key": "<account key>"
    }
  },
  "embeddings_models": {
    "text-embedding-3-small": "asksage"
  }
}
```

Two keys in that shape are easy to get wrong. Inside an `embeddings_providers`
entry the wire dialect is `format`, not `embeddings_format` — the latter is not
read and the entry silently keeps the `openai` default. And the provider alone
resolves nothing: a request's `model` is looked up in `embeddings_models`, so
without that mapping `POST /v1/embeddings` answers
`404 Unknown model: '<id>'. Configured: (none)` and never calls upstream.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-asksage
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `asksage--*` shims automatically.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.14.0.dev28` (the plugin shim loader, the vendor manifest **and**
  `connection.token_command`;
  an older core ignores the key and the provider would start with no credential)
- One of `ASKSAGE_TOKEN_API_KEY` / `ASK_SAGE_API` / `ASKSAGE_API_KEY` in the
  gateway's environment, for the shipped exchange to mint its token

## License

MIT — see [LICENSE](LICENSE).
