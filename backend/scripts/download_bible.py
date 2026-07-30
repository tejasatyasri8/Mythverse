from datasets import load_dataset

print("Downloading Bible dataset...")

dataset = load_dataset("DatadudeDev/Bible")

print(dataset)

dataset["train"].to_csv(
    "data/christianity/raw/bible.csv",
    index=False
)

print("Bible downloaded successfully.")