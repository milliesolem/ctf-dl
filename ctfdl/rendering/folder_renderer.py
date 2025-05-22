import os
import logging
from jinja2 import Environment, FileSystemLoader
from ctfdl.utils.slugify import slugify

logger = logging.getLogger("ctfdl.rendering.folder_renderer")

_DEFAULT_FOLDER_TEMPLATE = os.path.join(
    os.path.dirname(__file__), "templates", "folder_structure", "default.path.jinja"
)


class FolderStructureRenderer:
    def __init__(self, template_path=None):
        if not template_path:
            logger.debug("Using default folder structure template.")
            template_path = _DEFAULT_FOLDER_TEMPLATE

        if not template_path.endswith(".jinja"):
            template_path += ".jinja"

        if not os.path.isfile(template_path):
            raise FileNotFoundError(
                f"Folder structure template not found: {template_path}"
            )

        base_path = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)

        self.env = Environment(loader=FileSystemLoader(base_path))
        self.env.filters["slugify"] = slugify
        self.template = self.env.get_template(template_name)

    def render(self, challenge):
        context = {
            "challenge": {
                "name": challenge.name,
                "category": challenge.category,
                "value": challenge.value,
            }
        }
        return self.template.render(context).strip()
