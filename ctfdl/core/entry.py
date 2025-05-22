from ctfdl.core.downloader import download_challenges
from ctfdl.utils.zip_output import zip_output_folder
from ctfdl.templating.engine import TemplateEngine
from pathlib import Path
import tempfile

from ctfdl.models.config import ExportConfig
import logging
from rich.console import Console

console = Console()
logger = logging.getLogger("ctfdl.entry")


async def run_export(config: ExportConfig):
    if config.list_templates:
        from ctfdl.templating.inspector import list_available_templates

        list_available_templates(
            config.template_dir or Path("."), Path(__file__).parent.parent / "templates"
        )
        return

    solved_filter = True if config.solved else False if config.unsolved else None

    output_dir = (
        Path(tempfile.mkdtemp()) / "ctf-export" if config.zip_output else config.output
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    success, index_data = await download_challenges(
        url=config.url,
        username=config.username,
        password=config.password,
        token=config.token,
        output_dir=output_dir,
        template_dir=str(config.template_dir) if config.template_dir else None,
        variant_name=config.variant_name,
        folder_template_name=config.folder_template_name,
        categories=config.categories,
        min_points=config.min_points,
        max_points=config.max_points,
        solved=solved_filter,
        update=config.update,
        no_attachments=config.no_attachments,
        parallel=config.parallel,
    )

    if success:
        console.print("🎉 [bold green]All challenges downloaded successfully![/]")
        if not config.no_index:
            template_engine = TemplateEngine(
                user_template_dir=config.template_dir,
                builtin_template_dir=Path(__file__).parent.parent / "templates",
            )
            template_engine.render_index(
                template_name=config.index_template_name or "grouped",
                challenges=index_data,
                output_path=output_dir / "index.md",
            )

    if success and config.zip_output:
        zip_output_folder(output_dir)
