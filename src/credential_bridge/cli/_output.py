# src/credential_bridge/cli/_output.py
"""Shared Rich output helpers — imported by all CLI modules."""
import json
import sys
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# On Windows the default console codepage is often cp1252 which cannot encode
# many Unicode characters (✓, ✗, box-drawing lines used by Rich panels).
# Reconfigure stdout/stderr to UTF-8 so Rich renders correctly.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except AttributeError:
        pass  # reconfigure not available in some environments (e.g. redirected streams)

console = Console()
err_console = Console(stderr=True)


def print_success(message: str) -> None:
    """Print a green success panel."""
    console.print(
        Panel(f"[green]✓[/green]  {message}", border_style="green", padding=(0, 1))
    )


def print_error(message: str, title: str = "Error") -> None:
    """Print a red error panel to stderr."""
    err_console.print(
        Panel(f"[red]✗[/red]  {message}", title=f"[red bold]{title}[/red bold]",
              border_style="red", padding=(0, 1))
    )


def print_result(data: Dict[str, Any], title: str = "") -> None:
    """Print a JSON result in a cyan panel with syntax highlighting."""
    syntax = Syntax(json.dumps(data, indent=2), "json", theme="monokai")
    console.print(
        Panel(syntax,
              title=f"[bold cyan]{title}[/bold cyan]" if title else "",
              border_style="cyan", padding=(0, 1))
    )


def print_table(rows: List[str], title: str = "", column: str = "Key") -> None:
    """Print a list of strings as a Rich table."""
    table = Table(title=title, border_style="cyan", show_header=True,
                  header_style="bold cyan")
    table.add_column(column, style="cyan")
    for row in rows:
        table.add_row(row)
    console.print(table)
