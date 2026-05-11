# Backend Comparison

Choose the right backend for your use case.

| Feature | Vault | Keyring | .env File |
|---|---|---|---|
| **Best for** | Production / team secrets | Local dev credentials | App configuration |
| **Storage** | Remote Vault server | OS credential store | File on disk |
| **Versioning** | ✓ KV-v2 multi-version | ✗ | ✗ |
| **Token / TTL rotation** | ✓ | ✗ | ✗ |
| **Multi-field secrets** | ✓ | ✓ (JSON-serialised) | ✓ |
| **`list_secrets()`** | ✓ | ✗ (platform limit) | ✓ |
| **Cross-platform** | ✓ | ✓ | ✓ |
| **Audit log** | ✓ | ✗ | ✗ |
| **Requires server** | ✓ | ✗ | ✗ |
| **`add_secret` if exists** | Creates new version (safe) | Raises `KeyringError` | Raises `EnvFileKeyExistsError` |
| **`update_secret` behaviour** | Merges (other keys kept) | Replaces entire dict | Replaces matching lines |
| **`get_secret` by group label** | ✗ | ✗ | ✓ |
| **`delete_secret` by group label** | ✗ | ✗ | ✓ |

## Decision guide

**Use Vault when:**

- You need team-shared, centrally managed credentials
- You need audit logs and access policies
- You're in a CI/CD pipeline with Vault already configured

**Use Keyring when:**

- You need to store personal developer credentials locally
- You want OS-level encryption with no server to maintain
- You're building a desktop app or developer CLI tool

**Use .env File when:**

- You follow 12-factor app configuration
- You need human-readable, repo-adjacent config (excluded from git)
- You need to populate `os.environ` for a process

## Using multiple backends

You can mix backends in one application:

```python
from credential_bridge import SecretsManager

# Production secrets from Vault
vault = SecretsManager("vault", vault_token="s.xxx")
db_creds = vault.get_secret("myapp/database")

# Developer token from local keyring
kr = SecretsManager("keyring", service_name="myapp")
api_key = kr.get_secret("github_token")

# App config from .env
env = SecretsManager("env", path=".env")
env.add_secret("DATABASE", {"DB_HOST": db_creds["host"]})
```
