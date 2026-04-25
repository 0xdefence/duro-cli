"""DURO CLI visual identity — green pixel-art banner, bordered panels, spinner.

Provides the shared Rich console, welcome box, status helpers, and an animated
spinner context manager used throughout the CLI and REPL.
"""

from __future__ import annotations

import itertools
import random
import threading
import time
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from duro import __version__

console = Console()

# ---------------------------------------------------------------------------
# Pixel-art banner — dense Unicode half-block DURO logo (green)
# ---------------------------------------------------------------------------

BANNER_LINES = [
    " ▗▄▄▄  ▗▖ ▗▖ ▗▄▄▖  ▗▄▖ ",
    " █▀  █ █  █  █▀▀▄ █  █ ",
    " █   █ █  █  █▀▀▘ █  █ ",
    " ▜▄▄▀  ▝▚▞▘ ▐▌    ▝▚▞▘ ",
]

# ---------------------------------------------------------------------------
# Spinner — pulsing star/asterisk sequence (Claude Code style)
# ---------------------------------------------------------------------------

_SPINNER_FRAMES = ["·", "✢", "✳", "✶", "✻", "✽"]
_SPINNER_CYCLE = _SPINNER_FRAMES + _SPINNER_FRAMES[-2:0:-1]  # bounce

_SPINNER_VERBS = [
    "Scanning",
    "Confirming",
    "Forging",
    "Hashing",
    "Validating",
    "Resolving",
    "Linking",
    "Checking",
    "Probing",
    "Analyzing",
]


class Spinner:
    """Animated terminal spinner with pulsing star frames."""

    def __init__(self, label: str = "") -> None:
        self._label = label or random.choice(_SPINNER_VERBS)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _run(self) -> None:
        frames = itertools.cycle(_SPINNER_CYCLE)
        while not self._stop.is_set():
            frame = next(frames)
            text = f"\r  [bold green]{frame}[/bold green] [dim]{self._label}…[/dim] "
            console.print(text, end="", highlight=False)
            time.sleep(0.12)
        # Clear the spinner line
        console.print("\r" + " " * (len(self._label) + 12) + "\r", end="")

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)


@contextmanager
def spinner(label: str = ""):
    """Context manager for an animated spinner during long operations."""
    s = Spinner(label)
    s.start()
    try:
        yield
    finally:
        s.stop()


# ---------------------------------------------------------------------------
# Welcome box
# ---------------------------------------------------------------------------


def show_welcome() -> None:
    """Print the bordered welcome box with pixel-art logo and hints."""
    banner = Text()
    for line in BANNER_LINES:
        banner.append(line + "\n", style="bold green")

    body = Text()
    body.append("\n")
    body.append_text(banner)
    body.append("  EXPLOITABILITY, PROVEN.\n\n", style="dim")
    body.append("  Type ", style="dim")
    body.append("duro chat", style="bold")
    body.append(" for interactive mode\n", style="dim")
    body.append("  Type ", style="dim")
    body.append("duro help", style="bold")
    body.append(" for commands\n", style="dim")

    console.print(
        Panel(
            body,
            title=f"[bold green]DURO CLI v{__version__}[/bold green]",
            title_align="left",
            border_style="green",
            padding=(0, 2),
        )
    )


# Keep old name as alias for backwards compat in case anything references it
show_banner = show_welcome

# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------


def ok(msg: str) -> None:
    """Green bullet success message."""
    console.print(f"[bold bright_green]●[/bold bright_green] {msg}")


def warn(msg: str) -> None:
    """Yellow bullet warning message."""
    console.print(f"[bold yellow]●[/bold yellow] {msg}")


def err(msg: str) -> None:
    """Red bullet error message."""
    console.print(f"[bold red]●[/bold red] {msg}")


def section(title: str) -> None:
    """Green-bordered section panel."""
    console.print(Panel.fit(f"[bold green]{title}[/bold green]", border_style="green"))


def bullet(msg: str) -> None:
    """Green bullet-prefixed output line."""
    console.print(f"[green]●[/green] {msg}")


def muted(msg: str) -> None:
    """Dim hint text."""
    console.print(f"[dim]{msg}[/dim]")
