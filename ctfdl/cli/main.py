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

output_format_map = {
    "json": {
        "variant_name": "json",
        "index_template_name": "json",
        "folder_template_name": "flat",
    },
    "markdown": {
        "variant_name": "default",
        "index_template_name": "grouped",
        "folder_template_name": "default",
    },
    "minimal": {
        "variant_name": "minimal",
        "index_template_name": "grouped",
        "folder_template_name": "default",
    },
}


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
    zip_output: bool = typer.Option(
        False,
        "--zip",
        help="Compress output folder after download",
        rich_help_panel="Output",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--output-format",
        help="Preset output format that selects a challenge template variant (e.g., json, markdown)",
        rich_help_panel="Output",
    ),
    # Templating
    template_dir: Optional[str] = typer.Option(
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
        help="Template used for folder structure",
        rich_help_panel="Templating",
    ),
    index_template_name: Optional[str] = typer.Option(
        "grouped",
        "--index-template",
        help="Template used to render challenge index file",
        rich_help_panel="Templating",
    ),
    no_index: bool = typer.Option(
        False,
        "--no-index",
        help="Do not generate a challenge index file",
        rich_help_panel="Templating",
    ),
    list_templates: bool = typer.Option(
        False,
        "--list-templates",
        help="List available templates and exit",
        rich_help_panel="Templating",
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

    if list_templates:
        from ctfdl.templating.inspector import list_available_templates

        list_available_templates(
            Path(template_dir) if template_dir else Path("."),
            Path(__file__).parent.parent / "templates",
        )
        raise typer.Exit()

    if url is None:
        raise typer.BadParameter("Missing required argument: URL")

    if output_format:
        format_settings = output_format_map.get(output_format.lower())
        if not format_settings:
            raise typer.BadParameter(f"Unknown output format: {output_format}")

        variant_name = format_settings["variant_name"]
        index_template_name = format_settings["index_template_name"]
        folder_template_name = format_settings["folder_template_name"]
    else:
        variant_name = variant_name
        index_template_name = index_template_name
        folder_template_name = folder_template_name

    from ctfdl.models.config import ExportConfig
    from ctfdl.core.entry import run_export

    config = ExportConfig(
        url=url,
        output=Path(output),
        token=token,
        username=username,
        password=password,
        cookie=Path(cookie) if cookie else None,
        template_dir=Path(template_dir) if template_dir else None,
        variant_name=variant_name,
        folder_template_name=folder_template_name,
        index_template_name=index_template_name,
        no_index=no_index,
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
