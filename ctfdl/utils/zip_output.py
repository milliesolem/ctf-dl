import shutil
from pathlib import Path

from rich.console import Console

console = Console()

def zip_output_folder(output_dir: Path, archive_name="ctf-export"):
    parent_dir = output_dir.parent
    archive_path = shutil.make_archive(archive_name, "zip", root_dir=parent_dir, base_dir=output_dir.name)
    console.print(f"🗂️ [green]Output saved to:[/] [bold underline]{archive_path}[/]")
    shutil.rmtree(parent_dir)

