from importlib.metadata import version

def show_version():
    from rich.console import Console
    try:
        __version__ = version("ctf-dl")
    except Exception:
        __version__ = "dev"

    Console().print(f"📦 [bold]ctf-dl[/bold] version: [green]{__version__}[/green]")

