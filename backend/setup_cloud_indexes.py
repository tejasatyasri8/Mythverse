import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

cloud = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "mythverse"

print("Creating payload indexes...")

# Index religion
cloud.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="religion",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

print("Created index: religion")

# Index book
cloud.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="book",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

print("Created index: book")

print("Cloud payload indexes created successfully!")

# Verify
info = cloud.get_collection(COLLECTION_NAME)

print("\nCloud collection:")
print("Points:", info.points_count)
print("Payload indexes:", info.payload_schema)