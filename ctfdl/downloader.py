import logging
import concurrent.futures
import os
from urllib.parse import unquote, urlparse

from ctfdl.utils import makedirs, download_file
from ctfdl.folder_structure import FolderStructureRenderer
from ctfdl.template_writer import TemplateWriter
from ctfdl.filters import apply_filters
from ctfbridge import get_client

logger = logging.getLogger("ctfdl.downloader")

def download_challenges(
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
    dry_run=False,
    no_attachments=False,
    parallel=4
):
    # Connect to CTF
    logger.info("Connecting to CTF platform: %s", url)
    client = get_client(url)

    if username and password:
        client.login(username=username, password=password)
    elif token:
        client.login(token=token)
    else:
        raise ValueError("Must provide either token or username/password to login.")

    # Fetch challenges
    challenges = client.get_challenges()
    logger.info("Fetched %d challenges from platform.", len(challenges))

    # Apply filters if any
    filtered_challenges = apply_filters(
        challenges,
        categories=categories,
        min_points=min_points,
        max_points=max_points
    )

    logger.info("%d challenges after applying filters.", len(filtered_challenges))

    # Prepare template writer
    writer = TemplateWriter(template_path)

    # Prepare folder structure renderer
    folder_renderer = FolderStructureRenderer(folder_template_path)

    # Prepare output directory
    makedirs(output_dir, dry_run=dry_run)

    # Prepare challenge download tasks
    tasks = []
    for chal in filtered_challenges:
        tasks.append((chal, writer, folder_renderer, output_dir, update, dry_run, no_attachments))

    # Parallel or sequential download
    if parallel > 1:
        logger.info("Downloading challenges with %d parallel workers.", parallel)
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = [executor.submit(process_challenge, *task) for task in tasks]
            concurrent.futures.wait(futures)
    else:
        logger.info("Downloading challenges sequentially.")
        for task in tasks:
            process_challenge(*task)

def process_challenge(chal, writer, folder_renderer, output_dir, update, dry_run, no_attachments):
    # Build folder path
    chal_folder_rel = folder_renderer.render(chal)
    chal_folder = os.path.join(output_dir, chal_folder_rel)

    # If update mode and challenge already exists, skip
    if update and os.path.exists(chal_folder):
        logger.info("Skipping existing challenge folder: %s", chal_folder_rel)
        return

    makedirs(chal_folder, dry_run=dry_run)

    # Prepare attachments metadata
    attachments = []
    if hasattr(chal, "attachments") and chal.attachments:
        for attachment_url in chal.attachments:
            attachment_name = unquote(urlparse(attachment_url).path.split("/")[-1])
            attachments.append({
                "filename": attachment_name,
                "path": attachment_name,
                "url": attachment_url
            })

    # Write README or challenge file
    challenge_data = {
        "name": chal.name,
        "category": chal.category,
        "value": chal.value,
        "description": chal.description,
        "attachments": attachments,
        "solved": getattr(chal, "solved", False)
    }

    writer.write(challenge_data, chal_folder, dry_run=dry_run)

    # Download attachments
    if not no_attachments:
        attachments_dir = os.path.join(chal_folder, "files")
        makedirs(attachments_dir, dry_run=dry_run)

        for attachment in attachments:
            file_path = os.path.join(attachments_dir, attachment["filename"])
            download_file(attachment["url"], file_path, dry_run=dry_run)
