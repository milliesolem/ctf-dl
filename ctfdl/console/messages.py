from rich.console import Console
from .decorators import verbosity_required
from .config import output_config

console = Console()

@verbosity_required(level=1)
def print_info(msg: str):
    console.print(f"🔍 [cyan]{msg}[/]")
    output_config.log(f"[INFO] {msg}")

@verbosity_required(level=2)
def print_debug(msg: str):
    console.print(f"[dim]{msg}[/]")
    output_config.log(f"[DEBUG] {msg}")

@verbosity_required(level=0)
def print_error(msg: str):
    console.print(f"❌ [bold red]{msg}[/]")
    output_config.log(f"[ERROR] {msg}")

@verbosity_required(level=1)
def print_connecting(url: str):
    console.print(f"🔌 Connecting to [blue]{url}[/]...")

@verbosity_required(level=1)
def print_connected():
    console.print("✅ [green]Connected successfully[/]")

@verbosity_required(level=1)
def print_warning(msg: str):
    console.print(f"⚠️ [yellow]{msg}[/]")
    output_config.log(f"[WARN] {msg}")

@verbosity_required(level=2)
def print_downloaded_challenge(name: str, category: str):
    console.print(f"✅ Downloaded: [green]{name}[/] ([cyan]{category}[/])")

@verbosity_required(level=1)
def print_failed_challenge(name: str, reason: str):
    console.print(f"❌ [bold red]ERROR:[/] Failed [green]{name}[/]: {reason}")
    output_config.log(f"[FAIL] {name}: {reason}")
