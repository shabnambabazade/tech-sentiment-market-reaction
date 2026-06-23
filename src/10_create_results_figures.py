from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

FINAL_DATA_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
REGRESSION_RESULTS_PATH = Path("outputs/tables/combined_main_regression_results.csv")

FIGURES_DIR = Path("outputs/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print("Loading data...")

df = pd.read_csv(FINAL_DATA_PATH)
reg = pd.read_csv(REGRESSION_RESULTS_PATH)

df["date"] = pd.to_datetime(df["date"], errors="coerce")

print("Data loaded.")

# Figure 1: negative news category counts

category_columns = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro"
]

category_labels = {
    "neg_earnings": "Earnings",
    "neg_growth": "Growth",
    "neg_regulation": "Regulation",
    "neg_competition": "Competition",
    "neg_macro": "Macro"
}

category_counts = pd.DataFrame({
    "category": [category_labels[col] for col in category_columns],
    "count": [df[col].sum() for col in category_columns]
})

plt.figure(figsize=(8, 5))
plt.bar(category_counts["category"], category_counts["count"])
plt.title("Negative news articles by category")
plt.xlabel("Negative news category")
plt.ylabel("Number of firm-day category counts")
plt.tight_layout()

output_path = FIGURES_DIR / "fig_1_negative_news_category_counts.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("Saved:", output_path)

# Figure 2: average daily return by category

avg_return_rows = []

for col in category_columns:
    subset = df[df[col] > 0]

    avg_return_rows.append({
        "category": category_labels[col],
        "avg_daily_return_percent": subset["daily_return"].mean() * 100
    })

avg_return_df = pd.DataFrame(avg_return_rows)

plt.figure(figsize=(8, 5))
plt.bar(avg_return_df["category"], avg_return_df["avg_daily_return_percent"])
plt.axhline(0, linewidth=1)
plt.title("Average same-day return by negative news category")
plt.xlabel("Negative news category")
plt.ylabel("Average daily return (%)")
plt.tight_layout()

output_path = FIGURES_DIR / "fig_2_average_daily_return_by_category.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("Saved:", output_path)

# Figure 3: average next-day return by category

avg_next_return_rows = []

for col in category_columns:
    subset = df[df[col] > 0]

    avg_next_return_rows.append({
        "category": category_labels[col],
        "avg_next_day_return_percent": subset["next_day_return"].mean() * 100
    })

avg_next_return_df = pd.DataFrame(avg_next_return_rows)

plt.figure(figsize=(8, 5))
plt.bar(avg_next_return_df["category"], avg_next_return_df["avg_next_day_return_percent"])
plt.axhline(0, linewidth=1)
plt.title("Average next-day return by negative news category")
plt.xlabel("Negative news category")
plt.ylabel("Average next-day return (%)")
plt.tight_layout()

output_path = FIGURES_DIR / "fig_3_average_next_day_return_by_category.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("Saved:", output_path)

# Figure 4: regression coefficients for returns
reg_return = reg[
    reg["outcome"].isin(["Daily return", "Next-day return"])
].copy()

reg_return["category"] = reg_return["variable"].map({
    "neg_earnings": "Earnings",
    "neg_growth": "Growth",
    "neg_regulation": "Regulation",
    "neg_competition": "Competition",
    "neg_macro": "Macro"
})

reg_return["coefficient_percent"] = reg_return["coefficient"] * 100

# Save a clean table too.
clean_regression_figure_data = reg_return[
    ["outcome", "category", "coefficient_percent", "p_value"]
]

clean_regression_figure_data.to_csv(
    Path("outputs/tables/regression_coefficients_for_return_figure.csv"),
    index=False
)

# Creating one figure for daily return.
daily = reg_return[reg_return["outcome"] == "Daily return"]

plt.figure(figsize=(8, 5))
plt.bar(daily["category"], daily["coefficient_percent"])
plt.axhline(0, linewidth=1)
plt.title("Regression coefficients: Same-day return")
plt.xlabel("Negative news category")
plt.ylabel("Coefficient in percentage points")
plt.tight_layout()

output_path = FIGURES_DIR / "fig_4_regression_coefficients_daily_return.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("Saved:", output_path)


# Creating one figure for next-day return.
next_day = reg_return[reg_return["outcome"] == "Next-day return"]

plt.figure(figsize=(8, 5))
plt.bar(next_day["category"], next_day["coefficient_percent"])
plt.axhline(0, linewidth=1)
plt.title("Regression coefficients: Next-day return")
plt.xlabel("Negative news category")
plt.ylabel("Coefficient in percentage points")
plt.tight_layout()

output_path = FIGURES_DIR / "fig_5_regression_coefficients_next_day_return.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("Saved:", output_path)

print("\nAll result figures were created successfully.")