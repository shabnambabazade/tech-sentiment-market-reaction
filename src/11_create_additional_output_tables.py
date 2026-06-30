from pathlib import Path
import pandas as pd


PANEL_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
REGRESSION_PATH = Path("outputs/tables/regression_results_event_categories.csv")
TABLE_DIR = Path("outputs/tables")

TABLE_DIR.mkdir(parents=True, exist_ok=True)


print("Loading final panel and regression results...")
panel = pd.read_csv(PANEL_PATH)
regression = pd.read_csv(REGRESSION_PATH)

panel["date"] = pd.to_datetime(panel["date"], errors="coerce")

panel["daily_return_pct"] = panel["daily_return"] * 100
panel["next_day_return_pct"] = panel["next_day_return"] * 100


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


# 1. Average outcomes for firm-days with each event category
average_rows = []

for column in category_columns:
    category_days = panel[panel[column] > 0].copy()

    average_rows.append({
        "category": category_labels[column],
        "column": column,
        "category_article_count": int(panel[column].sum()),
        "firm_days_with_category": int((panel[column] > 0).sum()),
        "average_same_day_return_pct": category_days["daily_return_pct"].mean(),
        "average_next_day_return_pct": category_days["next_day_return_pct"].mean(),
        "average_log_volume": category_days["log_volume"].mean(),
    })

average_outcomes = pd.DataFrame(average_rows)
average_outcomes.to_csv(
    TABLE_DIR / "average_outcomes_by_event_category_12_firms.csv",
    index=False,
)


# 2. Negative-news days versus no-negative-news days
news_comparison = (
    panel
    .groupby("has_negative_news", as_index=False)
    .agg(
        firm_days=("date", "count"),
        average_same_day_return_pct=("daily_return_pct", "mean"),
        average_next_day_return_pct=("next_day_return_pct", "mean"),
        average_log_volume=("log_volume", "mean"),
        total_articles=("article_count", "sum"),
        total_negative_articles=("negative_article_count", "sum"),
    )
)

news_comparison["group"] = news_comparison["has_negative_news"].map({
    0: "No negative news",
    1: "At least one negative article",
})

news_comparison = news_comparison[
    [
        "group",
        "firm_days",
        "average_same_day_return_pct",
        "average_next_day_return_pct",
        "average_log_volume",
        "total_articles",
        "total_negative_articles",
    ]
]

news_comparison.to_csv(
    TABLE_DIR / "negative_news_vs_no_negative_news_12_firms.csv",
    index=False,
)


# 3. Firm group summary
firm_group_summary = (
    panel
    .groupby("firm_group", as_index=False)
    .agg(
        firm_days=("date", "count"),
        firms=("ticker", "nunique"),
        total_articles=("article_count", "sum"),
        negative_articles=("negative_article_count", "sum"),
        negative_news_days=("has_negative_news", "sum"),
        average_same_day_return_pct=("daily_return_pct", "mean"),
        average_log_volume=("log_volume", "mean"),
    )
)

firm_group_summary.to_csv(
    TABLE_DIR / "firm_group_summary_12_firms.csv",
    index=False,
)


# 4. Event categories by firm group
group_category_rows = []

for group_name, group_data in panel.groupby("firm_group"):
    for column in category_columns:
        group_category_rows.append({
            "firm_group": group_name,
            "category": category_labels[column],
            "column": column,
            "category_article_count": int(group_data[column].sum()),
            "firm_days_with_category": int((group_data[column] > 0).sum()),
        })

event_by_group = pd.DataFrame(group_category_rows)
event_by_group.to_csv(
    TABLE_DIR / "event_category_counts_by_firm_group_12_firms.csv",
    index=False,
)


# 5. Separate regression tables by model
model_file_names = {
    "Same-day return": "regression_same_day_return_event_categories.csv",
    "Next-day return": "regression_next_day_return_event_categories.csv",
    "Log trading volume": "regression_log_volume_event_categories.csv",
}

for model_name, file_name in model_file_names.items():
    model_table = regression[regression["model"] == model_name].copy()
    model_table.to_csv(TABLE_DIR / file_name, index=False)


# 6. Interpretation helper table
helper_rows = []

for column in category_columns:
    category_name = category_labels[column]

    same_day = regression[
        (regression["variable"] == column)
        & (regression["model"] == "Same-day return")
    ].iloc[0]

    next_day = regression[
        (regression["variable"] == column)
        & (regression["model"] == "Next-day return")
    ].iloc[0]

    volume = regression[
        (regression["variable"] == column)
        & (regression["model"] == "Log trading volume")
    ].iloc[0]

    helper_rows.append({
        "category": category_name,
        "article_count": int(panel[column].sum()),
        "same_day_return_coefficient": same_day["coefficient"],
        "same_day_return_p_value": same_day["p_value"],
        "same_day_return_stars": same_day["stars"],
        "next_day_return_coefficient": next_day["coefficient"],
        "next_day_return_p_value": next_day["p_value"],
        "next_day_return_stars": next_day["stars"],
        "log_volume_coefficient": volume["coefficient"],
        "log_volume_p_value": volume["p_value"],
        "log_volume_stars": volume["stars"],
    })

interpretation_helper = pd.DataFrame(helper_rows)
interpretation_helper.to_csv(
    TABLE_DIR / "regression_interpretation_helper_event_categories.csv",
    index=False,
)


print("\nAdditional detailed output tables created:")
for path in sorted(TABLE_DIR.glob("*12_firms.csv")):
    print(path)

for path in sorted(TABLE_DIR.glob("regression_*event_categories.csv")):
    print(path)

print("\nDone.")
