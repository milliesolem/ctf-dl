import re


def slugify(text):
    """
    Turn a string into a safe folder/file name.
    - Lowercase
    - Replace spaces with hyphens
    - Remove unsafe characters
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = text.strip("-")
    return text
