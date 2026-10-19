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

| Shim | Base |
|:---|:---|
| `asksage--chat_completions` | `chat_completions` |
| `asksage--open_responses` | `open_responses` |
| `asksage--messages` | `messages` |
| `asksage--google_generate` | `google_generate` |

The pre-0.14 spellings `asksage--openai_chat`, `asksage--openai_responses` and
`asksage--anthropic` no longer resolve: this package registers the canonical
names only. Update a legacy spelling to the canonical name above.

All use AskSage's API-key env `ASKSAGE_API_KEY`; the `google_generate` leaf
overrides the auth header to `x-access-tokens`, and the `chat_completions` and
`open_responses` leaves add field renames. Unlike the argo/alcf packages, these
transforms use only absolute imports.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-asksage
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `asksage--*` shims automatically.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.13.0` (needs the plugin shim loader)
- `ASKSAGE_API_KEY` in the environment at request time

## License

MIT — see [LICENSE](LICENSE).
