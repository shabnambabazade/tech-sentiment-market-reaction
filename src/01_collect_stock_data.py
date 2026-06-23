from pathlib import Path
import math
import pandas as pd
import yfinance as yf

TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta"
}
START_DATE = "2023-01-01"
END_DATE = "2026-01-01"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Downloading stock data from Yahoo Finance...")

stock_data = yf.download(
    tickers=list(TICKERS.keys()),
    start=START_DATE,
    end=END_DATE,
    auto_adjust=False,
    progress=True
)

raw_path = RAW_DIR / "stock_data_raw_2023_2025.csv"
stock_data.to_csv(raw_path)

print(f"Raw stock data saved to: {raw_path}")

print("Cleaning stock data...")

stock_long = stock_data.stack(level=1).reset_index()

stock_long = stock_long.rename(columns={
    "Date": "date",
    "Ticker": "ticker",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume"
})

stock_long["company"] = stock_long["ticker"].map(TICKERS)
stock_long["date"] = pd.to_datetime(stock_long["date"])
stock_long = stock_long.sort_values(["ticker", "date"])

stock_long["daily_return"] = stock_long.groupby("ticker")["adj_close"].pct_change()
stock_long["next_day_return"] = stock_long.groupby("ticker")["daily_return"].shift(-1)

stock_long["log_volume"] = stock_long["volume"].apply(
    lambda x: math.log(x) if pd.notna(x) and x > 0 else None
)

processed_path = PROCESSED_DIR / "stock_data_processed_2023_2025.csv"
stock_long.to_csv(processed_path, index=False)

print(f"Processed stock data saved to: {processed_path}")

print("\nPreview:")
print(stock_long.head())

print("\nDataset shape:")
print(stock_long.shape)

print("\nColumns:")
print(stock_long.columns.tolist())

print("\nDate range:")
print(stock_long["date"].min(), "to", stock_long["date"].max())

print("\nObservations by ticker:")
print(stock_long["ticker"].value_counts())