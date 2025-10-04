import json
from pathlib import Path

import mdformat


def format_output(text: str, output_file: str | Path, prettify: bool = False) -> str:
    if not prettify:
        return text

    ext = Path(output_file).suffix.lower()

    if ext == ".md":
        return mdformat.text(text, extensions={"tables"})
    elif ext == ".json":
        try:
            obj = json.loads(text)
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            return text

    return text
