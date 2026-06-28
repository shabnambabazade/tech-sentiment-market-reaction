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

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_news_for_ticker_year(ticker, company, year):
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
        "apikey": API_KEY
    }

    print(f"Collecting news for {ticker} ({company}) in {year}...")

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if "Information" in data:
        print("API information message:")
        print(data["Information"])
        return []

    if "Note" in data:
        print("API limit note:")
        print(data["Note"])
        return []

    if "Error Message" in data:
        print("API error message:")
        print(data["Error Message"])
        return []

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
                    "topics": json.dumps(article.get("topics", []))
                })

    print(f"Articles collected: {len(rows)}")
    return rows


all_rows = []
request_count = 0

for ticker, company in TICKERS.items():
    for year in YEARS:
        rows = fetch_news_for_ticker_year(ticker, company, year)
        all_rows.extend(rows)
        request_count += 1

        # Free API has a daily request limit, so we do not send requests too fast.
        time.sleep(5)


news_df = pd.DataFrame(all_rows)

if not news_df.empty:
    news_df["published_at"] = pd.to_datetime(
        news_df["published_at"],
        format="%Y%m%dT%H%M%S",
        errors="coerce"
    )

    news_df["date"] = news_df["published_at"].dt.date
    news_df["date"] = pd.to_datetime(news_df["date"])

    numeric_columns = [
        "ticker_sentiment_score",
        "relevance_score",
        "overall_sentiment_score"
    ]

    for column in numeric_columns:
        news_df[column] = pd.to_numeric(news_df[column], errors="coerce")


output_path = RAW_DIR / "alpha_vantage_news_2023_2025.csv"
news_df.to_csv(output_path, index=False)

print("\nFinished collecting news data.")
print(f"Total API requests used: {request_count}")
print(f"Saved file: {output_path}")

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