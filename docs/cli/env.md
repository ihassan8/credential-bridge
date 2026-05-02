# .env CLI

The `cb env` subcommand manages secrets in a `.env` file.

## Global options

| Flag | Default | Description |
|---|---|---|
| `--path PATH` | `.env` | Path to the .env file |

## add

Add one or more key-value pairs to the .env file. Fails if any key already exists.

```bash
cb env add API_KEY --secret API_KEY=sk-abc123
cb env add database --secret DB_HOST=localhost --secret DB_PORT=5432
```

**Flags:**

| Flag | Required | Description |
|---|---|---|
| `NAME` | Yes | Label for the secret group |
| `--secret KEY=VALUE` | Yes (repeatable) | Key-value pair(s) to add |
| `--path PATH` | No | Path to the .env file |

## get

Retrieve a key's value from the .env file.

```bash
cb env get API_KEY
cb env get DB_HOST --path config/.env
```

Output:

```json
{
  "API_KEY": "sk-abc123"
}
```

## update

Update the value of an existing key. Fails if the key is not found.

```bash
cb env update API_KEY --secret API_KEY=sk-new
```

## delete

Remove a key from the .env file.

```bash
cb env delete API_KEY --yes
```

**Flags:**

| Flag | Description |
|---|---|
| `--yes` | Skip confirmation prompt |

## list

List all keys defined in the .env file.

```bash
cb env list
cb env list --path config/.env
```

Output:

```
API_KEY
DB_HOST
DB_PORT
DB_NAME
```
