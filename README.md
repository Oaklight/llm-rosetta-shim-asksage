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

## Credentials

AskSage's inference lanes do not accept the account API key directly: they take a
short-lived access token minted by `POST {host}/user/get-token-with-api-key`. The
exchange ships with this package — every `provider.yaml` declares
`connection.token_command: [python3, ../token.py]` — so a provider needs no
`token_command` of its own: the gateway runs the exchange at startup, on the
declared interval and after an upstream 401. A provider that names its own command
still wins.

The manifest also declares `connection.token_command_env: ASKSAGE_API_KEY`, so the
account key an operator enters in the admin panel is handed to the exchange in that
variable — it is the command's input, and the minted token is what goes upstream.
Exporting `ASKSAGE_API_KEY` (or `ASKSAGE_TOKEN_API_KEY` / `ASK_SAGE_API`) in the
gateway's environment still works and feeds the same variable.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-asksage
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `asksage--*` shims automatically.

## Archive and mirror

Every release publishes one archive of the bundled shims, so a gateway can load
them from a host other than GitHub. `main` never carries it: `dist/` is build
output and is in `.gitignore`.

- `v<version>/asksage.tar.gz` and `v<version>/asksage.tar.gz.sha256` live on the
  orphan `dist` branch.
- The same bytes are attached to the GitHub Release, with the digest in its
  notes.

Two interchangeable, version-pinned URLs for the same bytes:

```
https://github.com/Oaklight/llm-rosetta-shim-asksage/releases/download/v<version>/asksage.tar.gz
https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-asksage@dist/v<version>/asksage.tar.gz
```

The archive's root is `providers/`, the layout the package ships under
`src/llm_rosetta_shim_asksage/providers`, so a gateway source declares
`path: "providers"`:

```jsonc
{
  "shims": {
    "remotes": [
      {
        "url": "https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-asksage@dist/v<version>/asksage.tar.gz",
        "path": "providers",
        "archive": "tar.gz",
        "sha256": "<digest from v<version>/asksage.tar.gz.sha256>"
      }
    ]
  }
}
```

The digest is what pins the mirror, and the same value appears in the release
notes. jsDelivr is only the default suggestion: the gateway accepts any URL that
serves the same bytes, an internal mirror included.

### Publishing a release

1. Bump `__version__` in `src/llm_rosetta_shim_asksage/__init__.py`. The tag
   must match it — the release workflow passes the tag without its `v` as
   `--expect-version` and refuses a mismatch.
2. `python scripts/build_shim_archive.py --write` builds
   `dist/v<version>/asksage.tar.gz` and its digest locally and verifies the
   layout. CI runs the same build without writing on every push, so a tree whose
   `providers/` layout changed fails before a tag is cut.
3. Tag and push: `git tag v<version> && git push origin v<version>`.
4. `.github/workflows/release.yml` builds from the tag, creates or updates the
   GitHub Release, uploads the archive and its digest file, and commits
   `v<version>/` to the `dist` branch.

The workflow requests `contents: write` for `GITHUB_TOKEN`, because it creates
the release and pushes `dist`. An organization that downgrades action tokens to
read-only must restore "Read and write permissions" under Settings → Actions →
General, or the release step fails.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.14.0.dev28` (the plugin shim loader, the vendor manifest **and**
  `connection.token_command`;
  an older core ignores the key and the provider would start with no credential)
- One of `ASKSAGE_TOKEN_API_KEY` / `ASK_SAGE_API` / `ASKSAGE_API_KEY` in the
  gateway's environment, for the shipped exchange to mint its token

## License

MIT — see [LICENSE](LICENSE).
