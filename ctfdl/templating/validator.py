from pathlib import Path
from jinja2 import Environment, TemplateNotFound
import yaml


def validate_template_dir(template_dir: Path, env: Environment) -> list:
    errors = []
    variant_dir = template_dir / "challenge/variants"

    if not variant_dir.exists():
        return [f"Variant directory not found: {variant_dir}"]

    for file in variant_dir.glob("*.yaml"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for comp in data.get("components", []):
                    path = f"challenge/_components/{comp['template']}"
                    try:
                        env.get_template(path)
                    except TemplateNotFound:
                        errors.append(
                            f"Missing component template: {path} (from {file.name})"
                        )
        except Exception as e:
            errors.append(f"Failed to parse {file.name}: {e}")

    return errors
