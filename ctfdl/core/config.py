from pathlib import Path

from pydantic import BaseModel, Field


class ExportConfig(BaseModel):
    url: str = Field(..., description="Base URL of the CTF platform")
    output: Path = Field(default=Path("challenges"), description="Output folder")

    token: str | None = None
    username: str | None = None
    password: str | None = None
    cookie: Path | None = None

    # Templating
    template_dir: Path | None = None
    variant_name: str = "default"
    folder_template_name: str = "default"
    index_template_name: str | None = "grouped"
    no_index: bool = False

    # Filters
    categories: list[str] | None = None
    min_points: int | None = None
    max_points: int | None = None
    solved: bool = False
    unsolved: bool = False
    # status...

    # Behavior
    update: bool = False
    no_attachments: bool = False
    parallel: int = 30
    list_templates: bool = False
    zip_output: bool = False
    debug: bool = False
