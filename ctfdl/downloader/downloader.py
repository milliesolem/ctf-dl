import asyncio
from collections.abc import Callable
from pathlib import Path

from ctfbridge.exceptions import (
    LoginError,
    MissingAuthMethodError,
    NotAuthenticatedError,
    UnknownPlatformError,
)
from ctfbridge.models.challenge import Challenge, ProgressData

from ctfdl.downloader.client import get_authenticated_client
from ctfdl.events import EventEmitter
from ctfdl.models.config import ExportConfig
from ctfdl.templating.context import TemplateEngineContext
from ctfdl.templating.engine import TemplateEngine


async def download_challenges(
    config: ExportConfig, emitter: EventEmitter
) -> tuple[bool, list]:
    client = None
    try:
        await emitter.emit("connect_start", url=config.url)
        client = await get_authenticated_client(
            config.url, config.username, config.password, config.token
        )
        await emitter.emit("connect_success")
    except UnknownPlatformError:
        await emitter.emit("connect_fail", reason="Platform is not supported")
        return False, []
    except LoginError:
        await emitter.emit("connect_fail", reason="Invalid credentials or token")
        return False, []
    except MissingAuthMethodError:
        await emitter.emit("connect_fail", reason="Invalid authentication type")
        return False, []

    challenges_iterator = client.challenges.iter_all(
        categories=config.categories,
        min_points=config.min_points,
        max_points=config.max_points,
        solved=True if config.solved else False if config.unsolved else None,
        detailed=True,
        enrich=True,
    )

    template_engine = TemplateEngineContext.get()
    output_dir = config.output
    output_dir.mkdir(parents=True, exist_ok=True)
    all_challenges_data = []

    sem = asyncio.Semaphore(config.parallel)
    tasks = []
    challenge_count = 0

    async def process(chal: Challenge):
        try:
            await emitter.emit("challenge_start", challenge=chal)

            async def attachment_progress_callback(pd: ProgressData):
                await emitter.emit(
                    "attachment_progress", progress_data=pd, challenge=chal
                )

            await process_challenge(
                client=client,
                emitter=emitter,
                chal=chal,
                template_engine=template_engine,
                variant_name=config.variant_name,
                folder_template_name=config.folder_template_name,
                output_dir=output_dir,
                no_attachments=config.no_attachments,
                update=config.update,
                all_challenges_data=all_challenges_data,
                progress_callback=attachment_progress_callback,
                attachment_concurrency=config.parallel,
            )
            await emitter.emit("challenge_success", challenge=chal)
        except Exception as e:
            await emitter.emit("challenge_fail", challenge=chal, reason=str(e))
        finally:
            await emitter.emit("challenge_complete", challenge=chal)

    async def worker(chal: Challenge):
        async with sem:
            await process(chal)

    await emitter.emit("download_start")

    try:
        async for chal in challenges_iterator:
            challenge_count += 1
            task = asyncio.create_task(worker(chal))
            tasks.append(task)
    except NotAuthenticatedError:
        await emitter.emit("connect_fail", reason="Authentication required")
        return False, []

    if challenge_count == 0:
        await emitter.emit("no_challenges_found")
        await emitter.emit("download_complete")
        return False, []

    await asyncio.gather(*tasks)

    await emitter.emit("download_complete")
    return True, all_challenges_data


async def process_challenge(
    client,
    emitter: EventEmitter,
    chal: Challenge,
    template_engine: TemplateEngine,
    variant_name: str,
    folder_template_name: str,
    output_dir: Path,
    no_attachments: bool,
    update: bool,
    all_challenges_data: list,
    progress_callback: Callable,
    attachment_concurrency: int,
):
    challenge_data = {
        "name": chal.name,
        "category": chal.category,
        "value": chal.value,
        "description": chal.description,
        "attachments": chal.attachments,
        "services": chal.services,
        "solved": getattr(chal, "solved", False),
    }
    rel_path_str = template_engine.render_path(folder_template_name, challenge_data)
    chal_folder = output_dir / rel_path_str

    existed_before = chal_folder.exists()

    if existed_before and not update:
        await emitter.emit("challenge_skipped", challenge=chal)
        return

    chal_folder.mkdir(parents=True, exist_ok=True)
    template_engine.render_challenge(variant_name, challenge_data, chal_folder)
    if not no_attachments and chal.attachments:
        files_dir = chal_folder / "files"
        files_dir.mkdir(exist_ok=True)
        await client.attachments.download_all(
            attachments=chal.attachments,
            save_dir=str(files_dir),
            progress=progress_callback,
            concurrency=attachment_concurrency,
        )

    await emitter.emit("challenge_downloaded", challenge=chal, updated=existed_before)

    all_challenges_data.append(
        {
            "name": chal.name,
            "category": chal.category,
            "value": chal.value,
            "solved": getattr(chal, "solved", False),
            "path": str(Path(rel_path_str) / "README.md"),
        }
    )
