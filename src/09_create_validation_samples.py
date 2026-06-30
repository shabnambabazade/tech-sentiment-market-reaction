from pathlib import Path
import pandas as pd


NEWS_PATH = Path("data/processed/news_with_negative_categories_2023_2025.csv")
OUTPUT_DIR = Path("outputs/validation_samples")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("Loading categorized news data...")
news = pd.read_csv(NEWS_PATH)


category_columns = [
    "neg_earnings_guidance",
    "neg_demand_growth",
    "neg_legal_regulatory",
    "neg_product_technology",
    "neg_strategy_management",
    "neg_competition_pressure",
    "neg_other",
]

category_labels = {
    "neg_earnings_guidance": "earnings_guidance",
    "neg_demand_growth": "demand_growth",
    "neg_legal_regulatory": "legal_regulatory",
    "neg_product_technology": "product_technology",
    "neg_strategy_management": "strategy_management",
    "neg_competition_pressure": "competition_pressure",
    "neg_other": "other_negative",
}


sample_columns = [
    "ticker",
    "company",
    "date",
    "title",
    "summary",
    "ticker_sentiment_label",
] + category_columns


all_samples = []

for column in category_columns:
    category_data = news[news[column] == 1].copy()

    if len(category_data) == 0:
        print(column, "has no observations.")
        continue

    sample_size = min(15, len(category_data))

    sample = category_data.sample(
        n=sample_size,
        random_state=42,
    )[sample_columns]

    sample["sample_category"] = category_labels[column]

    output_path = OUTPUT_DIR / f"validation_sample_{category_labels[column]}.csv"
    sample.to_csv(output_path, index=False)

    all_samples.append(sample)

    print(column, "sample saved:", output_path)


if all_samples:
    combined = pd.concat(all_samples, ignore_index=True)
    combined_path = OUTPUT_DIR / "validation_sample_all_categories.csv"
    combined.to_csv(combined_path, index=False)

    print("\nCombined validation sample saved to:")
    print(combined_path)
    print("Rows:", len(combined))
else:
    print("No validation samples created.")
