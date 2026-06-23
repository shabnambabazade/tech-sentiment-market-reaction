from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf

INPUT_PATH = Path("data/processed/final_analysis_dataset_2023_2025.csv")
TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

print("Loading final analysis dataset...")

df = pd.read_csv(INPUT_PATH)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["date_fe"] = df["date"].astype(str)

print("Data loaded.")
print("Shape:", df.shape)

# These are our main explanatory variables:
# each variable counts how many negative news articles of that type appeared for a firm-day.
news_variables = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro"
]

# We keep only rows where key outcome variables are available.

regression_df = df.dropna(
    subset=[
        "daily_return",
        "next_day_return",
        "log_volume"
    ] + news_variables
).copy()

print("Regression sample shape:", regression_df.shape)

# Helper function for running regressions

def run_regression(outcome_variable, output_name):
    """
    Runs an OLS regression with firm fixed effects and date fixed effects.

    The model is:
    outcome = negative news categories + firm fixed effects + date fixed effects
    """

    formula = (
        f"{outcome_variable} ~ "
        f"neg_earnings + neg_growth + neg_regulation + neg_competition + neg_macro "
        f"+ C(ticker) + C(date_fe)"
    )

    print(f"\nRunning regression for: {outcome_variable}")

    model = smf.ols(
        formula=formula,
        data=regression_df
    ).fit(cov_type="HC1")

    print(model.summary())

    # Save only the main coefficients we care about.
    results_table = pd.DataFrame({
        "variable": model.params.index,
        "coefficient": model.params.values,
        "std_error": model.bse.values,
        "t_stat": model.tvalues.values,
        "p_value": model.pvalues.values
    })

    main_results = results_table[
        results_table["variable"].isin(news_variables)
    ].copy()

    output_path = TABLES_DIR / output_name
    main_results.to_csv(output_path, index=False)

    print(f"\nSaved main regression results to: {output_path}")

    return model, main_results

# Main regressions

daily_return_model, daily_return_results = run_regression(
    outcome_variable="daily_return",
    output_name="regression_daily_return.csv"
)

next_day_return_model, next_day_return_results = run_regression(
    outcome_variable="next_day_return",
    output_name="regression_next_day_return.csv"
)

log_volume_model, log_volume_results = run_regression(
    outcome_variable="log_volume",
    output_name="regression_log_volume.csv"
)

# Create one combined table for easier reporting

daily_return_results["outcome"] = "Daily return"
next_day_return_results["outcome"] = "Next-day return"
log_volume_results["outcome"] = "Log trading volume"

combined_results = pd.concat(
    [
        daily_return_results,
        next_day_return_results,
        log_volume_results
    ],
    ignore_index=True
)

combined_output_path = TABLES_DIR / "combined_main_regression_results.csv"
combined_results.to_csv(combined_output_path, index=False)

print("\nCombined regression table saved to:")
print(combined_output_path)

print("\nCombined main results:")
print(combined_results)

print("\nRegression analysis completed successfully.")