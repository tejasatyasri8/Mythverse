from groq import Groq
from sqlalchemy.orm import Session

from app.config import GROQ_API_KEY, MODEL_NAME
from app.database.models import ChatHistory
from app.retriever.book_retriever import search_book

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are MythVerse, an AI scripture knowledge assistant that "
        "answers ONLY from the provided scripture context.\n\n"

        "Core Rules:\n"
        "1. Use only the supplied scripture context to answer.\n"
        "2. Do not use outside knowledge or add teachings that are not present "
        "in the context.\n"
        "3. If the provided context does not contain enough information, "
        "clearly say that the selected scripture does not provide enough "
        "information for this question.\n"
        "4. Never invent chapter numbers, verses, quotes, or references.\n\n"

        "Answer Style:\n"
        "5. Do not simply repeat scripture text. Explain the meaning in "
        "simple, clear language.\n"
        "6. Explain concepts in a way that a modern reader can understand.\n"
        "7. Include practical connections to everyday life when supported "
        "by the scripture meaning.\n"
        "8. Give a realistic modern-life example when appropriate.\n"
        "9. Keep the tone respectful, educational, calm, and beginner-friendly.\n\n"

        "Comparison Rules:\n"
        "10. When comparing two scriptures, clearly distinguish which teaching "
        "comes from which scripture.\n"
        "11. Identify similarities only when they are supported by the "
        "provided contexts.\n"
        "12. Identify differences only when they are supported by the "
        "provided contexts.\n"
        "13. Never claim that one religion or scripture is superior to another.\n"
        "14. Do not use outside religious knowledge to fill missing information.\n"
        "15. If one scripture does not contain enough information, clearly "
        "state that instead of guessing.\n\n"

        "Response Format for Single Scripture:\n"
        "📖 Meaning:\n"
        "Explain what the teaching means in simple words.\n\n"

        "💡 Explanation:\n"
        "Explain why this teaching is important.\n\n"

        "🌱 Modern Life Application:\n"
        "Explain how the principle can be applied today.\n\n"

        "🌍 Example:\n"
        "Provide a relatable real-world example.\n\n"

        "📜 Scripture Reference:\n"
        "Mention the exact chapter and verse references used.\n\n"

        "For comparisons, prefer:\n"
        "📖 Scripture 1:\n"
        "Explain the teaching found in the first scripture.\n\n"

        "📖 Scripture 2:\n"
        "Explain the teaching found in the second scripture.\n\n"

        "🔎 Similarities:\n"
        "Explain supported similarities.\n\n"

        "⚖️ Differences:\n"
        "Explain supported differences.\n\n"

        "🌱 Modern Life Application:\n"
        "Explain the practical lesson supported by both contexts.\n\n"

        "📜 Scripture References:\n"
        "Mention the exact references used from both scriptures.\n\n"

        "Safety:\n"
        "16. Do not use harsh, insulting, or offensive language.\n"
        "17. Do not criticize or compare religions negatively.\n"
        "18. End every answer with a short Key Takeaway summarizing the "
        "main lesson in one or two sentences.\n"
        "19. Use modern examples only to explain the supplied teachings, "
        "not to introduce new teachings.\n"
        "20. If the user gives a short acknowledgement, gratitude, "
        "confirmation, or closing message such as 'thanks', 'okay', "
        "or 'got it', respond briefly and conversationally.\n"
        "21. Keep responses concise while maintaining explanation quality.\n"
        "22. Avoid unnecessary repetition.\n"
    )
}


def build_context(verses):
    context = ""

    for verse in verses:
        metadata = verse["metadata"]

        context += (
            f"Religion: {metadata['religion']}\n"
            f"Book: {metadata['book']}\n"
            f"Chapter: {metadata['chapter']}\n"
            f"Verse: {metadata['verse']}\n\n"
            f"{verse['text']}\n\n"
            "--------------------\n\n"
        )

    return context


def generate_response(
    db: Session,
    session_id: str,
    user_message: str,
    mode: str,

    religion: str | None = None,
    holy_book: str | None = None,

    first_religion: str | None = None,
    first_book: str | None = None,

    second_religion: str | None = None,
    second_book: str | None = None,

    history: list | None = None
):
    try:

        history = history or []
        history = history[-6:]

        # =================================
        # SINGLE MODE
        # =================================

        if mode == "single":

            # Make sure values exist before calling search_book
            if not religion or not holy_book:
                return {
                    "answer": "Please select a religion and holy book.",
                    "sources": []
                }

            verses = search_book(
                query=user_message,
                religion=religion,
                book=holy_book,
                top_k=3
            )

            if not verses:
                return {
                    "answer": (
                        "I couldn't find relevant teachings in "
                        "the selected scripture."
                    ),
                    "sources": []
                }

            context = build_context(verses)

            # Explicitly use a generic list so Pylance
            # doesn't infer the wrong message type
            messages: list = [SYSTEM_MESSAGE]

            for chat in history:
                messages.append(
                    {
                        "role": chat["role"],
                        "content": chat["content"]
                    }
                )

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
                messages=messages
            )

            return {
                "answer": response.choices[0].message.content,
                "sources": verses
            }

        # =================================
        # COMPARE MODE
        # =================================

        if mode == "compare":

            # Make sure all four values exist
            if (
                not first_religion
                or not first_book
                or not second_religion
                or not second_book
            ):
                return {
                    "answer": (
                        "Please select both scriptures before "
                        "starting the comparison."
                    ),
                    "sources": []
                }

            # -----------------------------
            # FIRST SCRIPTURE
            # -----------------------------

            first_verses = search_book(
                query=user_message,
                religion=first_religion,
                book=first_book,
                top_k=3
            )

            # -----------------------------
            # SECOND SCRIPTURE
            # -----------------------------

            second_verses = search_book(
                query=user_message,
                religion=second_religion,
                book=second_book,
                top_k=3
            )

            # -----------------------------
            # No results
            # -----------------------------

            if not first_verses and not second_verses:
                return {
                    "answer": (
                        "I couldn't find relevant teachings in "
                        "either selected scripture."
                    ),
                    "sources": []
                }

            # -----------------------------
            # Build contexts
            # -----------------------------

            first_context = build_context(first_verses)
            second_context = build_context(second_verses)

            # -----------------------------
            # Messages
            # -----------------------------

            messages: list = [SYSTEM_MESSAGE]

            for chat in history:
                messages.append(
                    {
                        "role": chat["role"],
                        "content": chat["content"]
                    }
                )

            comparison_prompt = (
                f"FIRST SCRIPTURE\n"
                f"Religion: {first_religion}\n"
                f"Book: {first_book}\n\n"
                f"Context:\n"
                f"{first_context}\n\n"

                f"========================================\n\n"

                f"SECOND SCRIPTURE\n"
                f"Religion: {second_religion}\n"
                f"Book: {second_book}\n\n"
                f"Context:\n"
                f"{second_context}\n\n"

                f"========================================\n\n"

                f"Question:\n"
                f"{user_message}\n\n"

                "Compare the two scriptures using ONLY "
                "the contexts provided above."
            )

            messages.append(
                {
                    "role": "user",
                    "content": comparison_prompt
                }
            )

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )

            all_sources = first_verses + second_verses

            return {
                "answer": response.choices[0].message.content,
                "sources": all_sources
            }

        # =================================
        # INVALID MODE
        # =================================

        return {
            "answer": "Invalid chat mode.",
            "sources": []
        }

    except Exception as e:

        print("LLM Error:", e)

        return {
            "answer": "Sorry, I couldn't generate a response right now.",
            "sources": []
        }