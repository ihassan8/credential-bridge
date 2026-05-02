# src/credential_bridge/cli/main.py
import typer

from .env_cli import app as env_app
from .keyring_cli import app as keyring_app
from .vault_cli import app as vault_app

app = typer.Typer(
    name="cb",
    help="Credential Bridge — unified secrets management CLI",
    no_args_is_help=True,
)

app.add_typer(vault_app, name="vault")
app.add_typer(keyring_app, name="keyring")
app.add_typer(env_app, name="env")


@app.command()
def wizard():
    """Launch the interactive secrets wizard."""
    # Use alias to avoid shadowing this module's main() entry point
    from ..prompt_wizard import main as _wizard_main
    _wizard_main()


def main():
    """Entry point registered in pyproject.toml as cb = credential_bridge.cli.main:main"""
    app()
