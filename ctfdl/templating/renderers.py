from pathlib import Path

from jinja2 import Environment

from ctfdl.utils.format_output import format_output


class BaseRenderer:
    """Base renderer with shared formatting and file writing logic."""

    def _apply_formatting_and_write(
        self, rendered: str, output_path: Path, config: dict
    ):
        """Format rendered content and write to disk."""
        rendered = format_output(
            rendered,
            output_path,
            prettify=config.get("prettify", False),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")


class ChallengeRenderer(BaseRenderer):
    """Renders individual challenge."""

    def render(self, template, config: dict, challenge: dict, output_dir: Path):
        rendered = template.render(challenge=challenge)
        output_path = output_dir / config["output_file"]
        self._apply_formatting_and_write(rendered, output_path, config)


class FolderRenderer:
    """Renders the folder structure path for a challenge."""

    def __init__(self, env: Environment):
        self.env = env

    def render(self, template, challenge: dict) -> str:
        return template.render(challenge=challenge)


class IndexRenderer(BaseRenderer):
    """Renders the global challenge index."""

    def render(self, template, config: dict, challenges: list, output_path: Path):
        rendered = template.render(challenges=challenges)

        final_path = output_path.parent / config.get("output_file", output_path.name)

        self._apply_formatting_and_write(rendered, final_path, config)
