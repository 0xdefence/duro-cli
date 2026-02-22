from rich.console import Console
from rich.panel import Panel

console = Console()

BANNER = r"""
▗▄▄▄   ▗▖ ▗▖ ▗▄▄▖   ▗▄▖
▐▌  █  ▐▌ ▐▌ ▐▌ ▐▌ ▐▌ ▐▌
▐▌  █  ▐▌ ▐▌ ▐▛▀▚▖ ▐▌ ▐▌
▐▙▄▄▀   ▝▚▄▞▘▐▌ ▐▌  ▝▚▄▞▘
"""

def show_banner():
    console.print(BANNER, style="bold magenta")
    console.print("[bold]DURO CLI v0.1.0[/bold]\n[dim]EXPLOITABILITY, PROVEN.[/dim]\n")

def ok(msg: str):
    console.print(f"[green]OK[/green] {msg}")

def warn(msg: str):
    console.print(f"[yellow]WARN[/yellow] {msg}")

def err(msg: str):
    console.print(f"[red]ERROR[/red] {msg}")

def section(title: str):
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]"))
