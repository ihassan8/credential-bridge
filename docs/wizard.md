# Interactive Wizard

The interactive wizard provides a menu-driven interface for all backend operations without memorising CLI flags. It uses Rich for styled output and prompt_toolkit for smart input with tab-completion and command history.

## Launch

```bash
cb wizard
run-wizard
python -m credential_bridge wizard
```

`run-wizard` is a console script entry point installed alongside `cb` — it launches the same interactive wizard.

## Welcome screen

On launch the wizard renders a branded banner and drops into the main menu:

```
▶ Backend  (keyring / vault / env / exit):
```

Tab-complete any option or type it in full. Arrow-up recalls previous entries (session history is maintained).

## Keyring

```
[Keyring]  (add / get / update / delete / back):  add
  Service name:   myapp
  Secret name:    github_token
  Secret value:   ········        ← masked input
  ✓  Added github_token to keyring service 'myapp'.
```

All secret values are masked with `●` as you type.

## Vault

### Authentication

Select an auth type first:

```
[Vault]  (vault_token / approle / back):  vault_token
  Vault Token:  ········
  ✓  Vault token saved.
```

The token is validated against Vault before being saved. Saved credentials are loaded automatically on the next session — you won't be prompted again unless they expire.

!!! tip "VAULT_ADDR required"
    Set `VAULT_ADDR` before launching the wizard:
    ```bash
    export VAULT_ADDR=https://vault.example.com
    ```

### Operations

When you enter the Vault session you are asked for a **service name** (a logging tag) once. After that you choose an action and supply a secret path for each operation:

```
  Service name (tag):  myapp

[Vault › vault_token]  (add/get/update/delete/list/… /back):  add
  Secret path (e.g. myapp/db):    myapp/database
  Number of key-value pairs:      2
  Key 1:    user
  Value 1:  ········
  Key 2:    pass
  Value 2:  ········
  ✓  Secret myapp/database added.
```

Available actions:

| Action | Description |
|---|---|
| `add` | Add a new secret |
| `get` | Retrieve and display a secret |
| `update` | Update existing fields |
| `delete` | Permanently delete all versions |
| `list` | List secrets at a path |
| `read-metadata` | Show version metadata |
| `delete-versions` | Soft-delete specific versions |
| `undelete-versions` | Restore soft-deleted versions |
| `destroy-versions` | Permanently destroy specific versions |
| `get-config` | Show mount configuration |
| `back` | Return to backend selection |

### Result display

Get results are shown as syntax-highlighted JSON:

```
╭──────────────── myapp/database ────────────────╮
│ {                                              │
│   "user": "admin",                             │
│   "pass": "s3cr3t"                             │
│ }                                              │
╰────────────────────────────────────────────────╯
```

## .env File

```
[.env]  .env file path  (default: .env):  config/.env

[.env › config/.env]  (add / get / update / delete / list / back):  list
  Keys in config/.env
 ┌─────────┐
 │ Key     │
 ├─────────┤
 │ DB_HOST │
 │ DB_PORT │
 └─────────┘
```

The `.env` path is asked once per session — you don't need to re-enter it for each operation.

When adding a key, you are also prompted for an optional **group label** (a `# label` comment written above the key in the file). Leave it blank to use the key name as the label, or enter a custom label to group multiple related keys under a meaningful heading.

## Exiting

Type `exit` at the main menu or press `Ctrl+C` / `Ctrl+D` at any prompt to exit gracefully.

## Tips

- **Tab-completion**: All menu options support tab-completion
- **History**: Press `↑` to recall previous entries within the session
- **Masked input**: Vault tokens, AppRole credentials, and secret values are always masked
- **Breadcrumbs**: The prompt shows your current location (e.g. `[Vault › approle]`)
