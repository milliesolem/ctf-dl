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


def makedirs(path):
    """
    Create directories
    """
    os.makedirs(path, exist_ok=True)


def write_file(filepath, content):
    """
    Write a file
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


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
