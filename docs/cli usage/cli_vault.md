## Vault (HashiCorp)

### Overview

* Vault Secret Store grants programs the capability to store, read, share, and version sensitive information in secure manner. Each program is assigned a unique path to which they may store "secrets". Access to the secrets are obtained via AppRole, needing both a Role ID and Secret ID to begin the authentication process.

### Requirements

* JWT Token or AppRole IDs
* Click [here ](../vault/vault_token.md)for how to obtain JWT token and [here ](../vault/vault_approle.md)for how to obtain AppRole IDs

### Logging into the UI

* [Click Here ](../vault/login_vault.md) on how to log into the UI

### Vault CLI Usage

The Vault CLI allows you to manage secrets stored in Vault, including adding, updating, retrieving, and deleting secrets, as well as handling secret versions.

#### CLI Arguments

| Argument | Description |
|----------|-------------|
| \--vault-token VAULT_TOKEN | Vault token for authentication |
| \--vault-role-id VAULT_ROLE_ID | Vault AppRole role ID for authentication |
| \--vault-secret-id VAULT_SECRET_ID | Vault AppRole secret ID for authentication |
| \--service-name SERVICE_NAME | Service name for the secret. This can be anything such as the name of your app or tool. (default: default_service) |
| \--secrets SECRETS | Secrets to add.update in the form key=value |
| \--versions VERSIONS | Versions of the secret to operate on |
| \--mount-point MOUNT_POINT | Mount point for Vault secrets. This is the path to your secret folder. Automatically defaults to your user profile folder |

#### Add Secrets

To add a new secret to Vault:

```bash
vault-cli add --service-name <service_name> --secrets <secret_name>=<secret_value>
```

You can add multiple secrets by repeating the `--secrets` option:

**Example:**

```bash
vault-cli add --service-name test --secrets creds=creds --secrets user=user
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Credentials successfully added:
Name: test
Secret: {'creds': 'creds', 'user': 'user'}
```

#### Get Secrets

To retrieve a secret from Vault:

```bash
vault-cli get --service-name <service_name>
```

**Example:**

```bash
vault-cli get --service-name test
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Credentials successfully retrieved for test:
{
    "creds": "creds",
    "user": "user"
}
```

#### Delete Secrets

To delete a secret from Vault:

```bash
vault-cli delete --service-name <service_name>
```

**Example:**

```bash
vault-cli delete --service-name test
INFO:test1:Authenticating with Vault...
INFO:test1:Successfully authenticated with Vault using token.
INFO:test1:Checking Vault token status...
INFO:test1:Vault token is still valid.
👍 Credentials successfully deleted:
Name: test
```

#### Update Secrets

To update an existing secret in Vault:

```bash
vault-cli update --service-name <service_name> --secrets <secret_name>=<new_secret_value>
```

You can update multiple secrets by repeating the `--secrets` option:

**Example:**

```bash
vault-cli update --service-name test --secrets name=name --secrets pass=pass
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Credentials successfully updated:
Name: test
Credentials: {'name': 'name', 'pass': 'pass'}
```

#### List Secrets

To list all secrets in a specified path:

```bash
vault-cli list --service-name <service_name> 
```

**Example:**

```bash
vault-cli list --service-name test
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
ERROR:test:Failed to list secrets in test: None, on list https://vault-ent.acme.com/v1/user/metadata/test
👍 Secrets listed:
Name: test
Credentials: []
```

#### Read Secret Metadata

To read the metadata of a secret:

```bash
vault-cli read-metadata --service-name <service_name> 
```

**Example:**

```bash
vault-cli read-metadata --service-name test
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Metadata successfully retrieved for test:
{
    "request_id": "7eddfd00-5150-b889-ac8c-d92af2879c9a",
    "lease_id": "",
    "renewable": false,
    "lease_duration": 0,
    "data": {
        "cas_required": false,
        "created_time": "2024-06-18T11:51:41.010263874Z",
        "current_version": 3,
        "custom_metadata": null,
        "delete_version_after": "0s",
        "max_versions": 0,
        "oldest_version": 0,
        "updated_time": "2024-06-18T11:58:00.635343884Z",
        "versions": {
            "1": {
                "created_time": "2024-06-18T11:51:41.010263874Z",
                "deletion_time": "",
                "destroyed": false
            },
            "2": {
                "created_time": "2024-06-18T11:56:11.972274564Z",
                "deletion_time": "",
                "destroyed": false
            },
            "3": {
                "created_time": "2024-06-18T11:58:00.635343884Z",
                "deletion_time": "",
                "destroyed": false
            }
        }
    },
    "wrap_info": null,
    "warnings": null,
    "auth": null
}
```

#### Delete Secret Versions

To delete specific versions of a secret:

```bash
vault-cli delete-versions --service-name <service_name>  --versions <version_numbers>
```

You can specify multiple versions by repeating the `--versions` option:

**Example:**

```bash
vault-cli delete-versions --service-name test --versions 1 --versions 2
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Deleted versions [1, 2] of secret 'test'
```

#### Undelete Secret Versions

To undelete specific versions of a secret:

```bash
vault-cli undelete-versions --service-name <service_name>  --versions <version_numbers>
```

You can specify multiple versions by repeating the `--versions` option:

**Example:**

```bash
vault-cli undelete-versions --service-name test --versions 1 --versions 2
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
👍 Undeleted versions [1, 2] of secret 'test'
```

#### Destroy Secret Versions

To destroy specific versions of a secret:

```bash
vault-cli destroy-versions --service-name <service_name>  --versions <version_numbers>
```

You can specify multiple versions by repeating the `--versions` option:

**Example:**

```bash
vault-cli destroy-versions --service-name test --versions 1 --versions 2
INFO:test:Authenticating with Vault...
INFO:test:Successfully authenticated with Vault using token.
INFO:test:Checking Vault token status...
INFO:test:Vault token is still valid.
INFO:test:Permanently remove the specified version data and numbers:
Versions: [1, 2]
Secret: test
👍 Destroyed versions [1, 2] of secret 'test'
```

#### Specify a Custom Mount (Other Folders Containing secrets)

If you want to specify a custom mount point instead of using the default username-based mount point:

```bash
vault-cli add --service-name my_service --name my_secret --secret my_value --secret-type access_code --mount-point custom_mount_point
```