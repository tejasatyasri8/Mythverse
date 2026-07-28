import json
import os


DATA_PATH = os.path.join(
    "data",
    "bhagavad_gita.json"
)


def load_gita():

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)



def search_gita(query: str, top_k: int = 2):

    verses = load_gita()

    query_words = query.lower().split()

    results = []


    for verse in verses:

        score = 0

        text = (
            verse["meaning"]
            + " "
            + " ".join(verse["keywords"])
        ).lower()


        for word in query_words:

            if word in text:
                score += 1


        if score > 0:
            results.append(
                (score, verse)
            )


    results.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return [
        item[1]
        for item in results[:top_k]
    ]