from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class ExportConfig(BaseModel):
    url: str = Field(..., description="Base URL of the CTF platform")
    output: Path = Field(default=Path("challenges"), description="Output folder")

    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cookie: Optional[Path] = None

    # Templating
    template_dir: Optional[Path] = None
    variant_name: str = "default"
    folder_template_name: str = "default"
    index_template_name: Optional[str] = "grouped"
    no_index: bool = False

    # Filters
    categories: Optional[List[str]] = None
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    solved: bool = False
    unsolved: bool = False

    # Behavior
    no_attachments: bool = False
    parallel: int = 30
    list_templates: bool = False
    zip_output: bool = False
    debug: bool = False
