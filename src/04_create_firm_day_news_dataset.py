from pathlib import Path
import pandas as pd


INPUT_PATH = Path("data/processed/news_with_negative_categories_2023_2025.csv")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("Loading processed news data...")
news = pd.read_csv(INPUT_PATH)

print("News data loaded.")
print("Shape:", news.shape)


news["date"] = pd.to_datetime(news["date"], errors="coerce")


event_category_columns = [
    "neg_earnings_guidance",
    "neg_demand_growth",
    "neg_legal_regulatory",
    "neg_product_technology",
    "neg_strategy_management",
    "neg_competition_pressure",
]

category_columns = event_category_columns + ["neg_other"]


news["article_count"] = 1
news["negative_article_count"] = news["is_negative"]


agg_columns = {
    "article_count": "sum",
    "negative_article_count": "sum",
}

for column in category_columns:
    agg_columns[column] = "sum"


firm_day_news = (
    news
    .groupby(["ticker", "company", "date"], as_index=False)
    .agg(agg_columns)
)


# one article can appear in more than one category,
# so this is a category count, not the same as negative_article_count
firm_day_news["total_classified_negative_categories"] = (
    firm_day_news[category_columns].sum(axis=1)
)


output_path = OUTPUT_DIR / "news_firm_day_2023_2025.csv"
firm_day_news.to_csv(output_path, index=False)


print("\nFirm-day news dataset saved to:")
print(output_path)

print("\nDataset shape:")
print(firm_day_news.shape)

print("\nPreview:")
print(firm_day_news.head(20))

print("\nDate range:")
print(firm_day_news["date"].min(), "to", firm_day_news["date"].max())

print("\nObservations by ticker:")
print(firm_day_news["ticker"].value_counts())

print("\nTotal category counts:")
for column in category_columns:
    print(column, "=", int(firm_day_news[column].sum()))
