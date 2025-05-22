import os
import logging
from jinja2 import Environment, FileSystemLoader
from ctfdl.utils.slugify import slugify

logger = logging.getLogger("ctfdl.rendering.template_writer")

_DEFAULT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "templates", "default.md.jinja"
)

_OUTPUT_NAMES = {
    "md": "README.md",
    "json": "challenge.json",
    "txt": "challenge.txt",
    "html": "challenge.html",
}


class TemplateWriter:
    def __init__(self, template_path=None):
        if not template_path:
            logger.debug("Using default challenge template.")
            template_path = _DEFAULT_TEMPLATE_PATH

        if not template_path.endswith(".jinja"):
            template_path += ".jinja"

        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Challenge template not found: {template_path}")

        base_path = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)

        self.env = Environment(loader=FileSystemLoader(base_path))
        self.env.filters["slugify"] = slugify
        self.template = self.env.get_template(template_name)
        self.template_extension = os.path.splitext(template_name)[0].split(".")[-1]

    def write(self, challenge_data, output_folder):
        rendered = self.template.render(challenge=challenge_data)
        output_filename = _OUTPUT_NAMES.get(
            self.template_extension, "challenge_output.txt"
        )
        output_path = os.path.join(output_folder, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
