## FEDS Vault

### Overview

* Vault Secret Store grants programs the capability to store, read, share, and version sensitive information in secure manner. Each program is assigned a unique path to which they may store "secrets". Access to the secrets are obtained via AppRole, needing both a Role ID and Secret ID to begin the authentication process.

### Requirements

* JWT Token or AppRole IDs
* Click [here ](../vault/vault_token.md)for how to obtain JWT token and [here ](../vault/vault_approle.md)for how to obtain AppRole IDs

### Logging into the UI

* [Click Here ](../vault/login_vault.md) on how to log into the UI

### Initialize the VaultManager

```python
from credential_bridge import VaultManager

my_vault = VaultManager(
    # Provide either a Vault token or Approle credentials, not both.
    vault_token="your_token",
    vault_role_id="your_role_id",
    vault_secret_id="your_secret_id",
    service_name="your_service_name",
    mount_point="your_secret_folder" # Default to username
)
```
### Add secrets
```
my_vault.add_secret("my_secret", {"key": "value"})
```
### Get secrets
```
my_vault.get_secret("my_secret")
```

### Update secrets
```
my_vault.update_secret("my_secret", {"key": "new_value"})
```
### Delete secrets
```
my_vault.delete_secret("my_secret")
```