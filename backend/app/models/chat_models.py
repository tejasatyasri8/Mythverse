from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    religion: str
    holy_book: str
    message: str
    history: list = []

class ChatResponse(BaseModel):
    reply: str