## Overview

* This interactive wizard allows you to intuitively interact with both keyring and vault. It had some pre-default drop-down options where you can easily pick and choose the action you want to performs. This is recommended for users who don't like to use pass required arguments manually.

## Vault

### Requirements

* JWT Token or AppRole IDs
* Click [here ](../vault/vault_token.md)for how to obtain JWT token and [here ](../vault/vault_approle.md)for how to obtain AppRole IDs

### Logging into the UI

* [Click Here ](../vault/login_vault.md) on how to log into the UI

### Basic Usage

Open your anaconda prompt and run the following command.

```bash
run-wizard
```

1. When prompted for `Choose service to configure` select or type `vault`.
2. When prompted for `Choose authentication type` select `vault_token` or `approle. Please refer to the requirement section of this document on obtaining `vault_token` or `approle`. 
3. If you select `approle` then you will be promted to enter `Enter Role ID` and `Enter Secret ID`. You will only have to do this once and then the tool will save your creds in your local USERPROFILE directory as `.vault_config.json`
4. If you select `vault_token` then you will be promted to enter `Enter Vault Token`. You will only have to do this once and then the tool will save your creds in your local USERPROFILE directory as `.vault_config.json`

### Add Secrets

1. When prompted for `Choose action` select or type `add`.
2. When prompted for `SERVICE NAME` type in the name of your app/system. This is name you can use to pull the specified to token in your projects.
3. When prompted for `NUMBER OF SECRETS` type in the number of secrets you want to store for that service name. Normally your would store one but there are systems that also have seperate key for the integrated environment.
4. When prompted for `SECRET NAME:` type in the name of your secret key. `Ex. token, token-prod, token-int, etc`.

![vault_add.png](../img/vault/vault_add.png)

### Delete Secrets

1. When prompted for `Choose action:` select or type `delete`.
2. When prompted for `Enter Service Name:` type in the name of your app/system and then hit `Enter`. This command will delete the key for that `SERVICE NAME`.

![vault_delete.png](../img/vault/vault_delete.png)

### Update Secrets

1. When prompted for `Choose action:` select or type `update`.
2. When prompted for `Enter Service Name:` type in the name of your app/system.
3. When prompted for `NUMBER OF SECRETS` type in the number of secrets you want to update for that service name. Normally your would store one but there are systems that also have seperate key for the integrated environment.
4. When prompted for `Enter Secret Value:` type in the new secret that you want to add.

![vault_update.png](../img/vault/vault_update.png)

### Get Stored Secrets

1. When prompted for `Choose action:` select or type `get`.
2. When prompted for `Enter Service Name:` type in the name of your app/system.

![vault_get.png](../img/vault/vault_get.png)

### Get Secrets Metadata

1. When prompted for `Choose action:` select or type `read-metadata`.
2. When prompted for `Enter Service Name:` type in the name of your app/system.

![vault_metadata.png](../img/vault/vault_metedata.png)

### Delete Specified Versions

1. In Vault as you add new secrets it creates copy of new version while retaining the old ones.
    ![version.png](../img/vault/versions.png)
2. You can delete the version by excecuting `delete-versions` command.
3. When prompted for `Choose action:` select or type `delete-versions`.
4. When prompted for `Enter the number of versions to delete/undelete/destroy:` type in the number of versions you want to delete from the `SERVICE NAME`.
5. When prompted for `Enter version number:` type in the version number you want to delete and then hit `ENTER`.

![vault_version.png](../img/vault/vault_versions.png)


## Keyring

1. When prompted for `Choose service to configure` select or type `keyring`.

### Add Secret

1. When prompted for `Choose action:` select or type `add`.
2. When prompted for `Enter Service Name:` type in the name of your app/system. This is name you can use to pull the specified to token in your projects.
3. When prompted for `Enter Secret Name:` type in the name of your secret key. `Ex. token, token-prod, token-int, etc`.
4. When prompted for `Enter Secret:` type in the secret you want to store.

![key_add.png](../img/vault/key_add.png)

### Delete Secret

1. When prompted for `Choose action:` select or type `delete`.
2. When prompted for `Enter Service Name:` type in the name of your app/system and then hit `Enter`. This command will delete the key for that `SERVICE NAME`.

![key_delete.png](../img/vault/key_delete.png)

### Update Secret

1. When prompted for `Choose action:` select or type `update`.
2. When prompted for `Enter Service Name:` type in the name of your app/system.
3. When prompted for `Enter Secret Name:` type in the name of your secret key. `Ex. token, token-prod, token-int, etc`.
4. When prompted for `Enter Secret:` type in the secret you want to store.

![key_update.png](../img/vault/key_update.png)

### Get Stored Secret

1. When prompted for `Choose action:` select or type `get`.
2. When prompted for `Enter Service Name:` type in the name of your app/system.
3. When prompted for `Enter Secret Name:` type in the name of your secret key. `Ex. token, token-prod, token-int, etc`.

![key_get.png](../img/vault/key_get.png)