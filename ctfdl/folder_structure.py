import logging
import os

from jinja2 import Environment, FileSystemLoader

from .utils import slugify

logger = logging.getLogger("ctfdl.folder_structure")

_DEFAULT_FOLDER_TEMPLATES_FOLDER = os.path.join(
    os.path.dirname(__file__), "templates", "folder_structure"
)


class FolderStructureRenderer:
    def __init__(self, template_path=None):
        if template_path is None:
            logger.debug("No folder structure template specified. Using default.")
            template_path = os.path.join(
                _DEFAULT_FOLDER_TEMPLATES_FOLDER, "default.path.jinja"
            )

        if not template_path.endswith(".jinja"):
            template_path += ".jinja"

        if not os.path.isfile(template_path):
            guessed_path = os.path.join(_DEFAULT_FOLDER_TEMPLATES_FOLDER, template_path)
            if os.path.isfile(guessed_path):
                template_path = guessed_path
            else:
                logger.error("Folder structure template not found: %s", template_path)
                raise FileNotFoundError(f"Template {template_path} not found.")

        base_path = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)

        self.env = Environment(loader=FileSystemLoader(base_path))
        self.env.filters["slugify"] = slugify

        self.template = self.env.get_template(template_name)

        logger.debug("Loaded folder structure template: %s", template_path)

    def render(self, challenge_data):
        context = {
            "challenge": {
                "name": challenge_data.name,
                "category": challenge_data.category,
                "value": challenge_data.value,
            }
        }
        result = self.template.render(context)
        return result.strip()
