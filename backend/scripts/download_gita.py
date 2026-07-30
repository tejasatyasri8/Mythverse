from pathlib import Path
from datasets import load_dataset
import json

print("Downloading Bhagavad Gita dataset...")

# Download dataset
dataset = load_dataset(
    "Voider22/bhagavad-gita-verses-sanskrit-translations"
)

train = dataset["train"]

output_dir = Path("../data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "gita.jsonl"

with open(output_file, "w", encoding="utf-8") as f:
    for row in train:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"\nDownloaded {len(train)} verses.")
print(f"Saved to: {output_file.resolve()}")