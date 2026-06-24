# Workflow Instructions

This document explains how we organized and reproduced the analysis for this project.

The project combines stock market data with ticker-specific financial news sentiment data. The workflow starts with data collection, continues with cleaning and news classification, and ends with regression analysis and output generation.

## 1. Environment Setup

Before running the scripts, create a Python virtual environment:

python3 -m venv .venv

Then activate it:

source .venv/bin/activate

After activating the environment, install the required packages:

pip install -r requirements.txt

The required packages are listed in `requirements.txt`.

## 2. API Key Setup

The news data is collected from the Alpha Vantage News Sentiment API. To run the news collection script, a valid Alpha Vantage API key is required.

Create a local `.env` file in the main project folder and add the API key in this format:

ALPHA_VANTAGE_API_KEY=your_api_key_here

The real `.env` file is not included in the GitHub repository because it contains a private API key.

A template file named `.env.example` is included to show the required format.

## 3. Script Order

The scripts should be run in the order below. Each script creates an output that is used by the next step.

### Step 1: Test the environment

python src/00_test_environment.py

This script checks whether the required packages and the API key are loaded correctly.

### Step 2: Collect stock data

python src/01_collect_stock_data.py

This script downloads daily stock prices and trading volume for the firms in the sample. It also creates daily returns, next-day returns, and log trading volume.

### Step 3: Collect news sentiment data

python src/02_collect_alpha_vantage_news.py

This script collects ticker-specific financial news sentiment data from Alpha Vantage for the selected firms and years.

### Step 4: Create negative news categories

python src/03_create_negative_news_categories.py

This script identifies negative articles and classifies them into topic categories such as earnings, growth, regulation, competition, and macroeconomic news.

### Step 5: Aggregate news to the firm-day level

python src/04_create_firm_day_news_dataset.py

This script turns article-level news data into firm-day news variables. For example, it counts how many negative earnings-related articles appear for a firm on a given day.

### Step 6: Merge news and stock data

python src/05_merge_stock_and_news.py

This script merges the firm-day news variables with the daily stock market data.

### Step 7: Create descriptive statistics

python src/06_descriptive_statistics.py

This script creates summary statistics, category counts, and descriptive comparison tables.

### Step 8: Run regression analysis

python src/07_regression_analysis.py

This script estimates the main regression models using firm fixed effects and date fixed effects.

### Step 9: Format regression results

python src/08_format_regression_results.py

This script formats the regression output into cleaner tables for the paper and presentation.

### Step 10: Create figures

python src/10_create_results_figures.py

This script creates the main figures used to present the descriptive patterns and regression results.

## 4. Output Locations

The main processed datasets are saved in:

data/processed/

The output tables are saved in:

outputs/tables/

The output figures are saved in:

outputs/figures/

## 5. Main Files Produced by the Workflow

The final analysis dataset is:

data/processed/final_analysis_dataset_2023_2025.csv

The main formatted regression table is:

outputs/tables/formatted_regression_results.csv

The main figures are:

outputs/figures/fig_1_negative_news_category_counts.png
outputs/figures/fig_4_regression_coefficients_daily_return.png
outputs/figures/fig_5_regression_coefficients_next_day_return.png

## 6. Notes

Raw article-level news files are not included in the public repository. They can be reproduced by running the Alpha Vantage collection script with a valid API key.

The results should be interpreted as associations rather than causal effects.
