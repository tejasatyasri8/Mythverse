from groq import Groq
from sqlalchemy.orm import Session

from app.config import GROQ_API_KEY, MODEL_NAME
from app.database.models import ChatHistory


client = Groq(api_key=GROQ_API_KEY)


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are MythVerse, an expert AI assistant specializing in world mythologies. "
        "You provide accurate, engaging, and respectful explanations about Hindu, Greek, "
        "Norse, Egyptian, Roman, Japanese, Chinese, and other mythologies. "
        "If a question is unrelated to mythology, answer it briefly and politely."
    )
}


def generate_response(
    db: Session,
    session_id: str,
    user_message: str
):

    try:
        history = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.id)
            .all()
        )

        messages = [SYSTEM_MESSAGE]

        for chat in history:
            messages.append(
                {
                    "role": chat.role,
                    "content": chat.content
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        print("LLM Error:", e)
        return "Sorry, I couldn't generate a response right now."