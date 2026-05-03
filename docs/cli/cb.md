# Unified CLI — cb

`cb` is the single entry point for all credential-bridge operations.

## Install & invoke

```bash
# Standard
cb --help

# python -m fallback (when executables are blocked)
python -m credential_bridge --help
```

## Commands

| Command | Description |
|---|---|
| `cb vault` | HashiCorp Vault operations |
| `cb keyring` | System keyring operations |
| `cb env` | .env file operations |
| `cb wizard` | Interactive wizard |

## Global flags

| Flag | Description |
|---|---|
| `--version`, `-V` | Print version and exit |
| `--help` | Show help |
| `--install-completion` | Install shell tab-completion |

## Version

```bash
cb --version
# cb version 1.2.3
```

## Shell tab-completion

```bash
cb --install-completion   # installs for current shell
cb --show-completion      # prints the completion script
```

## Interactive mode fallback

When `--secret` is omitted from `add` or `update` commands, the CLI prompts for secrets interactively with masked input:

```
$ cb env add DB_URL
Enter secrets interactively. Leave KEY blank to finish.
  Key   : DB_URL
  Value : ········
  Key   :
✓  Secret DB_URL added to .env.
```

## Machine-readable output

All `get` and `list` commands support `--output json` for scripting:

```bash
cb vault get myapp/db --output json | jq '.user'
cb env list --output json | python3 -c "import sys,json; print(json.load(sys.stdin))"
```
