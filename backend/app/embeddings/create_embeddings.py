import json
import pickle
from pathlib import Path

import faiss
import numpy as np
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


# Create FAISS index

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(
    dimension
)

index.add(
    np.array(embeddings)
    .astype("float32")
)


# Save FAISS index

faiss.write_index(
    index,
    str(INDEX_PATH)
)


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