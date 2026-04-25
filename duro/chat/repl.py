"""Interactive REPL loop for duro chat.

Rich-based prompt with session tracking, ambiguity handling,
and graceful error recovery.  Green-themed Claude Code-style visuals.
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from duro import __version__
from duro.ui import BANNER_LINES, spinner

from .parser import Intent
from .registry import dispatch
from .session import SessionContext, resolve

console = Console()


def _format_result(result: dict) -> str:
    """Format handler result for display."""
    output = result.get("output")
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        if output and isinstance(output[0], dict):
            lines = []
            for entry in output:
                lines.append("  ".join(f"{k}={v}" for k, v in entry.items()))
            return "\n".join(lines)
        return "\n".join(str(x) for x in output)
    if isinstance(output, dict):
        return json.dumps(output, indent=2)
    return str(output)


def _format_help(result: dict) -> None:
    """Render help output with green bullets and aligned columns."""
    commands = result.get("commands")
    if not commands:
        # Fallback to plain output
        text = _format_result(result)
        if text:
            console.print(text)
        return

    console.print()
    console.print("[bold green]Available commands[/bold green] [dim](type naturally or use exact names)[/dim]")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2), show_edge=False)
    table.add_column(style="bold", no_wrap=True)
    table.add_column(style="dim")

    for cmd, desc in commands:
        table.add_row(f"[green]●[/green] {cmd}", desc)

    console.print(table)

    footer = result.get("footer")
    if footer:
        console.print()
        for line in footer:
            console.print(f"  [dim]{line}[/dim]")
    console.print()


def _prompt_text(session: SessionContext) -> str:
    """Build prompt string showing current provider."""
    provider = session.last_provider
    if provider and provider != "mock":
        return f"duro ({provider}) > "
    return "duro > "


def _show_repl_welcome(session: SessionContext) -> None:
    """Print the REPL welcome box with logo and tips."""
    # Build left column: banner + status
    left = Text()
    for line in BANNER_LINES:
        left.append(line + "\n", style="bold green")
    left.append("\n")
    left.append("  Welcome back.\n", style="bold")
    provider = session.last_provider or "mock"
    left.append(f"  Provider: {provider}\n", style="dim")

    # Build right column: tips
    tips = (
        "\n"
        "  [bold]Tips:[/bold]\n"
        "  [green]●[/green] Type naturally or use exact commands\n"
        "  [green]●[/green] [bold]help[/bold] for all commands\n"
        "  [green]●[/green] [bold]quit[/bold] to exit\n"
    )

    console.print(
        Panel(
            left,
            title=f"[bold green]DURO Interactive Shell v{__version__}[/bold green]",
            title_align="left",
            subtitle="[dim]" + tips + "[/dim]",
            subtitle_align="right",
            border_style="green",
            padding=(0, 2),
        )
    )


def launch_repl() -> None:
    """Launch the interactive NLP-driven REPL."""
    session = SessionContext()

    _show_repl_welcome(session)

    while True:
        try:
            prompt = _prompt_text(session)
            # Print green ">" in prompt via Rich, read input plainly
            console.print(f"\n[green]{prompt[:-2]}[/green]", end="")
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not raw.strip():
            continue

        # Parse with session-aware follow-up resolution
        result = resolve(raw, session)

        # Quit
        if result.intent == Intent.QUIT:
            console.print("[dim]Goodbye.[/dim]")
            break

        # Unknown
        if result.intent == Intent.UNKNOWN:
            console.print(f"[bold red]●[/bold red] Could not understand: {raw}")
            console.print("[dim]Type 'help' for available commands.[/dim]")
            session.update_after_command(result.intent, raw)
            continue

        # Ambiguity — low confidence with alternatives
        if result.confidence < 0.70 and result.alternatives:
            console.print(f"[bold yellow]●[/bold yellow] Not sure — did you mean:")
            console.print(f"    [bold]{result.intent.name}[/bold] [dim]({result.confidence:.0%})[/dim]")
            for alt, score in result.alternatives[:3]:
                console.print(f"    {alt.name} [dim]({score:.0%})[/dim]")
            console.print("[dim]Re-phrase or type the exact command.[/dim]")
            session.update_after_command(result.intent, raw)
            continue

        # Dispatch with spinner
        try:
            with spinner():
                handler_result = dispatch(result.intent, result.params)
        except ValueError as e:
            console.print(f"[bold red]●[/bold red] {e}")
            session.update_after_command(result.intent, raw)
            continue
        except SystemExit:
            session.update_after_command(result.intent, raw)
            continue
        except Exception as e:
            console.print(f"[bold red]●[/bold red] Unexpected error: {e}")
            session.update_after_command(result.intent, raw)
            continue

        # Handle SET_PROVIDER action
        if handler_result.get("action") == "set_provider":
            new_provider = handler_result["provider"]
            session.last_provider = new_provider
            console.print(f"[bold bright_green]●[/bold bright_green] Provider set to: {new_provider}")
            session.update_after_command(result.intent, raw)
            continue

        # Help — use structured formatter if available
        if result.intent == Intent.HELP and "commands" in handler_result:
            _format_help(handler_result)
            session.update_after_command(result.intent, raw)
            continue

        # Display result
        formatted = _format_result(handler_result)
        if formatted:
            label = handler_result.get("label", "")
            if label:
                console.print(f"[bold green]●[/bold green] [dim][{label}][/dim]")
            console.print(f"[green]●[/green] {formatted}")

        # Update session context
        session.update_after_command(result.intent, raw)

        # Capture run_id if the handler produced one
        if "run_id" in handler_result:
            session.update_after_run(
                run_id=handler_result["run_id"],
                scenario_path=result.params.get("scenario_path"),
                provider=result.params.get("provider"),
            )
