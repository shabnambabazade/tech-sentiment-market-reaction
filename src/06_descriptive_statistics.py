from pathlib import Path
import pandas as pd


DATA_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
TABLE_DIR = Path("outputs/tables")

TABLE_DIR.mkdir(parents=True, exist_ok=True)


print("Loading final analysis dataset...")
panel = pd.read_csv(DATA_PATH)

panel["date"] = pd.to_datetime(panel["date"], errors="coerce")


category_columns = [
    "neg_earnings_guidance",
    "neg_demand_growth",
    "neg_legal_regulatory",
    "neg_product_technology",
    "neg_strategy_management",
    "neg_competition_pressure",
]

category_labels = {
    "neg_earnings_guidance": "Earnings/guidance events",
    "neg_demand_growth": "Demand/growth events",
    "neg_legal_regulatory": "Legal/regulatory events",
    "neg_product_technology": "Product/technology problems",
    "neg_strategy_management": "Strategy/management changes",
    "neg_competition_pressure": "Competition pressure",
}


print("\nDataset shape:")
print(panel.shape)

print("\nDate range:")
print(panel["date"].min(), "to", panel["date"].max())

print("\nObservations by ticker:")
print(panel["ticker"].value_counts().sort_index())


sample_summary = pd.DataFrame({
    "item": [
        "Firm-day observations",
        "Number of firms",
        "Trading days per firm",
        "Total counted articles",
        "Negative articles",
        "Negative-news firm-days",
    ],
    "value": [
        len(panel),
        panel["ticker"].nunique(),
        int(panel.groupby("ticker")["date"].nunique().median()),
        int(panel["article_count"].sum()),
        int(panel["negative_article_count"].sum()),
        int(panel["has_negative_news"].sum()),
    ],
})

sample_summary.to_csv(TABLE_DIR / "sample_summary_12_firms.csv", index=False)


firm_summary = (
    panel
    .groupby(["ticker", "company", "firm_group"], as_index=False)
    .agg(
        firm_days=("date", "count"),
        articles=("article_count", "sum"),
        negative_articles=("negative_article_count", "sum"),
        negative_news_days=("has_negative_news", "sum"),
        average_daily_return=("daily_return", "mean"),
        average_log_volume=("log_volume", "mean"),
    )
)

firm_summary["average_daily_return_pct"] = firm_summary["average_daily_return"] * 100
firm_summary.to_csv(TABLE_DIR / "firm_summary_12_firms.csv", index=False)


category_summary = []

for column in category_columns:
    category_summary.append({
        "category": category_labels[column],
        "column": column,
        "article_count": int(panel[column].sum()),
        "firm_days_with_category": int((panel[column] > 0).sum()),
    })

category_summary = pd.DataFrame(category_summary)
category_summary.to_csv(TABLE_DIR / "negative_category_counts_12_firms.csv", index=False)


descriptive_vars = [
    "daily_return",
    "next_day_return",
    "log_volume",
    "article_count",
    "negative_article_count",
] + category_columns

descriptive_stats = panel[descriptive_vars].describe().T
descriptive_stats.to_csv(TABLE_DIR / "descriptive_statistics_12_firms.csv")


print("\nSample summary:")
print(sample_summary)

print("\nFirm summary:")
print(firm_summary)

print("\nNegative category counts:")
print(category_summary)

print("\nDescriptive statistics saved to outputs/tables/")
