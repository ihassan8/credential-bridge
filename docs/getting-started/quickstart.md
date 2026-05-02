# Quick Start

## Choose your backend

<select id="cb-backend-selector">
  <option value="all">All backends</option>
  <option value="vault">HashiCorp Vault</option>
  <option value="keyring">System Keyring</option>
  <option value="env">.env File</option>
</select>

## Add a secret

<div data-backend="vault">

```python
from credential_bridge import SecretsManager

sm = SecretsManager(
    "vault",
    vault_token="s.your-token",        # or set VAULT_TOKEN env var
    # vault_url is read from VAULT_ADDR env var automatically
)
sm.add_secret("myapp/database", {"user": "admin", "pass": "s3cr3t"})
```

</div>

<div data-backend="keyring">

```python
from credential_bridge import SecretsManager

sm = SecretsManager("keyring", service_name="myapp")
sm.add_secret("database", {"user": "admin", "pass": "s3cr3t"})
```

</div>

<div data-backend="env">

```python
from credential_bridge import SecretsManager

sm = SecretsManager("env", path=".env")
sm.add_secret("DATABASE", {"DB_HOST": "localhost", "DB_PORT": "5432"})
```

</div>

## Retrieve a secret

<div data-backend="vault">

```python
secret = sm.get_secret("myapp/database")
print(secret["user"])  # admin
```

</div>

<div data-backend="keyring">

```python
secret = sm.get_secret("database")
print(secret["user"])  # admin
```

</div>

<div data-backend="env">

```python
secret = sm.get_secret("DB_HOST")
print(secret["DB_HOST"])  # localhost
```

</div>

## Handle errors

```python
from credential_bridge import SecretsManager, CredentialBridgeError, VaultAuthError

try:
    sm = SecretsManager("vault", vault_token="bad-token")
except VaultAuthError as e:
    print(f"Auth failed: {e}")
except CredentialBridgeError as e:
    print(f"Other error: {e}")
```

## Via CLI

```bash
# Vault
cb vault add myapp/db --secret user=admin --secret pass=s3cr3t --vault-token s.xxx

# Keyring
cb keyring add database --secret user=admin --service-name myapp

# .env
cb env add DB_HOST --secret DB_HOST=localhost
```
