import re
from pathlib import Path

import yaml


def parse_template_metadata(template_path: Path) -> dict:
    metadata = {}
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read(1024)  # Read first 1KB (or so) for metadata

        # Match a Jinja comment block at the very start
        m = re.match(r"^\s*\{#(.*?)#\}", content, re.DOTALL)
        if m:
            comment_text = m.group(1).strip()
            # Parse the comment text as YAML
            metadata = yaml.safe_load(comment_text) or {}
    except Exception as e:
        pass

    return metadata
