import logging
import os

from jinja2 import Environment, FileSystemLoader

from ctfdl.utils import slugify, write_file

logger = logging.getLogger("ctfdl.template_writer")

_DEFAULT_TEMPLATES_FOLDER = os.path.join(os.path.dirname(__file__), "templates")


class TemplateWriter:
    def __init__(self, template_path=None):
        """
        Initialize the template writer.
        """
        if template_path is None:
            logger.debug("No challenge template specified. Using default.")
            template_path = os.path.join(_DEFAULT_TEMPLATES_FOLDER, "default.md.jinja")

        if not template_path.endswith(".jinja"):
            template_path += ".jinja"

        if not os.path.isfile(template_path):
            guessed_path = os.path.join(_DEFAULT_TEMPLATES_FOLDER, template_path)
            if os.path.isfile(guessed_path):
                template_path = guessed_path
            else:
                logger.error("Template not found: %s", template_path)
                raise FileNotFoundError(f"Template {template_path} not found.")

        base_path = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)
        self.env = Environment(loader=FileSystemLoader(base_path))
        self.template = self.env.get_template(template_name)

        logger.debug("Loaded challenge template: %s", template_path)
        self.template_extension = os.path.splitext(template_name)[0].split(".")[-1]

        # Inject useful filters
        self.env.filters["slugify"] = slugify

    def write(self, challenge_data, output_folder):
        """
        Render the template and write the file to the given output folder.

        Args:
            challenge_data (dict): The challenge fields
            output_folder (str): Directory to save the output
        """
        rendered = self.template.render(challenge=challenge_data)

        output_filename = self._guess_output_filename()
        output_path = os.path.join(output_folder, output_filename)

        write_file(output_path, rendered)

    def _guess_output_filename(self):
        """
        Guess the output filename based on template extension.
        """
        if self.template_extension == "md":
            return "README.md"
        elif self.template_extension == "json":
            return "challenge.json"
        elif self.template_extension == "txt":
            return "challenge.txt"
        elif self.template_extension == "html":
            return "challenge.html"
        else:
            return "challenge_output.txt"
