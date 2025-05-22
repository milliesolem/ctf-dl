import shutil
from pathlib import Path

from rich.console import Console

console = Console()


def zip_output_folder(output_dir: Path):
    archive_path = shutil.make_archive(output_dir.stem, "zip", root_dir=output_dir)
    console.print(f"🗂️ [green]Output saved to:[/] [bold underline]{archive_path}[/]")
    shutil.rmtree(output_dir)
