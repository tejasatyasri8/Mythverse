import json
import pickle
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams
import uuid
from sentence_transformers import SentenceTransformer


# Paths
BASE_DIR = Path(__file__).resolve().parents[2]

GITA_PATH = (
    BASE_DIR
    / "data"
    / "hinduism"
    / "processed"
    / "bhagavad_gita.json"
)

BIBLE_PATH = (
    BASE_DIR
    / "data"
    / "christianity"
    / "processed"
    / "bible.json"
)


VECTORSTORE_DIR = BASE_DIR / "app" / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "mythverse.index"
DOCUMENTS_PATH = VECTORSTORE_DIR / "documents.pkl"
METADATA_PATH = VECTORSTORE_DIR / "metadata.pkl"


VECTORSTORE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Load embedding model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
client = QdrantClient(
    url="http://localhost:6333"
)

COLLECTION_NAME = "mythverse"

# Create collection if not exists

collections = client.get_collections().collections

existing = [c.name for c in collections]

if COLLECTION_NAME in existing:

    client.delete_collection(
        collection_name=COLLECTION_NAME
    )

    print("Existing collection deleted.")

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

print("Collection created.")
documents = []
metadata = []


# -------------------------
# Load Bhagavad Gita
# -------------------------

with open(GITA_PATH, "r", encoding="utf-8") as file:
    gita = json.load(file)


for verse in gita:

    text = f"""
    Bhagavad Gita

    Chapter {verse['chapter']}
    Verse {verse['verse']}

    Sanskrit:
    {verse['sanskrit']}

    Translation:
    {verse['translation']}

    Meaning:
    {verse['meaning']}
    """

    documents.append(text)

    metadata.append({
        "religion": "Hinduism",
        "book": "Bhagavad Gita",
        "chapter": verse["chapter"],
        "verse": verse["verse"]
    })


# -------------------------
# Load Bible
# -------------------------

with open(BIBLE_PATH, "r", encoding="utf-8") as file:
    bible = json.load(file)


for verse in bible:

    text = f"""
    Bible

    Book:
    {verse['reference']}

    Chapter:
    {verse['chapter']}

    Verse:
    {verse['verse']}

    Text:
    {verse['text']}
    """

    documents.append(text)

    metadata.append({
        "religion": "Christianity",
        "book": "Bible",
        "reference": verse["reference"],
        "chapter": verse["chapter"],
        "verse": verse["verse"]
    })


print(
    f"Total documents: {len(documents)}"
)


# Generate embeddings

embeddings = model.encode(
    documents,
    convert_to_numpy=True,
    normalize_embeddings=True
)


# Upload embeddings to Qdrant

batch_size = 500

for start in range(0, len(embeddings), batch_size):

    batch_points = []

    end = min(start + batch_size, len(embeddings))

    for i in range(start, end):

        batch_points.append(
            PointStruct(
                id=str(uuid.uuid4()),

                vector=embeddings[i].tolist(),

                payload={
                    "text": documents[i],
                    **metadata[i]
                }
            )
        )


    client.upsert(
        collection_name=COLLECTION_NAME,
        points=batch_points
    )

    print(f"Uploaded {end}/{len(embeddings)}")

print("Uploaded embeddings to Qdrant.")


# Save documents

with open(
    DOCUMENTS_PATH,
    "wb"
) as file:
    pickle.dump(
        documents,
        file
    )


# Save metadata

with open(
    METADATA_PATH,
    "wb"
) as file:
    pickle.dump(
        metadata,
        file
    )


print("MythVerse embeddings created successfully.")
print(f"Indexed {len(documents)} documents.")