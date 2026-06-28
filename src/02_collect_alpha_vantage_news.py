from pathlib import Path
import os
import time
import json
import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if API_KEY is None:
    raise ValueError("API key not found. Please check your .env file.")


TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta",

    # added these to make the sample more diverse
    "ZM": "Zoom",
    "SNAP": "Snap",
    "SNOW": "Snowflake",
    "NET": "Cloudflare",
    "ROKU": "Roku",
    "DBX": "Dropbox",
}


YEARS = [2023, 2024, 2025]

# keeping this below the daily API limit to be safe
MAX_REQUESTS_THIS_RUN = 20

RAW_DIR = Path("data/raw")
CACHE_DIR = RAW_DIR / "alpha_vantage_cache"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


NEWS_COLUMNS = [
    "ticker",
    "company",
    "year",
    "published_at",
    "title",
    "summary",
    "source",
    "url",
    "ticker_sentiment_score",
    "ticker_sentiment_label",
    "relevance_score",
    "overall_sentiment_score",
    "overall_sentiment_label",
    "topics",
]


def fetch_news_for_ticker_year(ticker, company, year):
    cache_path = CACHE_DIR / f"alpha_vantage_news_{ticker}_{year}.csv"

    if cache_path.exists():
        print(f"Using saved file for {ticker} in {year}")
        cached_df = pd.read_csv(cache_path)
        return cached_df.to_dict("records"), False

    time_from = f"{year}0101T0000"
    time_to = f"{year}1231T2359"

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "time_from": time_from,
        "time_to": time_to,
        "sort": "EARLIEST",
        "limit": 1000,
        "apikey": API_KEY,
    }

    print(f"Collecting news for {ticker} ({company}) in {year}...")

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if "Information" in data:
        print("API information message:")
        print(data["Information"])
        return [], True

    if "Note" in data:
        print("API limit note:")
        print(data["Note"])
        return [], True

    if "Error Message" in data:
        print("API error message:")
        print(data["Error Message"])
        return [], True

    articles = data.get("feed", [])
    rows = []

    for article in articles:
        ticker_sentiments = article.get("ticker_sentiment", [])

        for item in ticker_sentiments:
            if item.get("ticker") == ticker:
                rows.append({
                    "ticker": ticker,
                    "company": company,
                    "year": year,
                    "published_at": article.get("time_published"),
                    "title": article.get("title"),
                    "summary": article.get("summary"),
                    "source": article.get("source"),
                    "url": article.get("url"),
                    "ticker_sentiment_score": item.get("ticker_sentiment_score"),
                    "ticker_sentiment_label": item.get("ticker_sentiment_label"),
                    "relevance_score": item.get("relevance_score"),
                    "overall_sentiment_score": article.get("overall_sentiment_score"),
                    "overall_sentiment_label": article.get("overall_sentiment_label"),
                    "topics": json.dumps(article.get("topics", [])),
                })

    cache_df = pd.DataFrame(rows, columns=NEWS_COLUMNS)
    cache_df.to_csv(cache_path, index=False)

    print(f"Articles collected: {len(rows)}")
    print(f"Saved cache file: {cache_path}")

    return rows, True


all_rows = []
request_count = 0

for ticker, company in TICKERS.items():
    for year in YEARS:
        if request_count >= MAX_REQUESTS_THIS_RUN:
            print("\nStopping here for today to avoid using too many API requests.")
            print("Run this script again later and it will continue using the saved files.")
            break

        rows, used_request = fetch_news_for_ticker_year(ticker, company, year)
        all_rows.extend(rows)

        if used_request:
            request_count += 1
            time.sleep(5)

    if request_count >= MAX_REQUESTS_THIS_RUN:
        break


news_df = pd.DataFrame(all_rows, columns=NEWS_COLUMNS)

if not news_df.empty:
    news_df["published_at"] = pd.to_datetime(
        news_df["published_at"],
        format="%Y%m%dT%H%M%S",
        errors="coerce",
    )

    news_df["date"] = news_df["published_at"].dt.date
    news_df["date"] = pd.to_datetime(news_df["date"])

    numeric_columns = [
        "ticker_sentiment_score",
        "relevance_score",
        "overall_sentiment_score",
    ]

    for column in numeric_columns:
        news_df[column] = pd.to_numeric(news_df[column], errors="coerce")


output_path = RAW_DIR / "alpha_vantage_news_2023_2025.csv"
news_df.to_csv(output_path, index=False)

print("\nFinished collecting news data.")
print(f"New API requests used in this run: {request_count}")
print(f"Saved final file: {output_path}")

print("\nDataset shape:")
print(news_df.shape)

print("\nPreview:")
print(news_df.head())

print("\nColumns:")
print(news_df.columns.tolist())

if not news_df.empty:
    print("\nArticles by ticker:")
    print(news_df["ticker"].value_counts())

    print("\nArticles by year:")
    print(news_df["year"].value_counts().sort_index())

    print("\nTicker sentiment labels:")
    print(news_df["ticker_sentiment_label"].value_counts())