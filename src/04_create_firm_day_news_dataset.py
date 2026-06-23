from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/news_with_negative_categories_2023_2025.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading processed news data...")

news = pd.read_csv(INPUT_PATH)

print("News data loaded.")
print("Shape:", news.shape)


# Make sure date is a proper date variable.
news["date"] = pd.to_datetime(news["date"], errors="coerce")

# These are the negative news category variables we created in the previous step.
category_columns = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

# We create two general count variables:
# article_count = total number of news articles for a firm on a day
# negative_article_count = total number of negative news articles for a firm on a day

news["article_count"] = 1
news["negative_article_count"] = news["is_negative"]

# Now we aggregate the news data to firm-day level.
# This means each row will be one company on one date.
firm_day_news = (
    news
    .groupby(["ticker", "company", "date"], as_index=False)
    .agg({
        "article_count": "sum",
        "negative_article_count": "sum",
        "neg_earnings": "sum",
        "neg_growth": "sum",
        "neg_regulation": "sum",
        "neg_competition": "sum",
        "neg_macro": "sum",
        "neg_other": "sum"
    })
)

# Total number of classified negative news articles.
# One article can belong to more than one category, so this is not always equal to negative_article_count.
firm_day_news["total_classified_negative_categories"] = firm_day_news[category_columns].sum(axis=1)

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