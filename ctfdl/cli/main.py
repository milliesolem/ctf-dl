import asyncio
import getpass
import sys
from enum import Enum

import typer
from rich.console import Console

from ctfdl.cli.helpers import (
    build_export_config,
    handle_check_update,
    handle_list_templates,
    handle_version,
    resolve_output_format,
)


class ChallengeStatus(str, Enum):
    all = "all"
    solved = "solved"
    unsolved = "unsolved"


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
        False, "--debug", "-d", help="Enable debug logging", rich_help_panel="Options"
    ),
    url: str | None = typer.Argument(
        None,
        help="URL of the CTF instance (e.g., https://ctf.example.com)",
        show_default=False,
    ),
    output: str | None = typer.Option(
        "challenges",
        "--output",
        "-o",
        help="Output directory to save challenges",
        rich_help_panel="Output",
    ),
    zip_output: bool = typer.Option(
        False,
        "--zip",
        "-z",
        help="Compress output folder after download",
        rich_help_panel="Output",
    ),
    output_format: str | None = typer.Option(
        None,
        "--output-format",
        "-f",
        help="Preset output format (json, markdown, minimal)",
        rich_help_panel="Output",
    ),
    template_dir: str | None = typer.Option(
        None,
        "--template-dir",
        help="Directory containing custom templates",
        rich_help_panel="Templating",
    ),
    variant_name: str = typer.Option(
        "default",
        "--template",
        help="Challenge template variant to use",
        rich_help_panel="Templating",
    ),
    folder_template_name: str = typer.Option(
        "default",
        "--folder-template",
        help="Template for folder structure",
        rich_help_panel="Templating",
    ),
    index_template_name: str | None = typer.Option(
        "grouped",
        "--index-template",
        help="Template for challenge index",
        rich_help_panel="Templating",
    ),
    no_index: bool = typer.Option(
        False,
        "--no-index",
        help="Do not generate an index file",
        rich_help_panel="Templating",
    ),
    list_templates: bool = typer.Option(
        False,
        "--list-templates",
        help="List available templates and exit",
        rich_help_panel="Templating",
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token",
        rich_help_panel="Authentication",
    ),
    username: str | None = typer.Option(
        None,
        "--username",
        "-u",
        help="Login username",
        rich_help_panel="Authentication",
    ),
    password: str | None = typer.Option(
        None,
        "--password",
        "-p",
        help="Login password",
        rich_help_panel="Authentication",
    ),
    cookie: str | None = typer.Option(
        None,
        "--cookie",
        "-c",
        help="Path to cookie/session file",
        rich_help_panel="Authentication",
    ),
    categories: list[str] | None = typer.Option(
        None,
        "--categories",
        help="Only download specified categories",
        rich_help_panel="Filters",
    ),
    min_points: int | None = typer.Option(
        None, "--min-points", help="Minimum challenge points", rich_help_panel="Filters"
    ),
    max_points: int | None = typer.Option(
        None, "--max-points", help="Maximum challenge points", rich_help_panel="Filters"
    ),
    status: ChallengeStatus = typer.Option(
        ChallengeStatus.all,
        "--status",
        case_sensitive=False,
        help="Filter challenges by their completion status",
        rich_help_panel="Filters",
    ),
    update: bool = typer.Option(
        False,
        "--update",
        help="Update existing challenges instead of skipping them (overwrites existing files)",
        rich_help_panel="Behavior",
    ),
    no_attachments: bool = typer.Option(
        False,
        "--no-attachments",
        help="Do not download attachments",
        rich_help_panel="Behavior",
    ),
    parallel: int = typer.Option(
        10,
        "--parallel",
        help="Number of parallel downloads",
        rich_help_panel="Behavior",
    ),
):
    if version:
        handle_version()

    if check_update:
        handle_check_update()

    if list_templates:
        handle_list_templates(template_dir)

    if url is None:
        raise typer.BadParameter("Missing required argument: URL")

    if username and not password:
        if sys.stdin.isatty():
            password = getpass.getpass("Password: ")
        else:
            typer.secho("Error: password required but not provided", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    if output_format:
        try:
            variant_name, index_template_name, folder_template_name = resolve_output_format(
                output_format
            )
        except ValueError as e:
            raise typer.BadParameter(str(e))

    config = build_export_config(locals())

    from ctfdl.challenges.entry import run_export

    asyncio.run(run_export(config))


if __name__ == "__main__":
    app()
