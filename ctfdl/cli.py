import socket
import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from ctfbridge.exceptions import UnknownPlatformError
from requests.exceptions import ConnectionError, SSLError, Timeout
from rich.console import Console

from ctfdl.downloader import download_challenges
from ctfdl.utils import list_available_templates

console = Console(log_path=False)
app = typer.Typer()


async def async_main(
    url: str,
    output: Path,
    token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    template: Optional[Path],
    folder_template: Optional[Path],
    categories: Optional[List[str]],
    min_points: Optional[int],
    max_points: Optional[int],
    solved: bool,
    unsolved: bool,
    update: bool,
    no_attachments: bool,
    parallel: int,
    list_templates: bool,
):
    """Download challenges from a CTF platform."""
    console.rule(f"[bold blue]CTF Download: {url}")

    # List templates
    if list_templates:
        list_available_templates()
        raise typer.Exit()

    # Credential enforcement
    if token and (username or password):
        console.print(
            "[red]Error:[/] Provide either token OR username/password, not both.",
            style="bold red",
        )
        raise typer.Exit(code=1)
    if not token and not (username and password):
        console.print(
            "[red]Error:[/] You must provide either a token OR both username and password.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    solved_filter = True if solved else False if unsolved else None

    try:
        success = await download_challenges(
            url=url,
            username=username,
            password=password,
            token=token,
            output_dir=str(output),
            template_path=str(template) if template else None,
            folder_template_path=str(folder_template) if folder_template else None,
            categories=categories,
            min_points=min_points,
            max_points=max_points,
            solved=solved_filter,
            update=update,
            no_attachments=no_attachments,
            parallel=parallel,
        )
        if success:
            console.print("[bold green]All challenges downloaded successfully![/]")
    except SSLError:
        console.print(
            "[bold red]SSL error. The server's certificate might be invalid or misconfigured.[/]"
        )
        raise typer.Exit(code=1)
    except ConnectionError as e:
        if isinstance(e.__cause__, socket.gaierror):
            console.print(
                "[bold red]Could not resolve the hostname. Please check the URL.[/]"
            )
        else:
            console.print(
                "[bold red]Failed to connect to the server. It might be down or unreachable.[/]"
            )
        raise typer.Exit(code=1)
    except Timeout:
        console.print(
            "[bold red]The request timed out. Try again later or check your connection.[/]"
        )
        raise typer.Exit(code=1)
    except UnknownPlatformError:
        console.print("[bold red]Platform not supported[/]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/] {e}")
        raise typer.Exit(code=1)


@app.command()
def main(
    url: str = typer.Argument(
        ..., help="Base URL of the CTF platform (e.g., https://demo.ctfd.io)"
    ),
    output: Path = typer.Option(
        Path("challenges"),
        "-o",
        "--output",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Output directory to save challenges",
    ),
    token: Optional[str] = typer.Option(
        None, "-t", "--token", hide_input=True, help="Authentication token"
    ),
    username: Optional[str] = typer.Option(
        None, "-u", "--username", help="Username for login"
    ),
    password: Optional[str] = typer.Option(
        None, "-p", "--password", hide_input=True, help="Password for login"
    ),
    template: Optional[Path] = typer.Option(
        None,
        "--template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to output template",
    ),
    folder_template: Optional[Path] = typer.Option(
        None,
        "--folder-template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to folder structure template",
    ),
    categories: Optional[List[str]] = typer.Option(
        None, "--categories", help="Only download specified categories"
    ),
    min_points: Optional[int] = typer.Option(
        None, "--min-points", help="Minimum points to download"
    ),
    max_points: Optional[int] = typer.Option(
        None, "--max-points", help="Maximum points to download"
    ),
    solved: bool = typer.Option(
        False, "--solved", help="Only download already solved challenges"
    ),
    unsolved: bool = typer.Option(
        False, "--unsolved", help="Only download unsolved challenges"
    ),
    update: bool = typer.Option(
        False, "--update", help="Skip challenges that already exist locally"
    ),
    no_attachments: bool = typer.Option(
        False, "--no-attachments", help="Skip downloading attachments"
    ),
    parallel: int = typer.Option(30, "--parallel", help="Number of parallel downloads"),
    list_templates: bool = typer.Option(
        False, "--list-templates", help="List available templates and exit"
    ),
):
    asyncio.run(
        async_main(
            url=url,
            output=output,
            token=token,
            username=username,
            password=password,
            template=template,
            folder_template=folder_template,
            categories=categories,
            min_points=min_points,
            max_points=max_points,
            solved=solved,
            unsolved=unsolved,
            update=update,
            no_attachments=no_attachments,
            parallel=parallel,
            list_templates=list_templates,
        )
    )


if __name__ == "__main__":
    app()
