import logging
import tempfile
from pathlib import Path

from rich.console import Console

from ctfdl.challenges.downloader import download_challenges
from ctfdl.common.archiver import zip_output_folder
from ctfdl.common.logging import setup_logging_with_rich
from ctfdl.core.config import ExportConfig
from ctfdl.core.events import EventEmitter
from ctfdl.rendering.context import TemplateEngineContext
from ctfdl.ui.rich_handler import RichConsoleHandler

console = Console()
logger = logging.getLogger("ctfdl.entry")


async def run_export(config: ExportConfig):
    setup_logging_with_rich(debug=config.debug)

    TemplateEngineContext.initialize(
        config.template_dir, Path(__file__).parent.parent / "resources" / "templates"
    )

    if config.list_templates:
        TemplateEngineContext.get().list_templates()
        return

    emitter = EventEmitter()

    RichConsoleHandler(emitter)

    temp_dir = Path(tempfile.mkdtemp()) if config.zip_output else None
    output_dir = (temp_dir / "ctf-export") if temp_dir else config.output
    config.output = output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        success, index_data = await download_challenges(config, emitter)
    except Exception as e:
        await emitter.emit("download_fail", str(e))
        raise SystemExit(1)

    if success:
        await emitter.emit("download_success")

        if not config.no_index:
            TemplateEngineContext.get().render_index(
                template_name=config.index_template_name or "grouped",
                challenges=index_data,
                output_path=output_dir / "index.md",
            )

        if config.zip_output:
            zip_output_folder(output_dir, archive_name="ctf-export")
