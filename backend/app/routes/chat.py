from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.chat_models import ChatRequest
from app.database.database import get_db
from app.database.models import ChatHistory
from app.services.llm import generate_response


router = APIRouter()


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    ai_response = generate_response(
        db,
        request.session_id,
        request.message
    )

    user_message = ChatHistory(
        session_id=request.session_id,
        role="user",
        content=request.message
    )

    assistant_message = ChatHistory(
        session_id=request.session_id,
        role="assistant",
        content=ai_response
    )

    db.add(user_message)
    db.add(assistant_message)

    db.commit()

    return {
        "reply": ai_response
    }