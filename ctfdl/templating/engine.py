from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader

from ctfdl.templating.inspector import (list_available_templates,
                                        validate_template_dir)
from ctfdl.templating.renderers import (ChallengeRenderer, FolderRenderer,
                                        IndexRenderer)
from ctfdl.templating.variant_loader import VariantLoader
from ctfdl.utils.slugify import slugify


class TemplateEngine:
    def __init__(self, user_template_dir: Path | None, builtin_template_dir: Path):
        self.user_template_dir = user_template_dir
        self.builtin_template_dir = builtin_template_dir

        loaders = []
        if user_template_dir:
            loaders.append(FileSystemLoader(str(user_template_dir)))
        loaders.append(FileSystemLoader(str(builtin_template_dir)))

        self.env = Environment(
            loader=ChoiceLoader(loaders), trim_blocks=True, lstrip_blocks=True
        )
        self.env.filters["slugify"] = slugify

        self.variant_loader = VariantLoader(user_template_dir, builtin_template_dir)
        self.challenge_renderer = ChallengeRenderer(self.env)
        self.folder_renderer = FolderRenderer(self.env)
        self.index_renderer = IndexRenderer(self.env)

    def render_challenge(self, variant_name: str, challenge: dict, output_dir: Path):
        variant = self.variant_loader.resolve_variant(variant_name)
        self.challenge_renderer.render(variant, challenge, output_dir)

    def render_path(self, template_name: str, challenge: dict) -> str:
        return self.folder_renderer.render(template_name, challenge)

    def render_index(self, template_name: str, challenges: list, output_path: Path):
        self.index_renderer.render(template_name, challenges, output_path)

    def validate(self) -> list:
        return validate_template_dir(
            self.user_template_dir or self.builtin_template_dir, self.env
        )

    def list_templates(self) -> None:
        list_available_templates(
            self.user_template_dir or Path("."), self.builtin_template_dir
        )
