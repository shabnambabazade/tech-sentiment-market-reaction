# Data Documentation

This document explains the data used in our project and how we constructed the final dataset for the analysis.

Our project combines financial news sentiment data with daily stock market data. The final dataset is organized at the firm-day level, which means that each row represents one company on one trading day.

## 1. Research Design

The main goal of the project is to study whether different types of negative financial news are associated with short-term market reactions.

The unit of observation is:

firm x trading day

For each selected firm and each trading day, we observe stock market outcomes and news-related variables.

## 2. Firms in the Sample

The project focuses on six large technology firms:

| Company | Ticker |
|---|---|
| Apple | AAPL |
| Microsoft | MSFT |
| Nvidia | NVDA |
| Alphabet | GOOGL |
| Amazon | AMZN |
| Meta | META |

These firms were selected because they are large, publicly traded technology companies and receive frequent financial news coverage.

## 3. Time Period

The analysis covers the period:

2023-2025

This period was chosen because it provides recent data and enough news observations for comparing different types of negative sentiment.

## 4. Data Sources

We use two main data sources.

### News Data

News sentiment data is collected from the Alpha Vantage News Sentiment API.

The news data includes ticker-specific sentiment labels, sentiment scores, relevance scores, publication dates, sources, and news topics.

We use ticker-specific sentiment information because the analysis is conducted at the firm level.

### Stock Market Data

Stock market data is collected from Yahoo Finance using the Python package `yfinance`.

The stock data includes daily stock prices, adjusted closing prices, and trading volume.

Adjusted closing prices are used to calculate daily stock returns.

## 5. Outcome Variables

The main outcome variables are daily stock return, next-day stock return, and log trading volume.

Daily stock return measures the stock price change on the same trading day.

Next-day stock return measures the stock return on the following trading day. We include this variable because some market reactions may happen with a short delay.

Trading volume is transformed into log trading volume because trading volume can be very large and highly skewed.

## 6. Negative News Definition

Negative news is identified using Alpha Vantage ticker-specific sentiment labels.

The following labels are treated as negative:

- Bearish
- Somewhat-Bearish

These labels are used because they refer to the sentiment of the article with respect to a specific ticker.

## 7. Negative News Categories

After identifying negative articles, we classify them into five topic categories using keyword-based rules.

The five main categories are:

- earnings
- growth
- regulation
- competition
- macroeconomic news

Negative articles that do not match any of these five categories are classified as `neg_other`.

## 8. Aggregation to Firm-Day Level

The original news data is collected at the article level.

Since the stock market data is daily, we aggregate the article-level news data to the firm-day level.

For each firm and trading day, we count:

- total number of articles
- total number of negative articles
- number of negative earnings-related articles
- number of negative growth-related articles
- number of negative regulation-related articles
- number of negative competition-related articles
- number of negative macro-related articles
- number of negative articles that do not match the main categories

This gives us one row per firm per trading day.

## 9. Date Alignment

Stock market data only exists for trading days. Some news articles may be published on weekends or holidays.

If a news article is published on a non-trading day, it is aligned to the next available trading day for the same ticker.

This allows us to connect news information to the closest available stock market reaction.

## 10. Final Dataset

The final analysis dataset is:

data/processed/final_analysis_dataset_2023_2025.csv

This dataset combines the firm-day news variables with the firm-day stock market variables.

Main variables in the final dataset include:

- ticker
- company
- date
- daily_return
- next_day_return
- log_volume
- article_count
- negative_article_count
- neg_earnings
- neg_growth
- neg_regulation
- neg_competition
- neg_macro
- neg_other

## 11. Data Availability Note

Raw article-level news files are not included in the public GitHub repository because the raw news data may contain article titles and summaries from external sources.

The raw data can be reproduced by running the Alpha Vantage collection script with a valid API key.

The repository includes the code, documentation, processed datasets, output tables, and figures needed to understand and reproduce the workflow.

## 12. Data-Related Notes and Limitations

The news category classification is based on keyword rules. This makes the classification transparent and reproducible, but it may not capture the full meaning or context of every article.

The link between news articles and firms relies on Alpha Vantage ticker-specific sentiment data. Since this matching is provided by the API, we use it as the basis for connecting articles to firms.

The public repository does not include raw article-level news files. Instead, it includes the scripts and documentation needed to reproduce the data collection process.
