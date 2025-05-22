from pathlib import Path
from jinja2 import Environment, TemplateNotFound


class ChallengeRenderer:
    def __init__(self, env: Environment):
        self.env = env

    def render(self, variant: dict, challenge: dict, output_dir: Path):
        for comp in variant["components"]:
            template_name = f"challenge/_components/{comp['template']}"
            try:
                template = self.env.get_template(template_name)
            except TemplateNotFound:
                raise FileNotFoundError(f"Template '{template_name}' not found.")

            rendered = template.render(challenge=challenge)
            output_path = output_dir / comp["file"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(rendered)


class FolderRenderer:
    def __init__(self, env: Environment):
        self.env = env

    def render(self, template_name: str, challenge: dict) -> str:
        path_template_file = f"folder_structure/{template_name}.jinja"
        try:
            template = self.env.get_template(path_template_file)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Folder structure template '{path_template_file}' not found."
            )

        return template.render(challenge=challenge)


class IndexRenderer:
    def __init__(self, env: Environment):
        self.env = env

    def render(self, template_name: str, challenges: list, output_path: Path):
        index_template_file = f"index/{template_name}.jinja"
        try:
            template = self.env.get_template(index_template_file)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Index template '{index_template_file}' not found."
            )

        rendered = template.render(challenges=challenges)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
