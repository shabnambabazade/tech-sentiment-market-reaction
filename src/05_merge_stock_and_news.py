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


stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
news["date"] = pd.to_datetime(news["date"], errors="coerce")


category_columns = [
    "neg_earnings_guidance",
    "neg_demand_growth",
    "neg_legal_regulatory",
    "neg_product_technology",
    "neg_strategy_management",
    "neg_competition_pressure",
    "neg_other",
]


# News can be published on weekends or market holidays.
# This moves each news date to the next available trading day for the same firm.
aligned_news_parts = []

for ticker in news["ticker"].dropna().unique():
    ticker_news = news[news["ticker"] == ticker].copy()

    ticker_stock_dates = stock.loc[
        stock["ticker"] == ticker,
        ["ticker", "date"]
    ].copy()

    ticker_stock_dates = ticker_stock_dates.rename(columns={"date": "trading_date"})

    ticker_news = ticker_news.sort_values("date")
    ticker_stock_dates = ticker_stock_dates.sort_values("trading_date")

    aligned = pd.merge_asof(
        ticker_news,
        ticker_stock_dates,
        left_on="date",
        right_on="trading_date",
        by="ticker",
        direction="forward",
    )

    aligned_news_parts.append(aligned)


aligned_news = pd.concat(aligned_news_parts, ignore_index=True)

# News after the final available trading day cannot be matched.
# This should normally be very small, but we report it to be transparent.
unmatched_news = aligned_news["trading_date"].isna().sum()

if unmatched_news > 0:
    print("\nUnmatched news rows after trading-day alignment:", unmatched_news)

aligned_news = aligned_news.dropna(subset=["trading_date"])


news_columns_to_sum = [
    "article_count",
    "negative_article_count",
] + category_columns


firm_day_news = (
    aligned_news
    .groupby(["ticker", "company", "trading_date"], as_index=False)[news_columns_to_sum]
    .sum()
)

firm_day_news = firm_day_news.rename(columns={"trading_date": "date"})


panel = stock.merge(
    firm_day_news,
    on=["ticker", "company", "date"],
    how="left",
)


count_columns = [
    "article_count",
    "negative_article_count",
] + category_columns

for column in count_columns:
    panel[column] = panel[column].fillna(0).astype(int)


panel["has_negative_news"] = (panel["negative_article_count"] > 0).astype(int)


output_path = OUTPUT_DIR / "final_analysis_dataset_2023_2025.csv"
panel.to_csv(output_path, index=False)


print("\nMerged final dataset saved to:")
print(output_path)

print("\nDataset shape:")
print(panel.shape)

print("\nDate range:")
print(panel["date"].min(), "to", panel["date"].max())

print("\nObservations by ticker:")
print(panel["ticker"].value_counts())

print("\nTotal article counts:")
print("article_count =", int(panel["article_count"].sum()))
print("negative_article_count =", int(panel["negative_article_count"].sum()))

print("\nTotal category counts:")
for column in category_columns:
    print(column, "=", int(panel[column].sum()))

print("\nPreview:")
print(panel.head())
