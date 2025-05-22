import socket
import asyncio
from pathlib import Path
from typing import List, Optional
import shutil

import typer
from rich.console import Console

console = Console(log_path=False)
app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "allow_extra_args": False,
        "ignore_unknown_options": False,
        "token_normalize_func": lambda x: x
    }
)


def check_credentials(token, username, password, cookie):
    # Allow any combination except both token and username/password
    if token and (username or password):
        console.print(
            "[red]Error:[/] Provide either token OR username/password, not both.",
            style="bold red",
        )
        raise typer.Exit(code=1)
    # Credentials are optional, so we don't error if none are provided


async def async_main(
    url: str,
    output: Path,
    token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    cookie: Optional[Path],
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
    zip_output: bool,
):
    console.rule(f"[bold blue]CTF Download: {url}")

    # Lazy imports for faster CLI startup
    from requests.exceptions import ConnectionError, SSLError, Timeout
    from ctfbridge.exceptions import UnknownPlatformError
    from ctfdl.downloader import download_challenges

    if list_templates:
        from ctfdl.utils.templates import list_available_templates
        list_available_templates()
        raise typer.Exit()

    check_credentials(token, username, password, cookie)

    solved_filter = True if solved else False if unsolved else None

    success = await download_challenges(
        url=url,
        username=username,
        password=password,
        token=token,
        # cookie_path=str(cookie) if cookie else None,
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
        if zip_output:
            archive_path = shutil.make_archive(output.stem, "zip", root_dir=output)
            console.print(f"🗂️ [green]Output saved to:[/] [bold underline]{archive_path}[/]")
            shutil.rmtree(output)
        console.print("🎉 [bold green]All challenges downloaded successfully![/]")

@app.command(name=None)
def cli(
    version: bool = typer.Option(False, "--version", is_eager=True, help="Show version and exit"),
    check_update: bool = typer.Option(False, "--check-update", is_eager=True, help="Check for updates"),
    url: Optional[str] = typer.Argument(None, help="URL of the CTF platform"),

    # Output options
    output: Optional[str] = typer.Option("challenges", "--output", "-o", help="Output directory to save challenges"),
    template: Optional[str] = typer.Option(None, "--template", help="Path to output template"),
    folder_template: Optional[str] = typer.Option(None, "--folder-template", help="Path to folder structure template"),
    zip_output: bool = typer.Option(False, "--zip", help="Compress output folder after download"),

    # Authentication
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Authentication token"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Username for login"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Password for login"),
    cookie: Optional[str] = typer.Option(None, "--cookie", help="Path to browser cookie/session file"),

    # Filters
    categories: Optional[List[str]] = typer.Option(None, "--categories", help="Only download specified categories"),
    min_points: Optional[int] = typer.Option(None, "--min-points", help="Minimum points to download"),
    max_points: Optional[int] = typer.Option(None, "--max-points", help="Maximum points to download"),
    solved: bool = typer.Option(False, "--solved", help="Only download solved challenges"),
    unsolved: bool = typer.Option(False, "--unsolved", help="Only download unsolved challenges"),

    # Behavior
    update: bool = typer.Option(False, "--update", help="Skip challenges that already exist locally"),
    no_attachments: bool = typer.Option(False, "--no-attachments", help="Skip downloading attachments"),
    parallel: int = typer.Option(30, "--parallel", help="Number of parallel downloads"),
    list_templates: bool = typer.Option(False, "--list-templates", help="List available templates and exit"),
):
    if version:
        from ctfdl.utils.version import show_version
        show_version()
        raise typer.Exit()

    if check_update:
        from ctfdl.utils.check_update import check_updates
        check_updates()
        raise typer.Exit()

    if url is None:
        raise typer.BadParameter("Missing required argument: URL")

    if list_templates:
        from ctfdl.templates import list_all_templates
        list_all_templates()
        raise typer.Exit()

    if url is None:
        ctx.fail("Missing required argument: URL")

    asyncio.run(
        async_main(
            url=url,
            output=output,
            template=template,
            folder_template=folder_template,
            zip_output=zip_output,
            token=token,
            username=username,
            password=password,
            cookie=cookie,
            categories=categories,
            min_points=min_points,
            max_points=max_points,
            solved=solved,
            unsolved=unsolved,
            update=update,
            no_attachments=no_attachments,
            parallel=parallel,
            list_templates=list_templates
        )
    )

if __name__ == "__main__":
    app()
