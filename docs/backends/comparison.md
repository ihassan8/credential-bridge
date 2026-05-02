# Backend Comparison

| Feature | Vault | Keyring | .env File |
|---|---|---|---|
| **Best for** | Production / team secrets | Local dev credentials | Environment config |
| **Storage** | Remote Vault server | OS credential store | File on disk |
| **Versioning** | ✓ KV-v2 | ✗ | ✗ |
| **Token/TTL rotation** | ✓ | ✗ | ✗ |
| **Multi-field secrets** | ✓ | ✓ (JSON) | ✓ |
| **`list_secrets()`** | ✓ | ✗ (platform limit) | ✓ |
| **Cross-platform** | ✓ | ✓ | ✓ |
| **Requires server** | ✓ | ✗ | ✗ |
| **Audit log** | ✓ | ✗ | ✗ |

## Choosing a backend

**Use Vault when:**

- You need centralized secrets for a team or production system
- You need audit trails, rotation, or access policies
- You're already using HashiCorp tooling

**Use Keyring when:**

- You need to store developer credentials locally (API keys, tokens)
- You want OS-level encryption without managing a server
- You're building a CLI tool or desktop application

**Use .env when:**

- You need to configure an application via environment variables
- You're following the 12-factor app methodology
- You want a human-readable, version-controllable secrets file (exclude from git!)
