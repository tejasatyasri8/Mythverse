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
    print("========== CHAT REQUEST ==========")
    print(request)

    # ---------------------------------
    # Validate SINGLE mode
    # ---------------------------------

    if request.mode == "single":

        if not request.religion or not request.holy_book:
            raise HTTPException(
                status_code=400,
                detail="Please select religion and holy book"
            )

    # ---------------------------------
    # Validate COMPARE mode
    # ---------------------------------

    elif request.mode == "compare":

        if not request.first_religion or not request.first_book:
            raise HTTPException(
                status_code=400,
                detail="First scripture is missing"
            )

        if not request.second_religion or not request.second_book:
            raise HTTPException(
                status_code=400,
                detail="Second scripture is missing"
            )

    # ---------------------------------
    # Generate response
    # ---------------------------------

    ai_response = generate_response(
        db=db,
        session_id=request.session_id,
        user_message=request.message,
        mode=request.mode,

        religion=request.religion,
        holy_book=request.holy_book,

        first_religion=request.first_religion,
        first_book=request.first_book,

        second_religion=request.second_religion,
        second_book=request.second_book,

        history=request.history
    )

    answer = ai_response["answer"]
    sources = ai_response["sources"]

    # ---------------------------------
    # Save user message
    # ---------------------------------

    user_message = ChatHistory(
        session_id=request.session_id,
        role="user",
        content=request.message
    )

    # ---------------------------------
    # Save assistant message
    # ---------------------------------

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