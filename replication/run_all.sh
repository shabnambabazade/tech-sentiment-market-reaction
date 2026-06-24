#!/bin/bash

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
