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
# Qdrant Cloud
# -----------------------------------

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    cloud_inference=True,
    timeout=60,
)


# -----------------------------------
# Reranker
# -----------------------------------

reranker = None





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

    # Retrieve more candidates than we finally return.
    candidate_k = max(top_k, 100)

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
                    match=MatchValue(value=religion),
                ),
                FieldCondition(
                    key="book",
                    match=MatchValue(value=book),
                ),
            ]
        ),

        limit=candidate_k,
    )

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
                    "reference": payload.get("reference"),
                },

                "score": point.score,
            }
        )

    print(
        f"\nRetrieved {len(output)} semantic candidates."
    )

    # -----------------------------------
    # Print results
    # -----------------------------------

    print("\nTOP RESULTS:")

    for i, result in enumerate(
        output[:top_k],
        start=1,
    ):

        metadata = result["metadata"]

        if (
            metadata["book"] == "Bible"
            and metadata.get("reference")
        ):
            reference = metadata["reference"]
        else:
            reference = (
                f"{metadata['chapter']}:{metadata['verse']}"
            )

        print(
            f"{i}. "
            f"{metadata['book']} "
            f"{reference} "
            f"(semantic={result['score']:.4f}, "
            f"rerank={result.get('rerank_score', 0.0):.4f}, "
            f"hybrid={result.get('hybrid_score', 0.0):.4f})"
        )

    return output[:top_k]