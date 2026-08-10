from pydantic import BaseModel, Field
from typing import Literal


class ChatRequest(BaseModel):
    session_id: str
    message: str

    mode: Literal["single", "compare"] = "single"

    # Single scripture
    religion: str | None = None
    holy_book: str | None = None

    # Compare scriptures
    first_religion: str | None = None
    first_book: str | None = None

    second_religion: str | None = None
    second_book: str | None = None

    history: list = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    sources: list = []