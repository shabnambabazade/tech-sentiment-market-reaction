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
print("Columns:", news.columns.tolist())


# We make sure that the publication date is treated as a real date.
news["published_at"] = pd.to_datetime(news["published_at"], errors="coerce")

# If the raw data already has a date column, we clean it.
# If not, we create it from published_at.

if "date" in news.columns:
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
else:
    news["date"] = news["published_at"].dt.date
    news["date"] = pd.to_datetime(news["date"], errors="coerce")


# We combine title, summary, and topics into one text field.
# This text will be used to classify the type of negative news.
def topics_to_text(value):
    """
    Alpha Vantage topics are stored as JSON-like text.
    We extract the topic names and turn them into plain text.
    """
    if pd.isna(value):
        return ""

    try:
        parsed = json.loads(value)
        topic_names = []

        for item in parsed:
            topic_name = item.get("topic", "")
            topic_names.append(topic_name)

        return " ".join(topic_names)

    except Exception:
        return str(value)


news["topics_text"] = news["topics"].apply(topics_to_text)

news["text_for_classification"] = (
    news["title"].fillna("") + " " +
    news["summary"].fillna("") + " " +
    news["topics_text"].fillna("")
).str.lower()


# Alpha Vantage gives ticker-specific sentiment labels.
# We treat Bearish and Somewhat-Bearish as negative sentiment.

negative_labels = ["Bearish", "Somewhat-Bearish"]
news["is_negative"] = news["ticker_sentiment_label"].isin(negative_labels).astype(int)


# Keyword dictionaries for the negative news categories.
# These categories follow the professor's suggestion:
# earnings prospects, growth expectations, regulation, competition, and macroeconomic concerns.

CATEGORY_KEYWORDS = {
    "earnings": [
        "earnings", "revenue", "revenues", "profit", "profits",
        "net income", "operating income", "margin", "margins",
        "eps", "earnings per share", "guidance", "quarterly results",
        "results", "financial results", "loss", "losses",
        "missed estimates", "miss estimates", "beat estimates",
        "lower guidance", "weak guidance", "profit warning",
        "costs", "expenses", "cash flow"
    ],

    "growth": [
        "growth", "demand", "sales", "users", "user growth",
        "subscriber", "subscribers", "subscription", "outlook",
        "forecast", "slowdown", "slowing", "slow growth",
        "expansion", "weaker demand", "weak demand",
        "cloud growth", "ai demand", "chip demand",
        "iphone demand", "ad sales", "digital advertising",
        "market opportunity", "future growth"
    ],

    "regulation": [
        "regulation", "regulatory", "antitrust", "lawsuit",
        "legal", "investigation", "probe", "fine", "penalty",
        "privacy", "data privacy", "court", "ftc", "doj",
        "sec", "european union", "eu", "commission",
        "regulator", "regulators", "ban", "blocked",
        "compliance", "monopoly", "app store rules"
    ],

    "competition": [
        "competition", "competitive", "competitor", "competitors",
        "rival", "rivals", "market share", "share loss",
        "loses share", "takes share", "pressure", "pricing pressure",
        "challenge", "challenger", "threat", "alternative",
        "substitute", "price war", "competes with",
        "catch up", "fall behind", "switching"
    ],

    "macro": [
        "inflation", "interest rate", "interest rates",
        "rate hike", "rate hikes", "higher rates",
        "federal reserve", "fed", "monetary policy",
        "recession", "economy", "economic", "macro",
        "tariff", "tariffs", "supply chain", "geopolitical",
        "war", "uncertainty", "bond yields", "treasury yields",
        "yields", "dollar", "oil prices", "consumer spending",
        "labor market", "unemployment"
    ]
}


def contains_keyword(text, keywords):
    """
    Returns 1 if at least one keyword appears in the text.
    Otherwise returns 0.

    We use regex word boundaries to avoid accidental matches.
    Example: 'fed' should match 'Fed', but not a random part of another word.
    """
    if pd.isna(text):
        return 0

    for keyword in keywords:
        keyword_pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

        if re.search(keyword_pattern, text):
            return 1

    return 0

# Create category variables.
# A category is counted only if the article is negative AND the related keywords appear.

for category, keywords in CATEGORY_KEYWORDS.items():
    column_name = f"neg_{category}"

    news[column_name] = news.apply(
        lambda row: 1
        if row["is_negative"] == 1 and contains_keyword(row["text_for_classification"], keywords)
        else 0,
        axis=1
    )


category_columns = [
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro"
]

# Some negative articles may not match any category.
# We keep them as "neg_other" so we do not lose them.

news["negative_category_count"] = news[category_columns].sum(axis=1)
news["neg_other"] = news.apply(
    lambda row: 1
    if row["is_negative"] == 1 and row["negative_category_count"] == 0
    else 0,
    axis=1
)

# Save the processed news dataset.
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
    "neg_earnings",
    "neg_growth",
    "neg_regulation",
    "neg_competition",
    "neg_macro",
    "neg_other"
]

print(news.loc[news["is_negative"] == 1, example_columns].head(20))