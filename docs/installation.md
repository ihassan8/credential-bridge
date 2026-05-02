# Installation

## Requirements

- Python **3.8 or later**

## Install from PyPI

```bash
pip install credential-bridge
```

Upgrade to the latest release:

```bash
pip install --upgrade credential-bridge
```

## Development install

Clone the repository and install in editable mode:

```bash
git clone https://github.com/vertex-ai-automations/credential-bridge.git
cd credential-bridge
pip install -e ".[image]"
pip install -r requirements.txt
```

## Verify the installation

```bash
python -c "import credential-bridge; print(credential-bridge.__version__)"
credential-bridge --help
```

You should see the version number and the CLI help text.

!!! tip "Virtual environments"
    Always install into a virtual environment (`python -m venv .venv`) to avoid dependency conflicts.