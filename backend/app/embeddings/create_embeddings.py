import json
import pickle
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client.models import SparseVectorParams
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct, Distance, VectorParams, SparseVectorParams

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
model = SentenceTransformer("all-MiniLM-L6-v2")
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
)
sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
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
    vectors_config={
        "dense": VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    },
    sparse_vectors_config={
        "sparse": SparseVectorParams(
            # Using the IDF modifier is standard for BM25 search
            index=models.SparseIndexParams(
                on_disk=False,
            )
        )
    }
)

print("Collection created.")
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="religion",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="book",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

print("Payload indexes created.")
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


# Generate Dense Embeddings
dense_embeddings = model.encode(
    documents,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# Generate Sparse (BM25) Embeddings
sparse_embeddings = list(sparse_model.embed(documents))




# Upload embeddings to Qdrant

batch_size = 500

for start in range(0, len(dense_embeddings), batch_size):
    batch_points = []
    end = min(start + batch_size, len(dense_embeddings))

    for i in range(start, end):
        
        # FastEmbed returns a SparseEmbedding object containing indices and values
        sparse_vec = sparse_embeddings[i]

        batch_points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": dense_embeddings[i].tolist(),
                    "sparse": models.SparseVector(
                        indices=sparse_vec.indices.tolist(),
                        values=sparse_vec.values.tolist()
                    )
                },
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