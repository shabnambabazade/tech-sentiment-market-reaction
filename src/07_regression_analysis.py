from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf


DATA_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
TABLE_DIR = Path("outputs/tables")

TABLE_DIR.mkdir(parents=True, exist_ok=True)


print("Loading final analysis dataset...")
panel = pd.read_csv(DATA_PATH)

panel["date"] = pd.to_datetime(panel["date"], errors="coerce")
panel["date_fe"] = panel["date"].dt.strftime("%Y-%m-%d")


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


# returns are converted to percentage points
panel["daily_return_pct"] = panel["daily_return"] * 100
panel["next_day_return_pct"] = panel["next_day_return"] * 100


def stars(p_value):
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


rhs = " + ".join(category_columns) + " + C(ticker) + C(date_fe)"

models = {
    "Same-day return": "daily_return_pct",
    "Next-day return": "next_day_return_pct",
    "Log trading volume": "log_volume",
}

all_results = []
model_summary = []

for model_name, outcome in models.items():
    model_data = panel.dropna(subset=[outcome]).copy()

    formula = f"{outcome} ~ {rhs}"

    print("\nRunning model:", model_name)
    print("Formula:", formula)
    print("Observations:", len(model_data))

    model = smf.ols(formula, data=model_data).fit(cov_type="HC1")

    model_summary.append({
        "model": model_name,
        "outcome": outcome,
        "observations": int(model.nobs),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
    })

    for column in category_columns:
        all_results.append({
            "model": model_name,
            "variable": column,
            "category": category_labels[column],
            "coefficient": model.params[column],
            "std_error": model.bse[column],
            "p_value": model.pvalues[column],
            "stars": stars(model.pvalues[column]),
            "coefficient_with_stars": f"{model.params[column]:.3f}{stars(model.pvalues[column])}",
            "std_error_formatted": f"({model.bse[column]:.3f})",
            "observations": int(model.nobs),
            "r_squared": model.rsquared,
        })


results = pd.DataFrame(all_results)
summary = pd.DataFrame(model_summary)

results.to_csv(TABLE_DIR / "regression_results_event_categories.csv", index=False)
summary.to_csv(TABLE_DIR / "regression_model_summary_event_categories.csv", index=False)


print("\nRegression results:")
print(results[[
    "model",
    "category",
    "coefficient_with_stars",
    "std_error_formatted",
    "p_value",
]])

print("\nModel summary:")
print(summary)

print("\nRegression tables saved to outputs/tables/")
