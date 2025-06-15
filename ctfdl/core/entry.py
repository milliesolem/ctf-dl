import logging
import tempfile
from pathlib import Path
from collections import Counter

from rich.console import Console
from rich.table import Table

from ctfdl.core.downloader import download_challenges
from ctfdl.models.config import ExportConfig
from ctfdl.templating.context import TemplateEngineContext
from ctfdl.templating.engine import TemplateEngine
from ctfdl.utils.logging_config import setup_logging_with_rich
from ctfdl.utils.zip_output import zip_output_folder

console = Console()
logger = logging.getLogger("ctfdl.entry")


async def run_export(config: ExportConfig):
    setup_logging_with_rich(debug=config.debug)

    TemplateEngineContext.initialize(
        config.template_dir, Path(__file__).parent.parent / "templates"
    )

    if config.list_templates:
        TemplateEngineContext.get().list_templates()
        return

    solved_filter = True if config.solved else False if config.unsolved else None

    temp_dir = Path(tempfile.mkdtemp()) if config.zip_output else None
    output_dir = (temp_dir / "ctf-export") if temp_dir else config.output
    config.output = output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    success, index_data = await download_challenges(config)

    if success:
        console.print(f"🎉 [bold green]{len(index_data)} challenges downloaded successfully![/bold green]")

        if not config.no_index:
            TemplateEngineContext.get().render_index(
                template_name=config.index_template_name or "grouped",
                challenges=index_data,
                output_path=output_dir / "index.md",
            )

        if config.zip_output:
            zip_output_folder(output_dir, archive_name="ctf-export")
