import json


INPUT_FILE = "data/raw/gita.jsonl"
OUTPUT_FILE = "data/processed/bhagavad_gita.json"


processed = []


with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        verse = json.loads(line)

        prabhu = verse.get("prabhu") or {}
        tej = verse.get("tej") or {}

        item = {
            "chapter": verse.get("chapter"),
            "verse": verse.get("verse"),

            "sanskrit": verse.get("slok", ""),

            "translation": prabhu.get("et", ""),

            "meaning": tej.get("ht", "")
        }

        processed.append(item)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        processed,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"Converted {len(processed)} verses.")
print(f"Saved to {OUTPUT_FILE}")