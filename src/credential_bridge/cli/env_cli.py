# src/credential_bridge/cli/env_cli.py
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import json

from ..backends.env_file import EnvFileBackend
from ..exceptions import CredentialBridgeError

app = typer.Typer(name="env", help=".env file secret operations", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)


@app.command()
def add(
    name: str = typer.Argument(..., help="Group label / key name"),
    secret: Optional[List[str]] = typer.Option(None, "--secret", help="KEY=value pairs"),
    path: str = typer.Option(".env", "--path", "-p", help="Path to .env file"),
):
    """Add a secret to the .env file."""
    if not secret:
        typer.echo("Error: --secret is required", err=True)
        raise typer.Exit(1)
    backend = EnvFileBackend(path=path)
    secret_dict = dict(s.split("=", 1) for s in secret)
    try:
        backend.add_secret(name, secret_dict)
        console.print(Panel(f"[green]✓[/green] Secret [bold]{name}[/bold] added to {path}.", title="Success"))
    except CredentialBridgeError as e:
        err_console.print(Panel(f"[red]{e}[/red]", title="Error"))
        raise typer.Exit(1)


@app.command()
def get(
    name: str = typer.Argument(..., help="Env var key name"),
    path: str = typer.Option(".env", "--path", "-p"),
):
    """Get a secret from the .env file."""
    backend = EnvFileBackend(path=path)
    try:
        result = backend.get_secret(name)
        syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
        console.print(Panel(syntax, title=f"[bold]{name}[/bold]"))
    except CredentialBridgeError as e:
        err_console.print(Panel(f"[red]{e}[/red]", title="Error"))
        raise typer.Exit(1)


@app.command()
def update(
    name: str = typer.Argument(..., help="Env var key name"),
    secret: Optional[List[str]] = typer.Option(None, "--secret", help="KEY=value pairs"),
    path: str = typer.Option(".env", "--path", "-p"),
):
    """Update a secret in the .env file."""
    if not secret:
        typer.echo("Error: --secret is required", err=True)
        raise typer.Exit(1)
    backend = EnvFileBackend(path=path)
    secret_dict = dict(s.split("=", 1) for s in secret)
    try:
        backend.update_secret(name, secret_dict)
        console.print(Panel(f"[green]✓[/green] [bold]{name}[/bold] updated in {path}.", title="Success"))
    except CredentialBridgeError as e:
        err_console.print(Panel(f"[red]{e}[/red]", title="Error"))
        raise typer.Exit(1)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Env var key name"),
    path: str = typer.Option(".env", "--path", "-p"),
    confirm: bool = typer.Option(False, "--yes", "-y"),
):
    """Delete a secret from the .env file."""
    if not confirm:
        typer.confirm(f"Delete '{name}' from {path}?", abort=True)
    backend = EnvFileBackend(path=path)
    try:
        backend.delete_secret(name)
        console.print(Panel(f"[green]✓[/green] [bold]{name}[/bold] deleted from {path}.", title="Success"))
    except CredentialBridgeError as e:
        err_console.print(Panel(f"[red]{e}[/red]", title="Error"))
        raise typer.Exit(1)


@app.command(name="list")
def list_secrets(
    path: str = typer.Option(".env", "--path", "-p"),
):
    """List all keys in the .env file."""
    backend = EnvFileBackend(path=path)
    try:
        keys = backend.list_secrets()
        table = Table(title=f"Keys in {path}")
        table.add_column("Key", style="cyan")
        for k in keys:
            table.add_row(k)
        console.print(table)
    except CredentialBridgeError as e:
        err_console.print(Panel(f"[red]{e}[/red]", title="Error"))
        raise typer.Exit(1)


def main():
    app()
