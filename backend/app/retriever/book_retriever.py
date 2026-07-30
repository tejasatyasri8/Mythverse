import pickle
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]


INDEX_PATH = (
    BASE_DIR
    / "app"
    / "vectorstore"
    / "mythverse.index"
)

DOCUMENTS_PATH = (
    BASE_DIR
    / "app"
    / "vectorstore"
    / "documents.pkl"
)

METADATA_PATH = (
    BASE_DIR
    / "app"
    / "vectorstore"
    / "metadata.pkl"
)


# Load embedding model once
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Load FAISS index
index = faiss.read_index(
    str(INDEX_PATH)
)


# Load documents
with open(
    DOCUMENTS_PATH,
    "rb"
) as file:
    documents = pickle.load(file)


# Load metadata
with open(
    METADATA_PATH,
    "rb"
) as file:
    metadata = pickle.load(file)



def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 3
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )


    # Search more results first
    distances, indices = index.search(
        query_embedding.astype("float32"),
        20
    )


    results = []


    for score, idx in zip(
        distances[0],
        indices[0]
    ):

        if idx == -1:
            continue


        meta = metadata[idx]


        # Filter selected source
        if (
            meta["religion"] == religion
            and meta["book"] == book
        ):

            results.append(
                {
                    "text": documents[idx],
                    "metadata": meta,
                    "score": float(score)
                }
            )


        if len(results) == top_k:
            break


    return results