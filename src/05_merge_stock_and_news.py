from pathlib import Path
import pandas as pd

STOCK_PATH = Path("data/processed/stock_data_processed_2023_2025.csv")
NEWS_PATH = Path("data/processed/news_firm_day_2023_2025.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print("Loading stock data...")
stock = pd.read_csv(STOCK_PATH)
print("Loading firm-day news data...")
news = pd.read_csv(NEWS_PATH)
print("\nStock data shape:", stock.shape)
print("News data shape:", news.shape)

# Make sure date columns are real dates.
stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
news["date"] = pd.to_datetime(news["date"], errors="coerce")

# These are the news variables we want to merge into the stock dataset.
news_count_columns = [
    "article_count",
    "negative_article_count",
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other",
    "total_classified_negative_categories"
]

# Important: Some news may be published on weekends or holidays. Stock market data only exists for trading days.
# To avoid losing weekend news, we map each news date to the next available trading day for the same ticker.

print("\nAligning news dates to trading days...")
stock_trading_days = (
    stock[["ticker", "date"]]
    .drop_duplicates()
    .sort_values(["ticker", "date"])
)

news_for_alignment = news.sort_values(["ticker", "date"]).copy()
aligned_news_list = []

for ticker in news_for_alignment["ticker"].unique():
    news_ticker = news_for_alignment[news_for_alignment["ticker"] == ticker].copy()
    trading_days_ticker = stock_trading_days[stock_trading_days["ticker"] == ticker].copy()

    aligned = pd.merge_asof(
        news_ticker.sort_values("date"),
        trading_days_ticker.sort_values("date"),
        on="date",
        by="ticker",
        direction="forward"
    )

    aligned_news_list.append(aligned)

aligned_news = pd.concat(aligned_news_list, ignore_index=True)

# After merge_asof, the "date" column is now the matched trading date.
# However, because some weekend news can be mapped to the same Monday, we aggregate once more at ticker-date level.

aligned_news = (
    aligned_news
    .groupby(["ticker", "date"], as_index=False)[news_count_columns]
    .sum()
)


print("Aligned news data shape:", aligned_news.shape)

# Now we merge the news variables into the stock dataset. We keep all stock trading days.
# If there was no news for a ticker-date, the news variables become 0.

print("\nMerging stock and news data...")

final_data = stock.merge(
    aligned_news,
    on=["ticker", "date"],
    how="left"
)

# Replace missing news values with 0. Missing means there was no matching news for that firm-day.

for column in news_count_columns:
    final_data[column] = final_data[column].fillna(0)

# Convert news count columns to integers.
for column in news_count_columns:
    final_data[column] = final_data[column].astype(int)

# Save final analysis dataset.
output_path = OUTPUT_DIR / "final_analysis_dataset_2023_2025.csv"
final_data.to_csv(output_path, index=False)

print("\nFinal analysis dataset saved to:")
print(output_path)

print("\nFinal dataset shape:")
print(final_data.shape)

print("\nPreview:")
print(final_data.head(20))

print("\nDate range:")
print(final_data["date"].min(), "to", final_data["date"].max())

print("\nObservations by ticker:")
print(final_data["ticker"].value_counts())

print("\nTotal news counts in final dataset:")
for column in news_count_columns:
    print(column, "=", int(final_data[column].sum()))

print("\nRows with at least one negative news article:")
print((final_data["negative_article_count"] > 0).sum())

print("\nExample rows with negative news:")
example_columns = [
    "ticker",
    "company",
    "date",
    "daily_return",
    "next_day_return",
    "log_volume",
    "negative_article_count",
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

print(final_data.loc[final_data["negative_article_count"] > 0, example_columns].head(20))