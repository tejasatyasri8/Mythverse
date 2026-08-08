import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue


COLLECTION_NAME = "mythverse"


# Connect to Qdrant Docker
load_dotenv()
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Load embedding model once
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 2
):

    # Create query embedding

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("=" * 50)
    print("Religion:", religion)
    print("Book:", book)
    print("Query:", query)
    # Search Qdrant with filters

    results = client.query_points(
        collection_name=COLLECTION_NAME,

        query=query_embedding.tolist(),

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

        limit=top_k
    )


    output = []


    for point in results.points:
        payload = point.payload or {}
        print(point.payload)

        output.append(
            {
                "text": payload.get("text", ""),

                "metadata": {
                    "religion": payload.get("religion"),
                    "book": payload.get("book"),
                    "chapter": payload.get("chapter"),
                    "verse": payload.get("verse")
                },

                "score": point.score
            }
        )


    return output