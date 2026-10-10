# llm-rosetta-shim-asksage

AskSage provider shims for [llm-rosetta](https://github.com/Oaklight/llm-rosetta),
delivered as a **plugin package** rather than as built-in shims.

Standalone-repository variant of
[llm-rosetta#666](https://github.com/Oaklight/llm-rosetta/issues/666), verifying the
plugin shim loader ([#272](https://github.com/Oaklight/llm-rosetta/issues/272) /
[#273](https://github.com/Oaklight/llm-rosetta/issues/273)) against a real shim set.
The built-in `asksage--*` shims stay in llm-rosetta for now.

## Shims

| Shim | Base |
|:---|:---|
| `asksage--openai_chat` | `openai_chat` |
| `asksage--openai_responses` | `openai_responses` |
| `asksage--anthropic` | `anthropic` |
| `asksage--google_generate` | `google_generate` |

All use AskSage's API-key env `ASKSAGE_API_KEY`; the `google_generate` leaf
overrides the auth header to `x-access-tokens`, and the openai_* leaves add
field renames. Unlike the argo/alcf packages, these transforms use only absolute
imports.

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
