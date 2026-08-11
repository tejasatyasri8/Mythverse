import os
import re

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    Document,
)

load_dotenv()

COLLECTION_NAME = "mythverse"

# -----------------------------------
# Qdrant Cloud connection
# -----------------------------------

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    cloud_inference=True,
    timeout=60,
)


# -----------------------------------
# Text normalization
# -----------------------------------

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------------
# Remove common stop words
# -----------------------------------

STOP_WORDS = {
    "what",
    "does",
    "the",
    "say",
    "about",
    "how",
    "is",
    "are",
    "of",
    "a",
    "an",
    "to",
    "in",
    "on",
    "for",
    "and",
    "your",
    "their",
    "its",
    "this",
    "that",
}


def get_keywords(text: str):
    words = normalize_text(text).split()

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    }


# -----------------------------------
# Reranking
# -----------------------------------

def rerank_results(query: str, results):

    query_text = normalize_text(query)
    query_keywords = get_keywords(query)

    for result in results:

        text = normalize_text(result["text"])
        text_words = set(text.split())

        # -----------------------------------
        # Keyword overlap
        # -----------------------------------

        matched_keywords = query_keywords & text_words

        if query_keywords:
            keyword_overlap = (
                len(matched_keywords)
                / len(query_keywords)
            )
        else:
            keyword_overlap = 0

        # -----------------------------------
        # Exact query phrase
        # -----------------------------------

        phrase_bonus = 0

        if len(query_text) > 5 and query_text in text:
            phrase_bonus = 0.20

        # -----------------------------------
        # Consecutive keyword phrase matching
        # -----------------------------------

        query_words = query_text.split()

        for size in range(
            min(4, len(query_words)),
            1,
            -1
        ):

            found_phrase = False

            for i in range(
                len(query_words) - size + 1
            ):

                phrase = " ".join(
                    query_words[i:i + size]
                )

                if len(phrase) > 4 and phrase in text:
                    phrase_bonus = max(
                        phrase_bonus,
                        size * 0.05
                    )
                    found_phrase = True
                    break

            if found_phrase:
                break

        # -----------------------------------
        # Final score
        # -----------------------------------

        result["rerank_score"] = (
            result["score"]
            + (keyword_overlap * 0.20)
            + phrase_bonus
        )

        result["matched_keywords"] = list(
            matched_keywords
        )

    results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return results


# -----------------------------------
# Search book
# -----------------------------------

def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 10,
):

    print("=" * 50)
    print("Religion:", religion)
    print("Book:", book)
    print("Query:", query)

    # -----------------------------------
    # Retrieve more semantic candidates
    # -----------------------------------

    candidate_k = max(top_k * 3, 30)

    results = client.query_points(
        collection_name=COLLECTION_NAME,

        query=Document(
            text=query,
            model="sentence-transformers/all-MiniLM-L6-v2",
        ),

        query_filter=Filter(
            must=[
                FieldCondition(
                    key="religion",
                    match=MatchValue(
                        value=religion
                    ),
                ),

                FieldCondition(
                    key="book",
                    match=MatchValue(
                        value=book
                    ),
                ),
            ]
        ),

        limit=candidate_k,
    )

    # -----------------------------------
    # Format results
    # -----------------------------------

    output = []

    for point in results.points:

        payload = point.payload or {}

        output.append(
            {
                "text": payload.get("text", ""),

                "metadata": {
                    "religion": payload.get("religion"),
                    "book": payload.get("book"),
                    "chapter": payload.get("chapter"),
                    "verse": payload.get("verse"),
                },

                "score": point.score,
            }
        )

    # -----------------------------------
    # Rerank
    # -----------------------------------

    output = rerank_results(
        query,
        output
    )

    # -----------------------------------
    # Print final ranking
    # -----------------------------------

    print("\nRERANKED RESULTS:")

    for i, result in enumerate(
        output[:top_k],
        start=1
    ):

        metadata = result["metadata"]

        print(
            f"{i}. "
            f"{metadata['book']} "
            f"{metadata['chapter']}:{metadata['verse']} "
            f"(semantic={result['score']:.4f}, "
            f"rerank={result['rerank_score']:.4f})"
        )

    return output[:top_k]