import re

from app.retriever.book_retriever import search_book


questions = [
    {
        "question": "What does the Bhagavad Gita say about performing one's duty?",
        "religion": "Hinduism",
        "book": "Bhagavad Gita",
        "expected": [
            ("Bhagavad Gita", 2, 47),
            ("Bhagavad Gita", 3, 35),
        ],
    },
    {
        "question": "What does the Bhagavad Gita say about the soul?",
        "religion": "Hinduism",
        "book": "Bhagavad Gita",
        "expected": [
            ("Bhagavad Gita", 2, 23),
            ("Bhagavad Gita", 2, 20),
            ("Bhagavad Gita", 13, 32),
        ],
    },
    {
        "question": "What does the Bible say about loving your enemies?",
        "religion": "Christianity",
        "book": "Bible",
        "expected": [
            ("Luke", 6, 27),
            ("Matthew", 5, 44),
        ],
    },
]


def get_reference(result):
    metadata = result["metadata"]

    book = metadata.get("book")
    chapter = metadata.get("chapter")
    verse = metadata.get("verse")

    if book and chapter is not None and verse is not None:
        return (book, int(chapter), int(verse))

    return None


# ============================================================
# EVALUATION
# ============================================================

results_by_question = []

for item in questions:

    print("\n" + "=" * 70)

    print("QUESTION:")
    print(item["question"])

    print("\nEXPECTED REFERENCES:")

    for expected in item["expected"]:
        print(
            f"- {expected[0]} "
            f"{expected[1]}:{expected[2]}"
        )

    results = search_book(
        query=item["question"],
        religion=item["religion"],
        book=item["book"],
        top_k=10,
    )

    retrieved = []

    print("\nRETRIEVED:")

    for i, result in enumerate(results, start=1):

        reference = get_reference(result)

        retrieved.append(reference)

        print(
            f"{i}. {reference} "
            f"(score={result['score']:.4f})"
        )

    results_by_question.append(
        {
            "question": item["question"],
            "expected": item["expected"],
            "retrieved": retrieved,
        }
    )


# ============================================================
# METRICS
# ============================================================

total_questions = len(results_by_question)

recall_at_1 = 0
recall_at_3 = 0
recall_at_5 = 0
recall_at_10 = 0

reciprocal_ranks = []


for item in results_by_question:

    expected = set(item["expected"])
    retrieved = item["retrieved"]

    # ------------------------------------
    # Recall@1
    # ------------------------------------

    if any(ref in expected for ref in retrieved[:1]):
        recall_at_1 += 1

    # ------------------------------------
    # Recall@3
    # ------------------------------------

    if any(ref in expected for ref in retrieved[:3]):
        recall_at_3 += 1

    # ------------------------------------
    # Recall@5
    # ------------------------------------

    if any(ref in expected for ref in retrieved[:5]):
        recall_at_5 += 1

    # ------------------------------------
    # Recall@10
    # ------------------------------------

    if any(ref in expected for ref in retrieved[:10]):
        recall_at_10 += 1

    # ------------------------------------
    # MRR
    # ------------------------------------

    reciprocal_rank = 0

    for rank, ref in enumerate(retrieved, start=1):

        if ref in expected:
            reciprocal_rank = 1 / rank
            break

    reciprocal_ranks.append(reciprocal_rank)


mrr = sum(reciprocal_ranks) / total_questions


# ============================================================
# FINAL REPORT
# ============================================================

print("\n")
print("=" * 70)
print("MYTHVERSE RAG EVALUATION")
print("=" * 70)

print(f"\nQuestions: {total_questions}")

print(
    f"Recall@1:  "
    f"{recall_at_1 / total_questions * 100:.2f}%"
)

print(
    f"Recall@3:  "
    f"{recall_at_3 / total_questions * 100:.2f}%"
)

print(
    f"Recall@5:  "
    f"{recall_at_5 / total_questions * 100:.2f}%"
)

print(
    f"Recall@10: "
    f"{recall_at_10 / total_questions * 100:.2f}%"
)

print(f"MRR:       {mrr:.4f}")


# ============================================================
# FAILURE REPORT
# ============================================================

print("\n" + "=" * 70)
print("FAILURE ANALYSIS")
print("=" * 70)

for item in results_by_question:

    expected = set(item["expected"])
    retrieved = item["retrieved"]

    if not any(ref in expected for ref in retrieved[:5]):

        print("\nFAILED QUESTION:")
        print(item["question"])

        print("Expected:")
        for ref in expected:
            print(" ", ref)

        print("Retrieved:")
        for rank, ref in enumerate(retrieved, start=1):
            print(f"  {rank}. {ref}")