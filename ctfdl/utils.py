import logging
import os
import re

logger = logging.getLogger("ctfdl")

def slugify(text):
    """
    Turn a string into a safe folder/file name.
    - Lowercase
    - Replace spaces with hyphens
    - Remove unsafe characters
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = text.strip("-")
    return text

def makedirs(path, dry_run=False):
    """
    Create directories safely, supporting dry-run mode.
    """
    if dry_run:
        logger.info("[Dry-Run] Would create directory: %s", path)
    else:
        os.makedirs(path, exist_ok=True)

def write_file(filepath, content, dry_run=False):
    """
    Write a file safely, supporting dry-run mode.
    """
    if dry_run:
        logger.info("[Dry-Run] Would write file: %s", filepath)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

def download_file(url, output_path, dry_run=False):
    """
    Download a file safely, supporting dry-run mode.
    """
    if dry_run:
        logger.info("[Dry-Run] Would download file from %s to %s", url, output_path)
    else:
        import requests
        r = requests.get(url)
        r.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(r.content)

def list_available_templates():
    """
    Print available templates (folder structure and challenge output).
    """
    base_template_dir = os.path.join(os.path.dirname(__file__), "templates")
    folder_template_dir = os.path.join(base_template_dir, "folder_structure")

    print("\nAvailable Folder Structure Templates:")
    if os.path.isdir(folder_template_dir):
        for fname in os.listdir(folder_template_dir):
            if fname.endswith(".jinja"):
                logical_name = fname[:-6]
                print(f"- {logical_name}")

    print("\nAvailable Challenge Templates:")
    if os.path.isdir(base_template_dir):
        for fname in os.listdir(base_template_dir):
            if fname.endswith(".jinja"):
                logical_name = fname[:-6]
                print(f"- {logical_name}")

    print()

def format_size(bytes_size):
    """
    Format a byte value into a human-readable format (e.g., KB, MB, GB).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f}PB"
