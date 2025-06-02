import asyncio
import os
from pathlib import Path

import ctfdl.utils.console as console
from ctfdl.core.client import get_authenticated_client
from ctfdl.templating.context import TemplateEngineContext
from ctfdl.models.config import ExportConfig
from rich.console import Console as RichConsole
from ctfbridge.exceptions import (
    UnknownPlatformError,
    LoginError,
    MissingAuthMethodError,
)

progress_console = RichConsole()


async def download_challenges(config: ExportConfig) -> tuple[bool, list]:
    client = None
    try:
        with console.connecting(config.url):
            client = await get_authenticated_client(
                config.url, config.username, config.password, config.token
            )
        console.connected()
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

    challenges = await client.challenges.get_all(
        categories=config.categories,
        min_points=config.min_points,
        max_points=config.max_points,
        solved=True if config.solved else False if config.unsolved else None,
    )

    if not challenges:
        console.no_challenges_found()
        return False, []

    challenges.sort(key=lambda c: (c.category.lower(), c.name.lower()))

    console.challenges_found(len(challenges))

    template_engine = TemplateEngineContext.get()
    output_dir = config.output
    output_dir.mkdir(parents=True, exist_ok=True)

    all_challenges_data = []

    async def process(chal):
        try:
            await process_challenge(
                client=client,
                chal=chal,
                template_engine=template_engine,
                variant_name=config.variant_name,
                folder_template_name=config.folder_template_name,
                output_dir=output_dir,
                update=config.update,
                no_attachments=config.no_attachments,
                all_challenges_data=all_challenges_data,
            )
            console.downloaded_challenge(
                chal.name, chal.category, console=progress_console
            )
        except Exception as e:
            console.failed_challenge(chal.name, str(e), console=progress_console)

    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )

    from rich.console import Console as RichConsole

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=progress_console,
        disable=config.debug,
    ) as progress:
        main_task = progress.add_task(
            "Downloading challenges...", total=len(challenges)
        )
        sem = asyncio.Semaphore(config.parallel)

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
