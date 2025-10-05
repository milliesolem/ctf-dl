import logging
import re
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def parse_template_metadata(template_path: Path) -> dict:
    metadata = {}
    try:
        content = template_path.read_text(encoding="utf-8")

        # Match a Jinja comment block at the very start
        m = re.match(r"^\s*\{#(.*?)#\}", content, re.DOTALL)
        if m:
            comment_text = m.group(1).strip()
            metadata = yaml.safe_load(comment_text) or {}
    except Exception as e:
        logger.exception(f"Failed to parse metadata from {template_path}: {e}")

    return metadata
