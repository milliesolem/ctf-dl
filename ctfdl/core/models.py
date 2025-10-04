from pathlib import Path

from ctfbridge.models.challenge import Challenge
from pydantic import BaseModel, Field


class ChallengeEntry(BaseModel):
    data: Challenge = Field(..., description="The CTFBridge Challenge object")
    path: Path = Field(..., description="Path to the challenge's directory")
    updated: bool = Field(default=False, description="If the challenge was updated instead of new")
