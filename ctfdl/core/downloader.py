import asyncio
import os
from pathlib import Path
from typing import Callable

import ctfdl.utils.console as console
from ctfbridge.exceptions import (LoginError, MissingAuthMethodError,
                                  UnknownPlatformError)
from ctfbridge.models.challenge import ProgressData
from ctfdl.core.client import get_authenticated_client
from ctfdl.models.config import ExportConfig
from ctfdl.templating.context import TemplateEngineContext
from rich.console import Console as RichConsole
from rich.live import Live
from rich.progress_bar import ProgressBar
from rich.text import Text
from rich.table import Table
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                           TimeElapsedColumn)
from rich.tree import Tree

progress_console = RichConsole()


def create_text_progress_bar(percentage: float, width: int = 20) -> str:
    """Helper to create a simple text-based progress bar."""
    filled_width = int(percentage / 100 * width)
    return f"[[bold green]{'█' * filled_width}[/][dim]{'─' * (width - filled_width)}[/]] {percentage:.0f}%"


async def download_challenges(config: ExportConfig) -> tuple[bool, list]:
    client = None
    try:
        with console.connecting(config.url):
            client = await get_authenticated_client(
                config.url, config.username, config.password, config.token
            )
    except UnknownPlatformError:
        console.connection_failed("Platform is unsupported or could not be identified.")
    except LoginError:
        if config.username and config.password:
            console.connection_failed("Invalid credentials")
        elif config.token:
            console.connection_failed("Invalid token")
    except MissingAuthMethodError:
        console.connection_failed("Invalid authentication type")

    if not client:
        return False, []

    challenges_iterator = client.challenges.iter_all(
        categories=config.categories,
        min_points=config.min_points,
        max_points=config.max_points,
        solved=True if config.solved else False if config.unsolved else None,
        detailed=True,
        enrich=True,
    )

    overall_progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Downloading Challenges..."),
        TextColumn("[green]({task.completed} downloaded)"),
        TimeElapsedColumn(),
        console=progress_console,
    )
    main_task = overall_progress.add_task("Challenges", total=None)
    
    root = Tree(overall_progress)

    template_engine = TemplateEngineContext.get()
    output_dir = config.output
    output_dir.mkdir(parents=True, exist_ok=True)
    all_challenges_data = []

    category_nodes = {}
    tree_lock = asyncio.Lock()

    with Live(root, console=progress_console, refresh_per_second=10, transient=True) as live:

        async def process(chal):
            parent_node = None
            challenge_node = None
            try:
                async with tree_lock:
                    if chal.category not in category_nodes:
                        node = root.add(f"📁 [bold cyan]{chal.category}[/bold cyan]")
                        category_nodes[chal.category] = {"node": node, "count": 0}
                    
                    category_info = category_nodes[chal.category]
                    parent_node = category_info["node"]
                    category_info["count"] += 1
                    
                    challenge_node = parent_node.add(f"📂 [bold]{chal.name}[/bold]")

                active_attachments = {}

                async def attachment_progress_callback(pd: ProgressData):
                    async with tree_lock:
                        node = active_attachments.get(pd.attachment.url)

                        progress_bar = ProgressBar(
                            total=pd.total_bytes,
                            completed=pd.downloaded_bytes,
                            width=30,
                        )

                        grid = Table.grid(expand=False)
                        grid.add_column(no_wrap=True)
                        grid.add_column(width=30)
                        grid.add_column(justify="left")

                        grid.add_row(
                            f"📄 {pd.attachment.name} ",
                            progress_bar,
                            f" [yellow]{pd.percentage:.2f}%[/yellow]"
                        )
                        
                        if node is None:
                            node = challenge_node.add(grid)
                            active_attachments[pd.attachment.url] = node
                        else:
                            node.label = grid

                        if pd.downloaded_bytes == pd.total_bytes and challenge_node and node in challenge_node.children:
                            challenge_node.children.remove(node)

                await process_challenge(
                    client=client,
                    chal=chal,
                    template_engine=template_engine,
                    variant_name=config.variant_name,
                    folder_template_name=config.folder_template_name,
                    output_dir=output_dir,
                    no_attachments=config.no_attachments,
                    all_challenges_data=all_challenges_data,
                    progress_callback=attachment_progress_callback,
                    attachment_concurrency=config.parallel,
                )
            except Exception as e:
                console.failed_challenge(chal.name, str(e), console=progress_console)
            finally:
                async with tree_lock:
                    if challenge_node and parent_node:
                        parent_node.children.remove(challenge_node)
                    
                    if chal.category in category_nodes:
                        category_info = category_nodes[chal.category]
                        category_info["count"] -= 1
                        if category_info["count"] == 0:
                            root.children.remove(category_info["node"])
                            del category_nodes[chal.category]
                    
                    overall_progress.update(main_task, advance=1)

        sem = asyncio.Semaphore(config.parallel)
        tasks = []
        async for chal in challenges_iterator:
            async def worker(c):
                async with sem:
                    await process(c)
            tasks.append(asyncio.create_task(worker(chal)))

        if not tasks:
            console.no_challenges_found()
            return False, []

        await asyncio.gather(*tasks)

    return True, all_challenges_data

async def process_challenge(
    client,
    chal,
    template_engine,
    variant_name,
    folder_template_name,
    output_dir: Path,
    no_attachments,
    all_challenges_data,
    progress_callback: Callable,
    attachment_concurrency: int,
):
    challenge_data = {
        "name": chal.name,
        "category": chal.category,
        "value": chal.value,
        "description": chal.description,
        "attachments": chal.attachments,
        "solved": getattr(chal, "solved", False),
    }

    rel_path = template_engine.render_path(folder_template_name, challenge_data)
    chal_folder = output_dir / rel_path

    os.makedirs(chal_folder, exist_ok=True)
    template_engine.render_challenge(variant_name, challenge_data, chal_folder)

    if not no_attachments and chal.attachments:
        await client.attachments.download_all(
            attachments=chal.attachments,
            save_dir=str(chal_folder / "files"),
            progress=progress_callback,
            concurrency=attachment_concurrency,
        )

    all_challenges_data.append(
        {
            "name": chal.name,
            "category": chal.category,
            "value": chal.value,
            "solved": getattr(chal, "solved", False),
            "path": str(rel_path) + "/README.md",
        }
    )
