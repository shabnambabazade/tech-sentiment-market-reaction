# Tech Sentiment Market Reaction

## Project Overview

This repository contains the code and documentation for our Media Economics research project.

The project looks at how different types of negative financial news are related to short-term stock market reactions. Our main idea is that negative news should not be treated as one single category. For example, investors may react differently to negative news about earnings than to negative news about regulation, competition, growth expectations, or broader macroeconomic conditions.

For this reason, we classify negative financial news into several topic groups and compare how these groups are associated with stock returns and trading volume.

## Research Question

Our research question is:

Which dimensions of negative financial news sentiment are most strongly associated with short-term stock returns and trading volume of large technology firms?

## Sample

The project focuses on six large technology firms:

| Company | Ticker |
|---|---|
| Apple | AAPL |
| Microsoft | MSFT |
| Nvidia | NVDA |
| Alphabet | GOOGL |
| Amazon | AMZN |
| Meta | META |

The sample period is 2023–2025.

The unit of observation is the firm-day.

## Data Sources

We use two main data sources.

First, we collect ticker-specific financial news sentiment data from the Alpha Vantage News Sentiment API. This data includes article-level information such as publication date, source, ticker-specific sentiment label, sentiment score, relevance score, and news topics.

Second, we collect daily stock market data from Yahoo Finance using the Python package yfinance. This data includes daily stock prices and trading volume.

## Main Variables

The main outcome variables are:

- daily stock return
- next-day stock return
- log trading volume

The main explanatory variables are counts of negative news articles by category:

- neg_earnings
- neg_growth
- neg_regulation
- neg_competition
- neg_macro

We define negative news using Alpha Vantage ticker-specific sentiment labels. Articles labelled as Bearish or Somewhat-Bearish are treated as negative.

## News Categories

After identifying negative articles, we classify them into five topic categories using keyword-based rules:

- earnings-related negative news
- growth-related negative news
- regulation-related negative news
- competition-related negative news
- macroeconomic negative news

This allows us to move beyond the general question of whether negative sentiment matters and instead ask which type of negative sentiment matters more.

## Method

The workflow follows these main steps:

1. collect daily stock data;
2. collect ticker-specific news sentiment data;
3. identify negative news articles;
4. classify negative news into topic categories;
5. aggregate article-level news data to the firm-day level;
6. merge the firm-day news data with stock market data;
7. estimate regression models with firm fixed effects and date fixed effects;
8. export tables and figures for the report and presentation.

The main regression relates stock market outcomes to the different negative news categories while controlling for firm fixed effects and date fixed effects.

The results should be interpreted as associations, not causal effects.

## Software Requirements

The required Python packages are listed in requirements.txt.

Main packages used in the project include:

- pandas
- numpy
- requests
- python-dotenv
- yfinance
- matplotlib
- statsmodels
- scikit-learn
- vaderSentiment

## Reproduction Steps

To reproduce the results, first create and activate a virtual environment:

python3 -m venv .venv

source .venv/bin/activate

Then install the required packages:

pip install -r requirements.txt

The Alpha Vantage API key should be stored in a local .env file:

ALPHA_VANTAGE_API_KEY=your_api_key_here

The real .env file is not included in the GitHub repository.

Run the scripts in the following order:

python src/00_test_environment.py

python src/01_collect_stock_data.py

python src/02_collect_alpha_vantage_news.py

python src/03_create_negative_news_categories.py

python src/04_create_firm_day_news_dataset.py

python src/05_merge_stock_and_news.py

python src/06_descriptive_statistics.py

python src/07_regression_analysis.py

python src/08_format_regression_results.py

python src/10_create_results_figures.py

## Main Outputs

The final analysis dataset is saved as:

data/processed/final_analysis_dataset_2023_2025.csv

Main output tables are saved in:

outputs/tables/

Main figures are saved in:

outputs/figures/

The most important result files are:

- outputs/tables/formatted_regression_results.csv
- outputs/tables/combined_main_regression_results.csv
- outputs/tables/descriptive_statistics.csv
- outputs/figures/fig_1_negative_news_category_counts.png
- outputs/figures/fig_4_regression_coefficients_daily_return.png
- outputs/figures/fig_5_regression_coefficients_next_day_return.png

## Preliminary Findings

The preliminary results suggest that not all types of negative financial news are associated with market outcomes in the same way.

The main findings are:

- earnings-related negative news is associated with lower same-day stock returns;
- growth-related negative news is associated with lower next-day stock returns;
- the evidence for trading volume is weaker than the evidence for stock returns.

Overall, the results suggest that separating negative financial news by topic can provide more information than using one general negative sentiment measure.

## Known Limitations

There are several limitations.

First, the topic classification is based on keyword rules. This approach is transparent and reproducible, but it may not capture the full meaning of every article.

Second, the news-firm link relies on Alpha Vantage ticker-specific sentiment data.

Third, the analysis is associational. We do not make causal claims.

Fourth, the sample only includes six large technology firms, so the results may not generalize to all firms or industries.

## Repository Structure

tech-sentiment-market-reaction/
README.md
requirements.txt
.env.example
.gitignore
src/
data/
outputs/
docs/
replication/
