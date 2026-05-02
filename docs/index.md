---
hide:
  - navigation
  - toc
---

<div class="cb-hero">
  <h1>Credential Bridge</h1>
  <p>Unified secrets management for Python — HashiCorp Vault, system keyring, and .env files through one clean API.</p>
  <div class="cb-hero-buttons">
    <a href="getting-started/installation/" class="cb-btn cb-btn-primary">Get Started</a>
    <a href="backends/comparison/" class="cb-btn cb-btn-outline">Compare Backends</a>
  </div>
</div>

<div id="cb-terminal-demo" class="cb-terminal"></div>

## Why Credential Bridge?

<div class="cb-cards">
  <div class="cb-card">
    <h3>🔌 Pluggable backends</h3>
    <p>Swap between Vault, keyring, and .env with a single constructor argument. Add custom backends in minutes.</p>
  </div>
  <div class="cb-card">
    <h3>🛡️ No silent failures</h3>
    <p>Every error raises a typed exception — <code>VaultAuthError</code>, <code>EnvFileNotFoundError</code>. Catch exactly what you need.</p>
  </div>
  <div class="cb-card">
    <h3>💻 Cross-platform</h3>
    <p>Works identically on Windows and Linux. No OS-specific code paths or environment variables.</p>
  </div>
  <div class="cb-card">
    <h3>🖥️ Modern CLI</h3>
    <p>Rich output, interactive prompts, and tab-completion via the <code>cb</code> unified command.</p>
  </div>
</div>

## Quick example

=== "SecretsManager"

    ```python
    from credential_bridge import SecretsManager

    # Vault
    sm = SecretsManager("vault", vault_token="s.xxx")
    sm.add_secret("myapp/db", {"user": "admin", "pass": "s3cr3t"})

    # .env file
    sm = SecretsManager("env", path=".env")
    sm.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})

    # System keyring
    sm = SecretsManager("keyring", service_name="myapp")
    sm.get_secret("api_key")
    ```

=== "Direct backends"

    ```python
    from credential_bridge import VaultBackend, KeyringBackend, EnvFileBackend

    vault = VaultBackend(vault_url="https://vault.example.com", vault_token="s.xxx")
    vault.add_secret("myapp/db", {"user": "admin"})

    env = EnvFileBackend(path=".env")
    env.add_secret("API_KEY", {"API_KEY": "sk-abc123"})
    ```
