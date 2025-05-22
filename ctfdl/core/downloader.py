from pathlib import Path
import asyncio
import os
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from ctfdl.templating.engine import TemplateEngine
from ctfdl.core.client import get_authenticated_client
import ctfdl.utils.console as console


async def download_challenges(
    url,
    username,
    password,
    token,
    output_dir,
    template_dir=None,
    variant_name="default",
    folder_template_name="default",
    categories=None,
    min_points=None,
    max_points=None,
    update=False,
    no_attachments=False,
    solved=None,
    parallel=4,
):
    console.connecting(url)
    client = await get_authenticated_client(url, username, password, token)

    challenges = await client.challenges.get_all(
        categories=categories,
        min_points=min_points,
        max_points=max_points,
        solved=solved,
    )
    if not challenges:
        console.no_challenges_found()
        return False, []
    console.challenges_found(len(challenges))

    template_engine = TemplateEngine(
        user_template_dir=Path(template_dir) if template_dir else None,
        builtin_template_dir=Path(__file__).parent.parent / "templates",
    )

    out_dir = Path(output_dir)
    os.makedirs(out_dir, exist_ok=True)

    all_challenges_data = []

    async def process(chal):
        try:
            await process_challenge(
                client,
                chal,
                template_engine,
                variant_name,
                folder_template_name,
                out_dir,
                update,
                no_attachments,
                all_challenges_data,
            )
            console.downloaded_challenge(chal.name, chal.category)
        except Exception as e:
            console.failed_challenge(chal.name, str(e))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console.console,
    ) as progress:
        main_task = progress.add_task(
            "Downloading challenges...", total=len(challenges)
        )
        sem = asyncio.Semaphore(parallel)

        async def worker(chal):
            async with sem:
                await process(chal)
                progress.update(main_task, advance=1)

        await asyncio.gather(*(worker(chal) for chal in challenges))
        progress.remove_task(main_task)

    return True, all_challenges_data


async def process_challenge(
    client,
    chal,
    template_engine,
    variant_name,
    folder_template_name,
    output_dir: Path,
    update,
    no_attachments,
    all_challenges_data,
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
    if update and chal_folder.exists():
        return

    os.makedirs(chal_folder, exist_ok=True)
    template_engine.render_challenge(variant_name, challenge_data, chal_folder)

    if not no_attachments and chal.attachments:
        for att in chal.attachments:
            await client.attachments.download(att, str(chal_folder / "files"))

    all_challenges_data.append(
        {
            "name": chal.name,
            "category": chal.category,
            "value": chal.value,
            "solved": getattr(chal, "solved", False),
            "path": str(rel_path) + "/README.md",
        }
    )
