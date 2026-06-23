import pandas as pd
import numpy as np
import requests
import yfinance as yf
import statsmodels.api as sm
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("Environment works!")

analyzer = SentimentIntensityAnalyzer()
headline = "Apple shares fall after weak earnings outlook."
score = analyzer.polarity_scores(headline)

print("Example headline:", headline)
print("Sentiment score:", score)