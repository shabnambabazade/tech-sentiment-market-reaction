from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


PANEL_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
RESULTS_PATH = Path("outputs/tables/regression_results_event_categories.csv")
FIGURE_DIR = Path("outputs/figures")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)


print("Loading data for figures...")
panel = pd.read_csv(PANEL_PATH)
results = pd.read_csv(RESULTS_PATH)

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
    "neg_earnings_guidance": "Earnings/guidance",
    "neg_demand_growth": "Demand/growth",
    "neg_legal_regulatory": "Legal/regulatory",
    "neg_product_technology": "Product/technology",
    "neg_strategy_management": "Strategy/management",
    "neg_competition_pressure": "Competition pressure",
}


# Figure 1: negative event category counts
category_counts = pd.DataFrame({
    "category": [category_labels[col] for col in category_columns],
    "count": [int(panel[col].sum()) for col in category_columns],
})

category_counts = category_counts.sort_values("count", ascending=True)

plt.figure(figsize=(9, 5))
plt.barh(category_counts["category"], category_counts["count"])
plt.xlabel("Number of negative article-category observations")
plt.title("Negative news event categories")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_negative_event_category_counts.png", dpi=300)
plt.close()


# Figure 2: negative articles by firm
firm_counts = (
    panel
    .groupby(["ticker", "company", "firm_group"], as_index=False)
    .agg(negative_articles=("negative_article_count", "sum"))
    .sort_values("negative_articles", ascending=True)
)

plt.figure(figsize=(9, 5))
plt.barh(firm_counts["ticker"], firm_counts["negative_articles"])
plt.xlabel("Number of negative articles")
plt.title("Negative news by firm")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_negative_articles_by_firm.png", dpi=300)
plt.close()


# Figure 3: same-day return coefficients
same_day = results[results["model"] == "Same-day return"].copy()
same_day["label"] = same_day["variable"].map(category_labels)
same_day = same_day.sort_values("coefficient")

plt.figure(figsize=(9, 5))
plt.barh(same_day["label"], same_day["coefficient"])
plt.axvline(0, linewidth=1)
plt.xlabel("Coefficient in percentage points")
plt.title("Same-day return regression coefficients")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_same_day_return_coefficients.png", dpi=300)
plt.close()


# Figure 4: next-day return coefficients
next_day = results[results["model"] == "Next-day return"].copy()
next_day["label"] = next_day["variable"].map(category_labels)
next_day = next_day.sort_values("coefficient")

plt.figure(figsize=(9, 5))
plt.barh(next_day["label"], next_day["coefficient"])
plt.axvline(0, linewidth=1)
plt.xlabel("Coefficient in percentage points")
plt.title("Next-day return regression coefficients")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_next_day_return_coefficients.png", dpi=300)
plt.close()


# Figure 5: log trading volume coefficients
volume = results[results["model"] == "Log trading volume"].copy()
volume["label"] = volume["variable"].map(category_labels)
volume = volume.sort_values("coefficient")

plt.figure(figsize=(9, 5))
plt.barh(volume["label"], volume["coefficient"])
plt.axvline(0, linewidth=1)
plt.xlabel("Coefficient")
plt.title("Log trading volume regression coefficients")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_log_volume_coefficients.png", dpi=300)
plt.close()


# Figure 6: average same-day return by event category
average_rows = []

for column in category_columns:
    category_days = panel[panel[column] > 0].copy()

    average_rows.append({
        "category": category_labels[column],
        "average_same_day_return_pct": category_days["daily_return_pct"].mean(),
        "average_next_day_return_pct": category_days["next_day_return_pct"].mean(),
    })

average_returns = pd.DataFrame(average_rows)

same_day_avg = average_returns.sort_values("average_same_day_return_pct")

plt.figure(figsize=(9, 5))
plt.barh(same_day_avg["category"], same_day_avg["average_same_day_return_pct"])
plt.axvline(0, linewidth=1)
plt.xlabel("Average same-day return (%)")
plt.title("Average same-day return on event-category days")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_average_same_day_return_by_event_category.png", dpi=300)
plt.close()


# Figure 7: average next-day return by event category
next_day_avg = average_returns.sort_values("average_next_day_return_pct")

plt.figure(figsize=(9, 5))
plt.barh(next_day_avg["category"], next_day_avg["average_next_day_return_pct"])
plt.axvline(0, linewidth=1)
plt.xlabel("Average next-day return (%)")
plt.title("Average next-day return on event-category days")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_average_next_day_return_by_event_category.png", dpi=300)
plt.close()


# Figure 8: negative-news days versus no-negative-news days
comparison = (
    panel
    .groupby("has_negative_news", as_index=False)
    .agg(average_same_day_return_pct=("daily_return_pct", "mean"))
)

comparison["group"] = comparison["has_negative_news"].map({
    0: "No negative news",
    1: "At least one negative article",
})

plt.figure(figsize=(8, 5))
plt.bar(comparison["group"], comparison["average_same_day_return_pct"])
plt.axhline(0, linewidth=1)
plt.ylabel("Average same-day return (%)")
plt.title("Average returns on negative-news and no-negative-news days")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_negative_news_vs_no_negative_news_returns.png", dpi=300)
plt.close()


# Figure 9: article counts by firm group
group_counts = (
    panel
    .groupby("firm_group", as_index=False)
    .agg(
        total_articles=("article_count", "sum"),
        negative_articles=("negative_article_count", "sum"),
    )
)

plt.figure(figsize=(8, 5))
plt.bar(group_counts["firm_group"], group_counts["negative_articles"])
plt.ylabel("Number of negative articles")
plt.title("Negative articles by firm group")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_articles_by_firm_group.png", dpi=300)
plt.close()


# Figure 10: event categories by firm group
group_category_rows = []

for group_name, group_data in panel.groupby("firm_group"):
    for column in category_columns:
        group_category_rows.append({
            "firm_group": group_name,
            "category": category_labels[column],
            "count": int(group_data[column].sum()),
        })

group_category_counts = pd.DataFrame(group_category_rows)

pivot = group_category_counts.pivot(
    index="category",
    columns="firm_group",
    values="count",
).fillna(0)

pivot = pivot.sort_values(by=pivot.columns.tolist(), ascending=True)

plt.figure(figsize=(10, 6))
pivot.plot(kind="barh", figsize=(10, 6))
plt.xlabel("Number of negative article-category observations")
plt.title("Event-category counts by firm group")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "figure_event_categories_by_firm_group.png", dpi=300)
plt.close()


print("\nFigures saved to:")
print(FIGURE_DIR)

print("\nCreated files:")
for path in sorted(FIGURE_DIR.glob("figure_*.png")):
    print(path)
