import re

from groq import Groq
from sqlalchemy.orm import Session

from app.config import GROQ_API_KEY, MODEL_NAME
from app.database.models import ChatHistory
from app.retriever.book_retriever import search_book

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are MythVerse, a wise and concise scripture knowledge assistant. "
        "Answer the user's question directly and naturally using ONLY the provided scripture context.\n\n"
        "Core Rules:\n"
        "1. Use only the supplied scripture context to answer.\n"
        "2. Do not use outside knowledge or add unverified details.\n"
        "3. If the context is insufficient, clearly state that the selected scripture does not provide enough information.\n"
        "4. Keep explanations clear, concise, and beginner-friendly without using rigid or multi-section headings.\n"
        "5. If the user greets you (e.g., Hello, Namaste, Vanakkam, Hi, etc.) or offers a casual acknowledgment, respond warmly and briefly as a scripture assistant without forcing scripture verses into the greeting.\n"
        "6. End with a short Key Takeaway summarizing the main lesson in one sentence when answering scripture questions."
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


def clean_llm_response(content):
    """
    Remove reasoning/thinking blocks and stray markdown code blocks
    before returning the final answer to the user.
    """

    if not content:
        return ""

    # Remove <think>...</think>
    content = re.sub(
        r"<think>.*?</think>",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove any unclosed <think> block just in case
    content = re.sub(
        r"<think>.*$",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove stray markdown code blocks
    content = re.sub(
        r"```.*?```",
        "",
        content,
        flags=re.DOTALL
    )

    return content.strip()


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
        # Catch simple casual greetings immediately
        cleaned_msg = user_message.strip().lower()

        if cleaned_msg in ["hi", "hello", "hey", "greetings"]:
            return {
                "answer": (
                    "Hello! 🙏 I'm MythVerse, your scripture knowledge assistant. "
                    "Feel free to ask any questions about the Bhagavad Gita "
                    "or other texts you'd like to explore."
                ),
                "sources": []
            }

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

            answer = clean_llm_response(
                response.choices[0].message.content
            )

            return {
                "answer": answer,
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

            answer = clean_llm_response(
                response.choices[0].message.content
            )

            all_sources = first_verses + second_verses

            return {
                "answer": answer,
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