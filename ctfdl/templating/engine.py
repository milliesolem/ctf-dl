from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, TemplateNotFound
from slugify import slugify

from ctfdl.templating.inspector import list_available_templates, validate_template_dir
from ctfdl.templating.metadata_loader import parse_template_metadata
from ctfdl.templating.renderers import ChallengeRenderer, FolderRenderer, IndexRenderer
from ctfdl.templating.variant_loader import VariantLoader


class TemplateEngine:
    def __init__(
        self,
        user_template_dir: Path | None,
        builtin_template_dir: Path,
    ):
        self.user_template_dir = user_template_dir
        self.builtin_template_dir = builtin_template_dir

        loaders = []
        if user_template_dir:
            loaders.append(FileSystemLoader(str(user_template_dir)))
        loaders.append(FileSystemLoader(str(builtin_template_dir)))

        self.env = Environment(
            loader=ChoiceLoader(loaders),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        self.env.filters["slugify"] = slugify

        self.variant_loader = VariantLoader(user_template_dir, builtin_template_dir)
        self.challenge_renderer = ChallengeRenderer()
        self.folder_renderer = FolderRenderer(self.env)
        self.index_renderer = IndexRenderer()

    def _load_with_metadata(self, template_file: str) -> tuple:
        try:
            template = self.env.get_template(template_file)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_file}' not found.")

        source, filename, _ = self.env.loader.get_source(self.env, template_file)
        metadata = parse_template_metadata(Path(filename))

        return template, metadata

    def render_challenge(self, variant_name: str, challenge: dict, output_dir: Path):
        variant = self.variant_loader.resolve_variant(variant_name)
        for comp in variant["components"]:
            template_file = f"challenge/_components/{comp['template']}"
            template, config = self._load_with_metadata(template_file)
            config["output_file"] = comp["file"]
            self.challenge_renderer.render(template, config, challenge, output_dir)

    def render_path(self, template_name: str, challenge: dict) -> str:
        template_file = f"folder_structure/{template_name}.jinja"
        template, _ = self._load_with_metadata(template_file)
        return self.folder_renderer.render(template, challenge)

    def render_index(self, template_name: str, challenges: list, output_path: Path):
        template_file = f"index/{template_name}.jinja"
        template, config = self._load_with_metadata(template_file)
        self.index_renderer.render(template, config, challenges, output_path)

    def validate(self) -> list:
        return validate_template_dir(
            self.user_template_dir or self.builtin_template_dir, self.env
        )

    def list_templates(self) -> None:
        list_available_templates(
            self.user_template_dir or Path(), self.builtin_template_dir
        )
