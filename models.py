from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str
    character_name: str = "Alex"
    setting: str = "forest"
    tone: str = "dramatic"
    art_style: str = "comic book"

class TestImageRequest(BaseModel):
    prompt: str
    art_style: str = "comic book"
