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


# Figure 1: negative category counts
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


print("\nFigures saved to:")
print(FIGURE_DIR)

print("\nCreated files:")
for path in sorted(FIGURE_DIR.glob("figure_*.png")):
    print(path)
