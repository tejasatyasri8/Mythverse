import json
import re

from app.retriever.book_retriever import search_book


DATASET_PATH = "evaluation/rag_dataset.json"


def normalize(text):
    """Normalize text for easier reference matching."""
    return re.sub(r"\s+", " ", text.strip().lower())


def reference_matches(result, expected_reference):
    """
    Check whether a retrieved result matches an expected scripture reference.
    """

    metadata = result["metadata"]

    book = metadata.get("book", "")
    chapter = str(metadata.get("chapter", "")).strip()
    verse = str(metadata.get("verse", "")).strip()

    # Bhagavad Gita
    if book == "Bhagavad Gita":
        match = re.search(r"(\d+):(\d+)", expected_reference)

        if not match:
            return False

        expected_chapter = match.group(1)
        expected_verse = match.group(2)

        return (
            chapter == expected_chapter
            and verse == expected_verse
        )

    # Bible
    if book == "Bible":

        reference = metadata.get("reference")

        if not reference:
            return False

        actual_reference = normalize(str(reference))
        expected_reference = normalize(expected_reference)

        actual_reference = re.sub(
            r"^psalm\b",
            "psalms",
            actual_reference,
        )

        expected_reference = re.sub(
            r"^psalm\b",
            "psalms",
            expected_reference,
        )

        return actual_reference == expected_reference
    return False


def evaluate_question(item, top_k=100):

    results = search_book(
        query=item["question"],
        religion=item["religion"],
        book=item["book"],
        top_k=top_k,
    )

    expected_references = item.get("expected_references")

    if expected_references is None:
        expected_reference = item.get("expected_reference")

        if expected_reference is not None:
            expected_references = [expected_reference]
        else:
            raise KeyError(
                "Dataset must contain 'expected_references' "
                "or 'expected_reference'"
            )

    first_hit_rank = None

    for rank, result in enumerate(results, start=1):

        matched = any(
            reference_matches(result, expected)
            for expected in expected_references
        )

        if matched:
            first_hit_rank = rank
            break

    return first_hit_rank


def main():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    total = len(dataset)

    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0
    hits_at_10 = 0
    hits_at_100 = 0

    reciprocal_rank_sum = 0

    for item in dataset:

        rank = evaluate_question(item, top_k=100)

        if rank is not None:

            if rank <= 1:
                hits_at_1 += 1

            if rank <= 3:
                hits_at_3 += 1

            if rank <= 5:
                hits_at_5 += 1

            if rank <= 10:
                hits_at_10 += 1

            if rank <= 100:
                hits_at_100 += 1

            reciprocal_rank_sum += 1 / rank

    print("\n")
    print("=" * 80)
    print("MYTHVERSE RAG EVALUATION")
    print("=" * 80)

    print(f"Questions: {total}")

    print(
        f"Recall@1:   {hits_at_1 / total * 100:.2f}%"
    )

    print(
        f"Recall@3:   {hits_at_3 / total * 100:.2f}%"
    )

    print(
        f"Recall@5:   {hits_at_5 / total * 100:.2f}%"
    )

    print(
        f"Recall@10:  {hits_at_10 / total * 100:.2f}%"
    )

    print(
        f"Recall@100: {hits_at_100 / total * 100:.2f}%"
    )

    print(
        f"MRR:        {reciprocal_rank_sum / total:.4f}"
    )


if __name__ == "__main__":
    main()