from pathlib import Path
import json
import re
import pandas as pd


RAW_NEWS_PATH = Path("data/raw/alpha_vantage_news_2023_2025.csv")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


print("Loading Alpha Vantage news data...")
news = pd.read_csv(RAW_NEWS_PATH)

print("Raw news data loaded.")
print("Shape:", news.shape)


news["published_at"] = pd.to_datetime(news["published_at"], errors="coerce")

if "date" in news.columns:
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
else:
    news["date"] = pd.to_datetime(news["published_at"].dt.date, errors="coerce")


def topics_to_text(value):
    # topics are saved as JSON text, so this turns them into normal words
    if pd.isna(value):
        return ""

    try:
        parsed = json.loads(value)
        topic_names = []

        for item in parsed:
            topic_names.append(item.get("topic", ""))

        return " ".join(topic_names)

    except Exception:
        return str(value)


if "topics" in news.columns:
    news["topics_text"] = news["topics"].apply(topics_to_text)
else:
    news["topics_text"] = ""


news["text_for_classification"] = (
    news["title"].fillna("") + " "
    + news["summary"].fillna("") + " "
    + news["topics_text"].fillna("")
).str.lower()


negative_labels = ["Bearish", "Somewhat-Bearish"]
news["is_negative"] = news["ticker_sentiment_label"].isin(negative_labels).astype(int)


category_keywords = {
    "earnings_guidance": [
        "earnings", "revenue", "revenues", "profit", "profits",
        "net income", "operating income", "margin", "margins",
        "eps", "earnings per share", "guidance", "quarterly results",
        "financial results", "loss", "losses", "missed estimates",
        "miss estimates", "lower guidance", "weak guidance",
        "profit warning", "costs", "expenses", "cash flow",
    ],

    "demand_growth": [
        "growth", "demand", "sales", "users", "user growth",
        "subscriber", "subscribers", "subscription", "customer growth",
        "customer demand", "slowdown", "slowing", "slow growth",
        "weaker demand", "weak demand", "outlook", "forecast",
        "expansion", "cloud growth", "ai demand", "chip demand",
        "ad sales", "digital advertising", "future growth",
    ],

    "legal_regulatory": [
        "regulation", "regulatory", "antitrust", "lawsuit", "legal",
        "investigation", "probe", "fine", "penalty", "privacy",
        "data privacy", "court", "ftc", "doj", "sec",
        "european union", "eu", "commission", "regulator",
        "regulators", "ban", "blocked", "compliance",
        "monopoly", "settlement",
    ],

    "product_technology": [
        "product delay", "launch delay", "delayed launch",
        "product issue", "product problem", "failed launch",
        "outage", "downtime", "cloud outage", "platform outage",
        "cybersecurity", "security breach", "data breach", "bug",
        "technical problem", "technical issue", "ai issue",
        "chip delay", "recall", "defect",
    ],

    "strategy_management": [
        "layoffs", "job cuts", "workforce reduction", "restructuring",
        "cost cutting", "cost cuts", "cost reduction", "ceo", "cfo",
        "management change", "leadership change", "executive departure",
        "acquisition", "merger", "takeover", "strategy shift",
        "business strategy", "spin off", "spinoff",
    ],

    "competition_pressure": [
        "competition", "competitive", "competitor", "competitors",
        "rival", "rivals", "market share", "share loss",
        "loses share", "takes share", "pricing pressure", "price war",
        "competitive pressure", "challenger", "threat", "alternative",
        "substitute", "competes with", "fall behind", "switching",
    ],
}


def contains_keyword(text, keywords):
    if pd.isna(text):
        return 0

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

        if re.search(pattern, text):
            return 1

    return 0


category_columns = []

for category, keywords in category_keywords.items():
    column_name = f"neg_{category}"
    category_columns.append(column_name)

    news[column_name] = news.apply(
        lambda row: 1
        if row["is_negative"] == 1
        and contains_keyword(row["text_for_classification"], keywords)
        else 0,
        axis=1,
    )


news["negative_category_count"] = news[category_columns].sum(axis=1)

news["neg_other"] = news.apply(
    lambda row: 1
    if row["is_negative"] == 1 and row["negative_category_count"] == 0
    else 0,
    axis=1,
)


output_path = PROCESSED_DIR / "news_with_negative_categories_2023_2025.csv"
news.to_csv(output_path, index=False)


print("\nProcessed news data saved to:")
print(output_path)

print("\nDataset shape:")
print(news.shape)

print("\nNegative sentiment count:")
print(news["is_negative"].value_counts())

print("\nNegative category counts:")
for column in category_columns + ["neg_other"]:
    print(column, "=", int(news[column].sum()))


print("\nNegative news examples:")
example_columns = [
    "ticker",
    "date",
    "title",
    "ticker_sentiment_label",
    "neg_earnings_guidance",
    "neg_demand_growth",
    "neg_legal_regulatory",
    "neg_product_technology",
    "neg_strategy_management",
    "neg_competition_pressure",
    "neg_other",
]

print(news.loc[news["is_negative"] == 1, example_columns].head(20))
