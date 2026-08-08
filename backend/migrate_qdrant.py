import os
import time
from dotenv import load_dotenv
from typing import cast

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)


load_dotenv()


# -----------------------------
# Local Docker Qdrant
# -----------------------------

local = QdrantClient(
    url="http://localhost:6333"
)


# -----------------------------
# Qdrant Cloud
# -----------------------------

cloud = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=300
)


collection_name = "mythverse"


# -----------------------------
# Check local collection
# -----------------------------

info = local.get_collection(collection_name)

print(
    "Local points:",
    info.points_count
)


# -----------------------------
# Create collection in cloud
# -----------------------------

try:

    cloud.get_collection(collection_name)

    print(
        "Cloud collection already exists"
    )

except Exception:

    print(
        "Creating cloud collection..."
    )

    cloud.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    print(
        "Cloud collection created"
    )


# -----------------------------
# Get existing cloud IDs
# -----------------------------

existing = set()

offset = None

while True:

    records, offset = cloud.scroll(
        collection_name=collection_name,
        limit=1000,
        offset=offset,
        with_payload=False,
        with_vectors=False
    )

    for r in records:
        existing.add(r.id)

    if offset is None:
        break


print(
    "Already in cloud:",
    len(existing)
)


# -----------------------------
# Migration
# -----------------------------

offset = None


while True:

    records, offset = local.scroll(
        collection_name=collection_name,
        limit=100,
        offset=offset,
        with_payload=True,
        with_vectors=False
    )


    if not records:
        break


    ids = [
        record.id
        for record in records
    ]


    # Get vectors
    full_points = local.retrieve(
        collection_name=collection_name,
        ids=ids,
        with_vectors=True
    )


    cloud_points = []


    for point in full_points:


        # Skip already migrated points
        if point.id in existing:
            continue


        if point.vector is None:
            continue


        cloud_points.append(
            PointStruct(
                id=point.id,
                vector=cast(list[float], point.vector),
                payload=point.payload
            )
        )


    if cloud_points:

        try:

            cloud.upsert(
                collection_name=collection_name,
                points=cloud_points,
                wait=True
            )


            print(
                "Uploaded:",
                len(cloud_points)
            )


            # Add uploaded IDs locally
            for p in cloud_points:
                existing.add(p.id)


            time.sleep(1)


        except Exception as e:

            print(
                "Upload failed:",
                e
            )

            print(
                "Waiting 10 seconds before retry..."
            )

            time.sleep(10)

            continue


    else:

        print(
            "Skipped existing batch"
        )


    if offset is None:
        break



print(
    "Migration completed successfully!"
)