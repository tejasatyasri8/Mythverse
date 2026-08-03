from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Local database stored in project folder
client = QdrantClient(path="app/vectorstore/qdrant_data")

COLLECTION_NAME = "mythverse"

# Delete collection if it already exists
try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

# Create collection
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=384,      # all-MiniLM-L6-v2 embedding size
        distance=Distance.COSINE,
    ),
)

print(f"Collection '{COLLECTION_NAME}' created successfully.")