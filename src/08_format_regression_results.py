from pathlib import Path
import pandas as pd

INPUT_PATH = Path("outputs/tables/combined_main_regression_results.csv")
OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading combined regression results...")
results = pd.read_csv(INPUT_PATH)
print("Raw results loaded.")
print(results)

# 1. Make variable names readable
variable_labels = {
    "neg_earnings": "Negative earnings news",
    "neg_growth": "Negative growth news",
    "neg_regulation": "Negative regulation news",
    "neg_competition": "Negative competition news",
    "neg_macro": "Negative macro news"
}

results["variable_label"] = results["variable"].map(variable_labels)

# 2. Add significance stars

def significance_stars(p_value):
    if p_value < 0.01:
        return "***"
    elif p_value < 0.05:
        return "**"
    elif p_value < 0.10:
        return "*"
    else:
        return ""


results["stars"] = results["p_value"].apply(significance_stars)

# 3. Format coefficients
# Returns are in decimal form. Example: -0.0036 means -0.36 percentage points.
# For return outcomes, we multiply by 100.
# For log volume, we keep the coefficient as it is.

def format_coefficient(row):
    coefficient = row["coefficient"]
    stars = row["stars"]
    outcome = row["outcome"]

    if outcome in ["Daily return", "Next-day return"]:
        formatted_value = coefficient * 100
        return f"{formatted_value:.3f}{stars}"
    else:
        return f"{coefficient:.3f}{stars}"


results["formatted_coefficient"] = results.apply(format_coefficient, axis=1)


# 4. Create a clean table for the report

formatted_table = results.pivot(
    index="variable_label",
    columns="outcome",
    values="formatted_coefficient"
).reset_index()

# Put variables in a logical order.
order = [
    "Negative earnings news",
    "Negative growth news",
    "Negative regulation news",
    "Negative competition news",
    "Negative macro news"
]

formatted_table["order"] = formatted_table["variable_label"].apply(lambda x: order.index(x))
formatted_table = formatted_table.sort_values("order").drop(columns="order")

# Rename first column.
formatted_table = formatted_table.rename(columns={
    "variable_label": "Negative news category"
})


# 5. Save formatted table

output_path = OUTPUT_DIR / "formatted_regression_results.csv"
formatted_table.to_csv(output_path, index=False)

print("\nFormatted regression table saved to:")
print(output_path)

print("\nFormatted table:")
print(formatted_table)

# 6. Save interpretation helper table

interpretation_table = results[
    [
        "outcome",
        "variable_label",
        "coefficient",
        "std_error",
        "p_value",
        "stars"
    ]
].copy()

interpretation_table["coefficient_percent_for_returns"] = interpretation_table.apply(
    lambda row: row["coefficient"] * 100
    if row["outcome"] in ["Daily return", "Next-day return"]
    else None,
    axis=1
)

interpretation_output_path = OUTPUT_DIR / "regression_interpretation_helper.csv"
interpretation_table.to_csv(interpretation_output_path, index=False)

print("\nInterpretation helper table saved to:")
print(interpretation_output_path)

print("\nRegression formatting completed successfully.")