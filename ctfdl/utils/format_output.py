from pathlib import Path

import mdformat


def format_output(text: str, output_file: str | Path, prettify: bool = False) -> str:
    if not prettify:
        return text

    ext = Path(output_file).suffix.lower()

    if ext == ".md":
        return mdformat.text(text, extensions={"tables"})

    return text
