from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ExportConfig(BaseModel):
    url: str = Field(..., description="Base URL of the CTF platform")
    output: Path = Field(default=Path("challenges"), description="Output folder")

    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cookie: Optional[Path] = None

    template: Optional[Path] = None
    folder_template: Optional[Path] = None

    categories: Optional[List[str]] = None
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    solved: bool = False
    unsolved: bool = False

    update: bool = False
    no_attachments: bool = False
    parallel: int = 30
    list_templates: bool = False
    zip_output: bool = False
