# .env File Backend

Use `EnvFileBackend` to read and write secrets in a `.env` file. Ideal for local development and 12-factor app configuration.

!!! security "Never commit .env to git"
    Add `.env` to your `.gitignore` to prevent accidentally committing secrets.

## Usage

```python
from credential_bridge import EnvFileBackend

backend = EnvFileBackend(path=".env")  # default: .env in current directory

# Add a single key
backend.add_secret("API_KEY", {"API_KEY": "sk-abc123"})

# Add a group of related keys
backend.add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_NAME": "mydb"})

# Get a key
secret = backend.get_secret("API_KEY")
print(secret["API_KEY"])  # sk-abc123

# Update (partial — only specified keys changed, others untouched)
backend.update_secret("DB_HOST", {"DB_HOST": "prod-db.example.com"})

# Delete
backend.delete_secret("API_KEY")

# List all keys
keys = backend.list_secrets()  # ["API_KEY", "DB_HOST", "DB_PORT", "DB_NAME"]
```

## File format

`add_secret("database", {"DB_HOST": "localhost", "DB_PORT": "5432"})` produces:

```
# database
DB_HOST=localhost
DB_PORT=5432
```

## Auto-load into os.environ

```python
backend = EnvFileBackend(path=".env", load_into_environ=True)
backend.add_secret("API_KEY", {"API_KEY": "sk-abc123"})
# os.environ["API_KEY"] is now "sk-abc123"
```

Syncing into `os.environ` only happens on mutating operations (add, update, delete). `get_secret()` and `list_secrets()` do not trigger a sync.

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str \| Path` | `".env"` | Path to the .env file. |
| `load_into_environ` | `bool` | `False` | Sync changes into `os.environ` on write. |
| `encoding` | `str` | `"utf-8"` | File encoding. |

## Atomic writes

All write operations (add, update, delete) use an atomic write strategy:

1. Write new content to `.env.tmp`
2. Rename `.env.tmp` → `.env` using `os.replace()` (atomic and cross-platform)

This prevents file corruption if the process is interrupted mid-write.

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `EnvFileError: already exist` | Key already in file | Use `update_secret()` to change it |
| `EnvFileNotFoundError` | Key not found | Check the key name with `list_secrets()` |
| `EnvFileError: not found` | `update_secret()` called on missing key | Use `add_secret()` first |

## CLI equivalent

```bash
cb env add API_KEY --secret API_KEY=sk-abc123
cb env add database --secret DB_HOST=localhost --secret DB_PORT=5432
cb env get API_KEY
cb env update API_KEY --secret API_KEY=sk-new
cb env delete API_KEY --yes
cb env list
```
