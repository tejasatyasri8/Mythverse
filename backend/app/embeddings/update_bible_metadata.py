import os
import json
import re

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

load_dotenv()

COLLECTION_NAME = "mythverse"

# -----------------------------------
# Qdrant Cloud
# -----------------------------------

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
)

# -----------------------------------
# Load Bible JSON
# -----------------------------------

DATA_PATH = "data/christianity/processed/bible.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    bible = json.load(f)

print(f"Bible verses loaded: {len(bible)}")

# -----------------------------------
# Create Bible lookup
# -----------------------------------

bible_lookup = {
    verse["reference"]: verse
    for verse in bible
}

# -----------------------------------
# Find all Bible points
# -----------------------------------

print("Finding Bible points in Qdrant...")

scroll_filter = Filter(
    must=[
        FieldCondition(
            key="religion",
            match=MatchValue(
                value="Christianity"
            ),
        ),
        FieldCondition(
            key="book",
            match=MatchValue(
                value="Bible"
            ),
        ),
    ]
)

all_points = []
offset = None

while True:

    points, next_offset = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=scroll_filter,
        limit=1000,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )

    all_points.extend(points)

    print(f"Found: {len(all_points)}")

    if next_offset is None:
        break

    offset = next_offset

print(f"Total Bible points found: {len(all_points)}")

# -----------------------------------
# Prepare metadata updates
# -----------------------------------

updates = []

for point in all_points:

    payload = point.payload or {}

    reference = payload.get("reference")

    # -----------------------------------
    # If reference is missing,
    # extract it from the stored text.
    # -----------------------------------

    if not reference:

        text = payload.get("text", "")

        match = re.search(
            r"Book:\s*([A-Za-z]+)\s+(\d+:\d+)",
            text,
            re.IGNORECASE,
        )

        if match:

            scripture_book = match.group(1).strip()

            chapter_verse = match.group(2).strip()

            reference = (
                f"{scripture_book} "
                f"{chapter_verse}"
            )

        else:
            continue

    # -----------------------------------
    # Find verse in Bible JSON
    # -----------------------------------

    verse = bible_lookup.get(reference)

    if not verse:
        continue

    scripture_book = reference.rsplit(" ", 1)[0]

    new_payload = {
        "religion": "Christianity",
        "book": "Bible",
        "scripture_book": scripture_book,
        "reference": reference,
        "chapter": verse["chapter"],
        "verse": verse["verse"],
    }

    updates.append(
        (
            point.id,
            new_payload,
        )
    )

print(
    f"Metadata updates prepared: "
    f"{len(updates)}"
)

# -----------------------------------
# Update Qdrant
# -----------------------------------

BATCH_SIZE = 100

for start in range(
    0,
    len(updates),
    BATCH_SIZE
):

    batch = updates[
        start:start + BATCH_SIZE
    ]

    for point_id, payload in batch:

        client.set_payload(
            collection_name=COLLECTION_NAME,
            payload=payload,
            points=[point_id],
            wait=False,
        )

    completed = min(
        start + BATCH_SIZE,
        len(updates),
    )

    print(
        f"Updated: "
        f"{completed}/{len(updates)}"
    )

# -----------------------------------
# Done
# -----------------------------------

print()
print("========================================")
print("Bible metadata update completed!")
print("========================================")