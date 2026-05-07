import yfinance as yf
import pandas as pd
import os

base = os.path.dirname(os.path.abspath(__file__))

# Load S&P 500 tickers from file
tickers = pd.read_csv(os.path.join(base, 'data', 'sp500_tickers.csv'), header=None)[0].tolist()
print(f"Loaded {len(tickers)} tickers")

# Download price data — this will take 3-5 minutes
print("Downloading price data... please wait")
data = yf.download(tickers, start="2021-01-01", end="2026-01-01")["Close"]

# Drop columns with too much missing data
data = data.dropna(axis=1, thresh=int(len(data) * 0.8))
print(f"Stocks after cleaning: {data.shape[1]}")

# Compute daily returns
returns = data.pct_change().dropna()

# Save to file so we don't re-download every time
returns.to_csv(os.path.join(base, 'data', 'returns.csv'))
print("Saved returns to data/returns.csv")
print(returns.tail(3))

# Save price levels for P/B computation
data.to_csv(os.path.join(base, 'data', 'prices.csv'))
print("Saved prices to data/prices.csv")