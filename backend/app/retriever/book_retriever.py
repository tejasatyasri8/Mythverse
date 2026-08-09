import os

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
# Search book
# -----------------------------------

def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 2
):

    print("=" * 50)
    print("Religion:", religion)
    print("Book:", book)
    print("Query:", query)

    # -----------------------------------
    # Search Qdrant
    # Qdrant generates the query embedding
    # -----------------------------------

    results = client.query_points(
        collection_name=COLLECTION_NAME,

        query=Document(
            text=query,
            model="sentence-transformers/all-MiniLM-L6-v2"
        ),

        query=Document(
            text=query,
            model="sentence-transformers/all-MiniLM-L6-v2"
        ),

        query_filter=Filter(
            must=[
                FieldCondition(
                    key="religion",
                    match=MatchValue(
                        value=religion
                    )
                ),

                FieldCondition(
                    key="book",
                    match=MatchValue(
                        value=book
                    )
                )
            ]
        ),

        limit=top_k,
    )

    # -----------------------------------
    # Format results
    # -----------------------------------

    output = []

    for point in results.points:

        payload = point.payload or {}

        print(payload)

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

    return output