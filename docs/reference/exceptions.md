# Exceptions

All credential-bridge exceptions inherit from `CredentialBridgeError`. Catch the base class to handle any library error, or catch specific subclasses for fine-grained handling.

## Hierarchy

```
CredentialBridgeError
├── BackendError                          base for all backend errors
│   ├── VaultError                        general Vault error
│   │   ├── VaultAuthError                bad token / AppRole credentials
│   │   ├── VaultConnectionError          unreachable server or bad URL
│   │   └── VaultSecretNotFoundError      secret path does not exist
│   ├── KeyringError                      OS keyring error
│   │   └── KeyringSecretNotFoundError    key does not exist in keyring
│   └── EnvFileError                      .env file error
│       ├── EnvFileNotFoundError          requested key or group not in file
│       └── EnvFileKeyExistsError         add_secret called on existing key
├── BackendNotRegisteredError             unknown backend name in SecretsManager
└── ConfigurationError                    missing required config (URL, credentials)
```

## Import

```python
from credential_bridge import (
    CredentialBridgeError,
    BackendError,
    VaultError,
    VaultAuthError,
    VaultConnectionError,
    VaultSecretNotFoundError,
    KeyringError,
    KeyringSecretNotFoundError,
    EnvFileError,
    EnvFileNotFoundError,
    EnvFileKeyExistsError,
    BackendNotRegisteredError,
    ConfigurationError,
)
```

## Usage examples

### Catch all library errors
```python
from credential_bridge import SecretsManager, CredentialBridgeError

try:
    sm = SecretsManager("vault", vault_token="s.xxx")
    result = sm.get_secret("myapp/db")
except CredentialBridgeError as e:
    print(f"credential-bridge error: {e}")
```

### Vault-specific handling
```python
from credential_bridge import (
    VaultAuthError, VaultConnectionError, VaultSecretNotFoundError, VaultError
)

try:
    result = backend.get_secret("myapp/db")
except VaultSecretNotFoundError:
    print("Secret does not exist — check the path")
except VaultAuthError:
    print("Token expired — renew in Vault UI")
except VaultConnectionError:
    print("Cannot reach Vault — check VAULT_ADDR")
except VaultError as e:
    print(f"General Vault error: {e}")
```

### Keyring-specific handling
```python
from credential_bridge import KeyringError, KeyringSecretNotFoundError

try:
    secret = backend.get_secret("my_token")
except KeyringSecretNotFoundError:
    print("Key does not exist in the keyring")
except KeyringError as e:
    print(f"Keyring backend failure: {e}")
```

### .env file handling
```python
from credential_bridge import EnvFileKeyExistsError, EnvFileNotFoundError

try:
    backend.add_secret("DB_HOST", {"DB_HOST": "localhost"})
except EnvFileKeyExistsError:
    # Key already in file — update instead
    backend.update_secret("DB_HOST", {"DB_HOST": "localhost"})

try:
    value = backend.get_secret("MISSING_KEY")
except EnvFileNotFoundError:
    print("Key not found in .env file")
```

### Unknown backend
```python
from credential_bridge import SecretsManager, BackendNotRegisteredError

try:
    sm = SecretsManager("aws")
except BackendNotRegisteredError as e:
    print(e)  # "Unknown backend 'aws'. Available: ['vault', 'keyring', 'env']"
```

### Missing configuration
```python
from credential_bridge import VaultBackend, ConfigurationError

try:
    backend = VaultBackend()  # no URL, no env var
except ConfigurationError as e:
    print(e)  # "Vault URL not configured. Pass vault_url= or set VAULT_ADDR..."
```

## Exception class reference

::: credential_bridge.exceptions
