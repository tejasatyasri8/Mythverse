from fastapi import APIRouter, Depends, HTTPException
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

    if not request.religion or not request.holy_book:
        raise HTTPException(
            status_code=400,
            detail="Please select religion and holy book"
        )


    ai_response = generate_response(
        db,
        request.session_id,
        request.message,
        request.religion,
        request.holy_book
    )


    answer = ai_response["answer"]
    sources = ai_response["sources"]


    user_message = ChatHistory(
        session_id=request.session_id,
        role="user",
        content=request.message
    )


    assistant_message = ChatHistory(
        session_id=request.session_id,
        role="assistant",
        content=answer
    )


    db.add(user_message)
    db.add(assistant_message)

    db.commit()


    return {
        "reply": answer,
        "sources": sources
    }