from groq import Groq
from sqlalchemy.orm import Session

from app.config import GROQ_API_KEY, MODEL_NAME
from app.database.models import ChatHistory
from app.retriever.book_retriever import search_book

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are MythVerse, an AI scripture knowledge assistant that answers ONLY from the provided scripture context.\n\n"

        "Core Rules:\n"
        "1. Use only the supplied scripture context to answer.\n"
        "2. Do not use outside knowledge or add teachings that are not present in the context.\n"
        "3. If the provided context does not contain enough information, clearly say that the selected scripture does not provide enough information for this question.\n"
        "4. Never invent chapter numbers, verses, quotes, or references.\n\n"

        "Answer Style:\n"
        "5. Do not simply repeat the scripture text. Explain the deeper meaning in simple, clear language.\n"
        "6. Explain concepts in a way that a modern reader can understand.\n"
        "7. Include practical connections to everyday life when they are supported by the scripture meaning.\n"
        "8. Give a realistic modern-life example to make the teaching easier to understand.\n"
        "9. Keep the tone respectful, educational, calm, and beginner-friendly.\n\n"

        "Response Format:\n"
        "Structure answers using these sections whenever possible:\n\n"

        "📖 Meaning:\n"
        "Explain what the teaching means in simple words.\n\n"

        "💡 Explanation:\n"
        "Explain why this teaching is important and what lesson it provides.\n\n"

        "🌱 Modern Life Application:\n"
        "Explain how this principle can be applied in today's life.\n\n"

        "🌍 Example:\n"
        "Provide a relatable real-world example.\n\n"

        "📜 Scripture Reference:\n"
        "Mention the exact chapter and verse references used from the provided context.\n\n"

        "Safety:\n"
        "10. Do not use harsh, insulting, or offensive language, even if the user does.\n"
        "11. Do not criticize or compare religions negatively.\n"
        "12. End every answer with a short Key Takeaway summarizing the main lesson in one or two sentences.\n"
        "Explain the teaching clearly without adding unsupported interpretations. Use modern examples only to explain the meaning, not to introduce new teachings.\n"
        "13. If the user gives a short acknowledgement, gratitude, confirmation, or closing message (such as 'thanks', 'I understood', 'okay', 'got it'), respond briefly and conversationally instead of providing a full scripture explanation.\n"
        "Keep responses concise while maintaining explanation quality. Avoid unnecessary repetition.\n"
    ),
}


def generate_response(
    db: Session,
    session_id: str,
    user_message: str,
    religion: str,
    holy_book: str,
    history: list
):
    try:
        
        # Load chat history
        history = history[-2:]

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
                    "role": chat["role"],
                    "content": chat["content"]
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