from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/news_with_negative_categories_2023_2025.csv")

TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

print("Loading processed news data...")

news = pd.read_csv(INPUT_PATH)

news["date"] = pd.to_datetime(news["date"], errors="coerce")

category_columns = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

display_columns = [
    "ticker",
    "company",
    "date",
    "title",
    "summary",
    "ticker_sentiment_label",
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

# 1. Create examples for each category
category_examples = []

for category in category_columns:
    subset = news[
        (news["is_negative"] == 1) &
        (news[category] == 1)
    ].copy()

    if len(subset) > 0:
        examples = subset[display_columns].head(10).copy()
        examples.insert(0, "category_checked", category)
        category_examples.append(examples)

if category_examples:
    category_examples_df = pd.concat(category_examples, ignore_index=True)
else:
    category_examples_df = pd.DataFrame(columns=["category_checked"] + display_columns)

category_examples_path = TABLES_DIR / "category_examples_for_manual_check.csv"
category_examples_df.to_csv(category_examples_path, index=False)

# 2. Create random manual validation sample

negative_news = news[news["is_negative"] == 1].copy()
sample_size = min(50, len(negative_news))
manual_sample = negative_news.sample(
    n=sample_size,
    random_state=42
)[display_columns].copy()

# Add empty columns for manual checking.

manual_sample["manual_category_correct"] = ""
manual_sample["manual_comment"] = ""

manual_sample_path = TABLES_DIR / "manual_validation_sample.csv"
manual_sample.to_csv(manual_sample_path, index=False)


print("\nCategory examples saved to:")
print(category_examples_path)

print("\nManual validation sample saved to:")
print(manual_sample_path)

print("\nCategory examples preview:")
print(category_examples_df.head(20))

print("\nManual validation sample preview:")
print(manual_sample.head(20))

print("\nValidation sample created successfully.")