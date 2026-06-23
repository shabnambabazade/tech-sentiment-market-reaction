from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

INPUT_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
TABLES_DIR = Path("outputs/tables")
FIGURES_DIR = Path("outputs/figures")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print("Loading final analysis dataset...")

df = pd.read_csv(INPUT_PATH)

df["date"] = pd.to_datetime(df["date"], errors="coerce")

print("Data loaded.")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# 1. Sample overview
sample_overview = (
    df.groupby("ticker")
    .agg(
        company=("company", "first"),
        first_date=("date", "min"),
        last_date=("date", "max"),
        observations=("date", "count"),
        negative_news_days=("negative_article_count", lambda x: (x > 0).sum()),
        total_negative_articles=("negative_article_count", "sum")
    )
    .reset_index()
)

sample_overview_path = TABLES_DIR / "sample_overview.csv"
sample_overview.to_csv(sample_overview_path, index=False)

print("\nSample overview:")
print(sample_overview)

# 2. Descriptive statistics
variables_for_summary = [
    "daily_return",
    "next_day_return",
    "log_volume",
    "article_count",
    "negative_article_count",
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

descriptive_stats = df[variables_for_summary].describe().T

descriptive_stats_path = TABLES_DIR / "descriptive_statistics.csv"
descriptive_stats.to_csv(descriptive_stats_path)

print("\nDescriptive statistics:")
print(descriptive_stats)


# 3. Negative news category counts
category_columns = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

category_counts = pd.DataFrame({
    "category": category_columns,
    "count": [int(df[col].sum()) for col in category_columns]
})

category_counts_path = TABLES_DIR / "negative_news_category_counts.csv"
category_counts.to_csv(category_counts_path, index=False)

print("\nNegative news category counts:")
print(category_counts)


# 4. Average market outcomes by negative news category
comparison_rows = []

for category in category_columns:
    subset = df[df[category] > 0]

    comparison_rows.append({
        "category": category,
        "firm_days_with_category": len(subset),
        "avg_daily_return_percent": subset["daily_return"].mean() * 100,
        "avg_next_day_return_percent": subset["next_day_return"].mean() * 100,
        "avg_log_volume": subset["log_volume"].mean()
    })

category_comparison = pd.DataFrame(comparison_rows)

category_comparison_path = TABLES_DIR / "average_outcomes_by_negative_news_category.csv"
category_comparison.to_csv(category_comparison_path, index=False)

print("\nAverage outcomes by negative news category:")
print(category_comparison)

# 5. Baseline comparison: negative news days vs no negative news days
df["has_negative_news"] = (df["negative_article_count"] > 0).astype(int)

negative_vs_no_news = (
    df.groupby("has_negative_news")
    .agg(
        observations=("date", "count"),
        avg_daily_return_percent=("daily_return", lambda x: x.mean() * 100),
        avg_next_day_return_percent=("next_day_return", lambda x: x.mean() * 100),
        avg_log_volume=("log_volume", "mean")
    )
    .reset_index()
)

negative_vs_no_news["group"] = negative_vs_no_news["has_negative_news"].map({
    0: "No negative news",
    1: "At least one negative news article"
})

negative_vs_no_news_path = TABLES_DIR / "negative_news_vs_no_negative_news.csv"
negative_vs_no_news.to_csv(negative_vs_no_news_path, index=False)

print("\nNegative news days vs no negative news days:")
print(negative_vs_no_news)

# 6. Figure: negative news category counts
plt.figure(figsize=(9, 5))
plt.bar(category_counts["category"], category_counts["count"])
plt.title("Negative news articles by category")
plt.xlabel("Negative news category")
plt.ylabel("Number of classified articles")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

figure_path = FIGURES_DIR / "negative_news_by_category.png"
plt.savefig(figure_path, dpi=300)
plt.close()

print("\nFigure saved to:")
print(figure_path)
print("\nAll descriptive outputs were created successfully.")