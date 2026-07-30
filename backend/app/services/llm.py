from groq import Groq
from sqlalchemy.orm import Session

from app.config import GROQ_API_KEY, MODEL_NAME
from app.database.models import ChatHistory
from app.retriever.book_retriever import search_book

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are MythVerse, an AI assistant that answers ONLY from the provided scripture context.\n\n"
        "Rules:\n"
        "1. Use only the supplied scripture context.\n"
        "2. Do not use outside knowledge.\n"
        "3. If the context is insufficient, clearly say that the selected scripture "
        "does not provide enough information.\n"
        "4. Explain the teaching in simple modern language and make sure of impactnes.\n"
        "5. Always include the chapter and verse references you used.\n"
        "6. donot use harsh or offensive language, even if the user does.\n"
    ),
}


def generate_response(
    db: Session,
    session_id: str,
    user_message: str,
    religion: str,
    holy_book: str,
):
    try:

        # Load chat history
        history = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.id)
            .all()
        )

        # Retrieve relevant scripture
        verses = search_book(
            query=user_message,
            religion=religion,
            book=holy_book,
            top_k=3
        )


        if not verses:
            return {
                "answer": "I couldn't find relevant teachings in the selected scripture.",
                "sources": []
            }


        context = ""

        for verse in verses:

            context += (
                f"Religion: {verse['metadata']['religion']}\n"
                f"Book: {verse['metadata']['book']}\n"
                f"Chapter: {verse['metadata']['chapter']}\n"
                f"Verse: {verse['metadata']['verse']}\n\n"
                f"{verse['text']}\n\n"
                "--------------------\n\n"
            )

        # Start messages
        messages = [SYSTEM_MESSAGE]

        # Add previous conversation
        for chat in history:
            messages.append(
                {
                    "role": chat.role,
                    "content": chat.content
                } # type: ignore
            )

        # Add current question with retrieved context
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Religion: {religion}\n"
                    f"Holy Book: {holy_book}\n\n"
                    f"Scripture Context:\n"
                    f"{context}\n"
                    f"Question:\n"
                    f"{user_message}"
                )
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages, # type: ignore
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": verses
        }

    except Exception as e:
        print("LLM Error:", e)
        return {
            "answer": "Sorry, I couldn't generate a response right now.",
            "sources": []
        }