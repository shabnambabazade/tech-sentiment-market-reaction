from pathlib import Path
import pandas as pd


RESULTS_PATH = Path("outputs/tables/regression_results_event_categories.csv")
SUMMARY_PATH = Path("outputs/tables/regression_model_summary_event_categories.csv")
TABLE_DIR = Path("outputs/tables")

TABLE_DIR.mkdir(parents=True, exist_ok=True)


print("Loading regression results...")
results = pd.read_csv(RESULTS_PATH)
summary = pd.read_csv(SUMMARY_PATH)


model_order = [
    "Same-day return",
    "Next-day return",
    "Log trading volume",
]

category_order = [
    "Earnings/guidance events",
    "Demand/growth events",
    "Legal/regulatory events",
    "Product/technology problems",
    "Strategy/management changes",
    "Competition pressure",
]


rows = []

for category in category_order:
    row = {"Category": category}

    for model in model_order:
        match = results[
            (results["category"] == category)
            & (results["model"] == model)
        ]

        if len(match) == 0:
            row[model] = ""
        else:
            coef = match.iloc[0]["coefficient_with_stars"]
            se = match.iloc[0]["std_error_formatted"]
            row[model] = f"{coef} {se}"

    rows.append(row)


for model in model_order:
    model_info = summary[summary["model"] == model].iloc[0]

    row_obs = {"Category": "Observations"}
    row_r2 = {"Category": "R-squared"}

    for column_model in model_order:
        if column_model == model:
            row_obs[column_model] = int(model_info["observations"])
            row_r2[column_model] = round(model_info["r_squared"], 3)
        else:
            row_obs[column_model] = ""
            row_r2[column_model] = ""

    rows.append(row_obs)
    rows.append(row_r2)


final_table = pd.DataFrame(rows)

csv_path = TABLE_DIR / "formatted_regression_table_event_categories.csv"
txt_path = TABLE_DIR / "formatted_regression_table_event_categories.txt"

final_table.to_csv(csv_path, index=False)

with open(txt_path, "w", encoding="utf-8") as file:
    file.write(final_table.to_string(index=False))


print("\nFormatted regression table saved to:")
print(csv_path)
print(txt_path)

print("\nFormatted table:")
print(final_table.to_string(index=False))
