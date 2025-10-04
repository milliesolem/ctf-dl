from pathlib import Path

from ctfbridge.models.challenge import Challenge as CTFBridgeChallenge
from jinja2 import Environment

from ctfdl.common.format_output import format_output
from ctfdl.core.models import ChallengeEntry


class BaseRenderer:
    """Base renderer with shared formatting and file writing logic."""

    def _apply_formatting_and_write(self, rendered: str, output_path: Path, config: dict):
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

    def render(self, template, config: dict, challenge: CTFBridgeChallenge, output_dir: Path):
        rendered = template.render(challenge=challenge.model_dump())
        output_path = output_dir / config["output_file"]
        self._apply_formatting_and_write(rendered, output_path, config)


class FolderRenderer:
    """Renders the folder structure path for a challenge."""

    def __init__(self, env: Environment):
        self.env = env

    def render(self, template, challenge: CTFBridgeChallenge) -> str:
        return template.render(challenge=challenge.model_dump())


class IndexRenderer(BaseRenderer):
    """Renders the global challenge index."""

    def render(self, template, config: dict, challenges: list[ChallengeEntry], output_path: Path):
        rendered = template.render(challenges=[challenge.model_dump() for challenge in challenges])

        final_path = output_path.parent / config.get("output_file", output_path.name)

        self._apply_formatting_and_write(rendered, final_path, config)
