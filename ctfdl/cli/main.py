import asyncio
from pathlib import Path
from typing import List, Optional

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
        "token_normalize_func": lambda x: x,
    },
)

@app.command(name=None)
def cli(
    version: bool = typer.Option(
        False,
        "--version",
        is_eager=True,
        help="Show version and exit",
        rich_help_panel="Options",
    ),
    check_update: bool = typer.Option(
        False,
        "--check-update",
        is_eager=True,
        help="Check for updates",
        rich_help_panel="Options",
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging", rich_help_panel="Options"
    ),
    url: Optional[str] = typer.Argument(
        None, help="URL of the CTF platform", show_default=False
    ),
    # Output Options
    output: Optional[str] = typer.Option(
        "challenges",
        "--output",
        "-o",
        help="Output directory to save challenges",
        rich_help_panel="Output",
    ),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        help="Path to challenge output template (Jinja2)",
        rich_help_panel="Output",
    ),
    folder_template: Optional[str] = typer.Option(
        None,
        "--folder-template",
        help="Path to folder structure template (Jinja2)",
        rich_help_panel="Output",
    ),
    index_template: Optional[str] = typer.Option(None, "--index-template", help="Custom index template"),
    no_index: bool = typer.Option(False, "--no-index", help="Disable challenge index generation"),
    zip_output: bool = typer.Option(
        False,
        "--zip",
        help="Compress output folder after download",
        rich_help_panel="Output",
    ),
    # Authentication
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token",
        rich_help_panel="Authentication",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        help="Username for login",
        rich_help_panel="Authentication",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Password for login",
        rich_help_panel="Authentication",
    ),
    cookie: Optional[str] = typer.Option(
        None,
        "--cookie",
        "-c",
        help="Path to browser cookie/session file",
        rich_help_panel="Authentication",
    ),
    # Filters
    categories: Optional[List[str]] = typer.Option(
        None,
        "--categories",
        help="Only download specified categories",
        rich_help_panel="Filters",
    ),
    min_points: Optional[int] = typer.Option(
        None,
        "--min-points",
        help="Minimum points to download",
        rich_help_panel="Filters",
    ),
    max_points: Optional[int] = typer.Option(
        None,
        "--max-points",
        help="Maximum points to download",
        rich_help_panel="Filters",
    ),
    solved: bool = typer.Option(
        False,
        "--solved",
        help="Only download solved challenges",
        rich_help_panel="Filters",
    ),
    unsolved: bool = typer.Option(
        False,
        "--unsolved",
        help="Only download unsolved challenges",
        rich_help_panel="Filters",
    ),
    # Behavior
    update: bool = typer.Option(
        False,
        "--update",
        help="Skip challenges that already exist locally",
        rich_help_panel="Behavior",
    ),
    no_attachments: bool = typer.Option(
        False,
        "--no-attachments",
        help="Skip downloading attachments",
        rich_help_panel="Behavior",
    ),
    parallel: int = typer.Option(
        30,
        "--parallel",
        help="Number of parallel downloads",
        rich_help_panel="Behavior",
    ),
    list_templates: bool = typer.Option(
        False,
        "--list-templates",
        help="List available templates and exit",
        rich_help_panel="Behavior",
    ),
):
    if version:
        from ctfdl.utils.version import show_version

        show_version()
        raise typer.Exit()

    if check_update:
        from ctfdl.utils.check_update import check_updates

        check_updates()
        raise typer.Exit()

    if debug:
        from ctfdl.utils.logging_config import setup_logging

        setup_logging()
        console.print(
            "[bold yellow]Debug mode active[/]. Logs saved to [underline]ctfdl-debug.log[/]"
        )

    if url is None:
        raise typer.BadParameter("Missing required argument: URL")

    if list_templates:
        from ctfdl.templates import list_all_templates

        list_all_templates()
        raise typer.Exit()

    from ctfdl.models.config import ExportConfig
    from ctfdl.core.entry import run_export

    config = ExportConfig(
        url=url,
        output=Path(output),
        token=token,
        username=username,
        password=password,
        cookie=cookie,
        template=Path(template) if template else None,
        folder_template=Path(folder_template) if folder_template else None,
        categories=categories,
        min_points=min_points,
        max_points=max_points,
        solved=solved,
        unsolved=unsolved,
        update=update,
        no_attachments=no_attachments,
        parallel=parallel,
        list_templates=list_templates,
        zip_output=zip_output,
    )

    asyncio.run(run_export(config))


if __name__ == "__main__":
    app()
