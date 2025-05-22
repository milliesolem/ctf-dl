import os
import logging
from jinja2 import Environment, FileSystemLoader
from ctfdl.utils.slugify import slugify

logger = logging.getLogger("ctfdl.rendering.index_writer")


_DEFAULT_INDEX_TEMPLATE = os.path.join(
    os.path.dirname(__file__), "templates", "index", "index.md.jinja"
)


class IndexWriter:
    def __init__(self, template_path=None):
        if not template_path:
            logger.debug("Using default index template.")
            template_path = _DEFAULT_INDEX_TEMPLATE

        if not template_path.endswith(".jinja"):
            template_path += ".jinja"

        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Index template not found: {template_path}")

        base_path = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)

        self.env = Environment(loader=FileSystemLoader(base_path))
        self.env.filters["slugify"] = slugify
        self.template = self.env.get_template(template_name)

    def write(self, challenges, output_dir):
        challenges_sorted = sorted(challenges, key=lambda c: (c["category"].lower(), c["name"].lower()))
        rendered = self.template.render(challenges=challenges)
        output_path = os.path.join(output_dir, "index.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
