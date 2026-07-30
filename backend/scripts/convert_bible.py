import pandas as pd
import json
from pathlib import Path


INPUT_FILE = "data/christianity/raw/bible.csv"
OUTPUT_FILE = "data/christianity/processed/bible.json"


def convert_bible():

    df = pd.read_csv(INPUT_FILE)

    bible = []

    for _, row in df.iterrows():

        bible.append({
            "book": "Bible",
            "chapter": int(row["chapter"]),
            "verse": int(row["verse"]),
            "reference": row["citation"],
            "text": row["text"]
        })


    Path("data/processed").mkdir(
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            bible,
            f,
            ensure_ascii=False,
            indent=2
        )


    print(
        f"Converted {len(bible)} Bible verses"
    )


if __name__ == "__main__":
    convert_bible()