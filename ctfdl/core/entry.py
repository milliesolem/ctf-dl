from ctfdl.core.downloader import download_challenges
from ctfdl.utils.zip_output import zip_output_folder
from ctfdl.rendering.template_loader import list_available_templates
from pathlib import Path
import tempfile

from ctfdl.models.config import ExportConfig
import logging
from rich.console import Console

console = Console()


logger = logging.getLogger("ctfdl.entry")


async def run_export(config: ExportConfig):
    if config.list_templates:
        list_available_templates()
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
        template_path=str(config.template) if config.template else None,
        folder_template_path=str(config.folder_template)
        if config.folder_template
        else None,
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
        from ctfdl.rendering.index_writer import IndexWriter
        IndexWriter().write(index_data, output_dir)

    if success and config.zip_output:
        zip_output_folder(output_dir)
