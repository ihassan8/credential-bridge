# Interactive Wizard

The interactive wizard provides a menu-driven interface for managing secrets without memorizing CLI flags.

## Launch

```bash
cb wizard
# or
run-wizard
```

## Supported backends

- **keyring** — system keyring operations (add/get/update/delete)
- **vault** — HashiCorp Vault operations (add/get/update/delete/list/metadata/versions)
- **env** — .env file operations (add/get/update/delete/list)

## Vault authentication

When you select the `vault` backend, the wizard will check for existing saved credentials in `~/.vault_config.json`. If none exist, it prompts you to enter a token or AppRole credentials. Valid credentials are saved for future sessions.

!!! security "VAULT_ADDR required"
    Set the `VAULT_ADDR` environment variable before launching the wizard.

## Features

- Tab-completion for all menu options
- Credential caching across sessions
- Masked input for sensitive values
- Clear error messages
