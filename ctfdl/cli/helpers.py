from pathlib import Path

import typer

from ctfdl.common.updates import check_updates
from ctfdl.common.version import show_version
from ctfdl.core.config import ExportConfig
from ctfdl.rendering.inspector import list_available_templates


def resolve_output_format(name: str) -> tuple[str, str, str]:
    output_format_map = {
        "json": ("json", "json", "flat"),
        "markdown": ("default", "grouped", "default"),
        "minimal": ("minimal", "grouped", "default"),
    }
    if name.lower() not in output_format_map:
        raise ValueError(f"Unknown output format: {name}")
    return output_format_map[name.lower()]


def build_export_config(args: dict) -> ExportConfig:
    return ExportConfig(
        url=args["url"],
        output=Path(args["output"]),
        token=args["token"],
        username=args["username"],
        password=args["password"],
        cookie=Path(args["cookie"]) if args["cookie"] else None,
        template_dir=Path(args["template_dir"]) if args["template_dir"] else None,
        variant_name=args["variant_name"],
        folder_template_name=args["folder_template_name"],
        index_template_name=args["index_template_name"],
        no_index=args["no_index"],
        categories=args["categories"],
        min_points=args["min_points"],
        max_points=args["max_points"],
        status=args["status"],
        update=args["update"],
        no_attachments=args["no_attachments"],
        parallel=args["parallel"],
        list_templates=args["list_templates"],
        zip_output=args["zip_output"],
        debug=args["debug"],
    )


def handle_version():
    show_version()
    raise typer.Exit()


def handle_check_update():
    check_updates()
    raise typer.Exit()


def handle_list_templates(template_dir):
    list_available_templates(
        Path(template_dir) if template_dir else Path(),
        Path(__file__).parent.parent / "templates",
    )
    raise typer.Exit()
