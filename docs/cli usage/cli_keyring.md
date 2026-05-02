## Keyring

### Overview

* The Python keyring library provides an easy way to access the system keyring service from python. It can be used in any application that needs safe password storage.

### Keyring CLI Usage

The Keyring CLI allows you to manage credentials stored in your system's keyring.

#### CLI Arguments

| Argument | Description |
|----------|-------------|
| \--service-name SERVICE_NAME | Service name for the credential |
| \--name NAME | Name of the secret. This can be anything such as the name of your app or tool. (default: default_service)|
| \--secret SECRET | Value of the secret |

#### Add Secret

```bash
keyring-cli add --service-name my_service --username my_user --password my_password
```

#### Get Secret

```bash
keyring-cli get --service-name my_service --username my_user
```

#### Delete Secret

```bash
keyring-cli delete --service-name my_service --username my_user
```

#### Update Secret

```bash
keyring-cli update --service-name my_service --username my_user --password new_password
```