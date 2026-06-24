# Progress Notes

This document records the main steps completed during the project.

## Project Setup

We created the project folder structure, set up a Python environment, added the required packages, and prepared the repository for GitHub.

## Data Collection

We collected daily stock market data for Apple, Microsoft, Nvidia, Alphabet, Amazon, and Meta using Yahoo Finance through `yfinance`.

We also collected ticker-specific financial news sentiment data from the Alpha Vantage News Sentiment API for the period 2023-2025.

## Data Processing

We calculated daily stock returns, next-day returns, and log trading volume.

We identified negative news articles using Alpha Vantage ticker sentiment labels and classified them into earnings, growth, regulation, competition, and macroeconomic categories.

The article-level news data was aggregated to the firm-day level and then merged with the stock market data.

## Analysis

We created descriptive statistics, category count tables, regression tables, and figures.

The main regressions use firm fixed effects and date fixed effects.

## Preliminary Findings

The preliminary results suggest that earnings-related negative news is associated with lower same-day returns, while growth-related negative news is associated with lower next-day returns.

The evidence for trading volume is weaker.

## Remaining Work

The remaining work is to finalize the paper, prepare the presentation slides, review the repository, and add the final GitHub link to the submission cover page.
