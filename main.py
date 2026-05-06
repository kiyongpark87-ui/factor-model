import yfinance as yf
import pandas as pd

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "V", "UNH",
    "XOM", "JNJ", "WMT", "PG", "MA",
    "HD", "CVX", "MRK", "ABBV", "PEP"
]

data = yf.download(tickers, start="2021-01-01", end="2024-01-01")["Close"]
returns = data.pct_change().dropna()

print(returns.head())