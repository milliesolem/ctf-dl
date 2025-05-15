from pathlib import Path
import asyncio

from ctfbridge import create_client
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from ctfdl.folder_structure import FolderStructureRenderer
from ctfdl.template_writer import TemplateWriter
from ctfdl.utils import makedirs

console = Console(log_path=False, log_time=False)


async def download_challenges(
    url,
    username,
    password,
    token,
    output_dir,
    template_path=None,
    folder_template_path=None,
    categories=None,
    min_points=None,
    max_points=None,
    update=False,
    no_attachments=False,
    solved=None,
    parallel=4,
):
    console.print(f"Connecting to CTF platform: {url}")
    client = await create_client(url)
    if username and password:
        await client.auth.login(username=username, password=password)
    elif token:
        await client.auth.login(token=token)
    else:
        raise ValueError("Must provide either token or username/password to login.")

    console.print("Fetching challenges...")
    challenges = await client.challenges.get_all(
        categories=categories,
        min_points=min_points,
        max_points=max_points,
        solved=solved,
    )
    if not challenges:
        console.print("[bold red]There are no challenges to download...[/]")
        return False
    console.print(f"{len(challenges)} challenges to download.")

    writer = TemplateWriter(template_path)
    folder_renderer = FolderStructureRenderer(folder_template_path)
    out_dir = Path(output_dir)
    makedirs(out_dir)
    tasks = [
        (chal, writer, folder_renderer, out_dir, update, no_attachments)
        for chal in challenges
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        main_task = progress.add_task("Downloading challenges...", total=len(tasks))

        async def worker(
            chal,
            writer,
            folder_renderer,
            out_dir,
            update,
            no_attachments,
            progress,
            main_task,
        ):
            try:
                await process_challenge(
                    client,
                    chal,
                    writer,
                    folder_renderer,
                    out_dir,
                    update,
                    no_attachments,
                )
                progress.console.log(f"Downloaded challenge: {chal.name}")
            except Exception as e:
                progress.console.log(f"[bold red]ERROR:[/] Failed {chal.name}: {e}")
            finally:
                progress.update(main_task, advance=1)

        # Prepare list of tasks
        tasks_to_run = [
            worker(
                chal,
                writer,
                folder_renderer,
                out_dir,
                update,
                no_attachments,
                progress,
                main_task,
            )
            for chal, writer, folder_renderer, out_dir, update, no_attachments in tasks
        ]

        if parallel > 1:
            semaphore = asyncio.Semaphore(parallel)

            async def limited_worker(task_coro):
                async with semaphore:
                    await task_coro

            await asyncio.gather(*(limited_worker(t) for t in tasks_to_run))
        else:
            for t in tasks_to_run:
                await t

        progress.remove_task(main_task)
    return True


async def process_challenge(
    client, chal, writer, folder_renderer, output_dir: Path, update, no_attachments
):
    rel = folder_renderer.render(chal)
    chal_folder = output_dir / rel
    if update and chal_folder.exists():
        return
    makedirs(chal_folder)
    data = {
        "name": chal.name,
        "category": chal.category,
        "value": chal.value,
        "description": chal.description,
        "attachments": chal.attachments,
        "solved": getattr(chal, "solved", False),
    }
    writer.write(data, str(chal_folder))

    if not no_attachments and chal.attachments:
        for att in chal.attachments:
            await client.attachments.download(att, str((chal_folder / "files")))
