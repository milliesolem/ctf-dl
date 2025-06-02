from rich.console import Console

# Default console used when none is passed explicitly
_default_console = Console(log_path=False, log_time=False)

# ===== Basic Notifications =====


def info(msg: str, console: Console = _default_console):
    console.print(f"🔍 [cyan]{msg}[/]")


def success(msg: str, console: Console = _default_console):
    console.print(f"✅ [green]{msg}[/]")


def warning(msg: str, console: Console = _default_console):
    console.print(f"⚠️ [yellow]{msg}[/]")


def error(msg: str, console: Console = _default_console):
    console.print(f"❌ [bold red]{msg}[/]")


def debug(msg: str, console: Console = _default_console):
    console.print(f"[dim]{msg}[/]")


# ===== Download Progress =====


def connecting(url: str, console: Console = _default_console):
    return console.status(
        f"[bold blue]️Connecting to CTF platform: [bold magenta]{url}[/]",
        spinner="dots",
    )


def connected(console: Console = _default_console):
    success("Connection established")


def connection_failed(error_message: str, console: Console = _default_console):
    error(f"Connection failed: {error_message}")


def no_challenges_found(console: Console = _default_console):
    error("There are no challenges to download...", console)


def challenges_found(count: int, console: Console = _default_console):
    console.print(f"📦 Found [bold]{count} challenges[/] to download:\n")


def downloaded_challenge(name: str, category: str, console: Console = _default_console):
    console.print(f"✅ Downloaded: [green]{name}[/] ([cyan]{category}[/])")


def failed_challenge(name: str, reason: str, console: Console = _default_console):
    console.print(f"❌ [bold red]ERROR:[/] Failed [green]{name}[/]: {reason}")


def download_complete(console: Console = _default_console):
    success("All challenges downloaded successfully!", console)


def zipped_output(path: str, console: Console = _default_console):
    console.print(f"🗂️ [green]Output saved to:[/] [bold underline]{path}[/]")


# ===== Version and Update =====


def version_output(version: str):
    console.print(f"📦 [bold]ctf-dl[/bold] version: [green]{version}[/green]")


def update_available(pkg: str, installed: str, latest: str):
    console.print(
        f"📦 [yellow]{pkg}[/]: update available → [red]{installed}[/] → [green]{latest}[/]"
    )


def up_to_date(pkg: str, version: str):
    console.print(f"✅ {pkg} is up to date ([green]{version}[/])")


def update_failed(pkg: str, reason: str):
    console.print(f"⚠️ Failed to fetch version for [yellow]{pkg}[/]: {reason}")


def not_installed(pkg: str):
    error(f"{pkg} is not installed.")


def upgrade_tip(cmd: str):
    console.print(f"\n🚀 To upgrade, run:\n[bold]{cmd}[/bold]")


# ===== Templates =====


def list_templates_header(name: str):
    console.print(f"\n📂 Available {name} Templates:")


def list_template_item(name: str):
    console.print(f"- {name}")


# ===== Context Manager =====


def spinner_status(message: str):
    return console.status(message, spinner="dots")
