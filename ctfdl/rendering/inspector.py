from pathlib import Path

import yaml
from jinja2 import Environment, TemplateNotFound
from rich.console import Console
from rich.table import Table

from ctfdl.rendering.metadata_loader import parse_template_metadata


def validate_template_dir(template_dir: Path, env: Environment) -> list[str]:
    errors = []
    variant_dir = template_dir / "challenge/variants"

    if not variant_dir.exists():
        return [f"Variant directory not found: {variant_dir}"]

    for file in variant_dir.glob("*.yaml"):
        try:
            data = yaml.safe_load(file.read_text(encoding="utf-8"))
            for comp in data.get("components", []):
                path = f"challenge/_components/{comp['template']}"
                try:
                    env.get_template(path)
                except TemplateNotFound:
                    errors.append(f"Missing component template: {path} (from {file.name})")
        except Exception as e:
            errors.append(f"Failed to parse {file.name}: {e}")

    return errors


def list_available_templates(user_template_dir: Path, builtin_template_dir: Path) -> None:
    console = Console()
    all_sources = [("User", user_template_dir), ("Built-in", builtin_template_dir)]

    def gather_variants(template_dir):
        entries = []
        for file in sorted((template_dir / "challenge/variants").glob("*.yaml")):
            name = file.stem
            description = ""
            try:
                data = yaml.safe_load(file.read_text(encoding="utf-8"))
                description = data.get("description", "")
            except Exception:
                description = "[red](invalid or unreadable)[/red]"
            entries.append((name, description))
        return entries

    def gather_templates(template_dir, subpath, suffix):
        files = []
        folder = template_dir / subpath
        if folder.exists():
            for f in sorted(folder.glob(f"*{suffix}")):
                name = f.name.replace(suffix, "")
                desc = parse_template_metadata(f).get("description", "No description")
                files.append((name, desc))
        return files

    printed = set()

    for label, source in all_sources:
        if not source.exists():
            continue

        # Check if there are any templates
        variants = gather_variants(source)
        folders = gather_templates(source, "folder_structure", ".jinja")
        indexes = gather_templates(source, "index", ".jinja")

        if not (variants or folders or indexes):
            continue

        console.rule(f"[bold blue]{label} Templates")

        if variants:
            table = Table(
                title="[not italic]Challenge Variants",
                title_justify="left",
                show_header=True,
                header_style="bold magenta",
                title_style="bold",
            )
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            for name, desc in variants:
                if ("variant", name) not in printed:
                    table.add_row(name, desc)
                    printed.add(("variant", name))
            console.print(table)

        if folders:
            table = Table(
                title="[not italic]Folder Structure Templates",
                title_justify="left",
                show_header=True,
                header_style="bold green",
                title_style="bold",
            )
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            for name, desc in folders:
                if ("folder", name) not in printed:
                    table.add_row(name, desc)
                    printed.add(("folder", name))
            console.print(table)

        if indexes:
            table = Table(
                title="[not italic]Index Templates",
                title_justify="left",
                show_header=True,
                header_style="bold yellow",
                title_style="bold",
            )
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            for name, desc in indexes:
                if ("index", name) not in printed:
                    table.add_row(name, desc)
                    printed.add(("index", name))
            console.print(table)
