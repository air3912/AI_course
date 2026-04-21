from typing import Literal

from pydantic import BaseModel


class ParseRequest(BaseModel):
    file_path: str
    file_type: Literal["pdf", "ppt", "pptx"]


class ParseResponse(BaseModel):
    file_path: str
    file_type: str
    extracted_text_preview: str
    text_length: int
