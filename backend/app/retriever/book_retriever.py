import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue


COLLECTION_NAME = "mythverse"


# -----------------------------------
# Environment variables
# -----------------------------------

load_dotenv()


# -----------------------------------
# Qdrant connection
# -----------------------------------

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)


# -----------------------------------
# Embedding model
# -----------------------------------

model = None


def get_model():

    global model

    if model is None:

        print("Loading embedding model...")

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded successfully.")

    return model


# -----------------------------------
# Search book
# -----------------------------------

def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 2
):

    # Load model only when needed
    embedding_model = get_model()


    # -----------------------------------
    # Create query embedding
    # -----------------------------------

    query_embedding = embedding_model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )


    print("=" * 50)
    print("Religion:", religion)
    print("Book:", book)
    print("Query:", query)


    # -----------------------------------
    # Search Qdrant with filters
    # -----------------------------------

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


    # -----------------------------------
    # Format results
    # -----------------------------------

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