import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import sys
import os

# Allow imports from the project root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factors.momentum import compute_momentum
from factors.profitability import compute_profitability
from factors.value import compute_value

# 20 large-cap US stocks across sectors (tech, finance, energy, healthcare, consumer)
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "V", "UNH",
    "XOM", "JNJ", "WMT", "PG", "MA",
    "HD", "CVX", "MRK", "ABBV", "PEP"
]

# Data Pipeline
# Download daily closing prices from 2021 to 2026
data = yf.download(tickers, start="2021-01-01", end="2026-01-01")["Close"]

# Compute daily percentage returns and drop the first row (NaN from pct_change)
returns = data.pct_change().dropna()

# Factor Computation
momentum, mom_ranks = compute_momentum(returns)   # Time-series factor (changes daily)
roe = compute_profitability(tickers)               # Static fundamental factor (one value per stock)
pb, pb_ranks = compute_value(tickers)             # Static fundamental factor (one value per stock)

# Data Cleaning
# ABBV has negative equity, producing a negative P/B ratio that distorts rankings
# Set negative P/B values to NaN and re-rank
pb = pb.copy()
pb[pb < 0] = None
pb_ranks = pb.rank(ascending=False)


# Normalisation
# Scale all factor ranks to [0, 1] so they contribute equally to the composite
def normalise(series):
    """Min-max normalisation: maps values to the range [0, 1]."""
    return (series - series.min()) / (series.max() - series.min())


prof_norm = normalise(roe.rank(ascending=True))   # Higher ROE = higher normalised score
value_norm = normalise(pb_ranks)                   # Lower P/B = higher normalised score


# Broadcasting Static Factors Across Time
# Profitability and value are point-in-time snapshots (not time-varying)
# We broadcast them into a DataFrame matching the shape of the momentum DataFrame
def broadcast(series, index, columns):
    """Repeat a static cross-sectional series across all dates in index."""
    return pd.DataFrame(
        [series.reindex(columns).values] * len(index),
        index=index,
        columns=columns
    )


# Normalise momentum ranks row-by-row (each day sums to 1)
mom_norm = mom_ranks.div(mom_ranks.max(axis=1), axis=0)

# Broadcast profitability and value to match momentum's time index
prof_broadcast = broadcast(prof_norm, mom_ranks.index, mom_ranks.columns)
value_broadcast = broadcast(value_norm, mom_ranks.index, mom_ranks.columns)

# Composite Score
# Equal-weight combination of all three factors
# Each factor contributes 1/3 to the final stock score each day
composite = (mom_norm + prof_broadcast + value_broadcast) / 3

# Portfolio Construction
# Long the top 5 ranked stocks, short the bottom 5 ranked stocks
# This is a long-short equity strategy (market-neutral in theory)
top5 = composite.rank(axis=1, ascending=True) >= 16     # Top 5 = ranks 16-20
bottom5 = composite.rank(axis=1, ascending=True) <= 5   # Bottom 5 = ranks 1-5

# Equal-weight returns within long and short legs
long_returns = returns[top5].mean(axis=1)
short_returns = returns[bottom5].mean(axis=1)

# Portfolio return = long leg minus short leg (long-short spread)
portfolio_returns = (long_returns - short_returns).dropna()

# Performance Metrics
# Cumulative return: how $1 invested grew over time
cumulative = (1 + portfolio_returns).cumprod()

# Sharpe ratio: annualised risk-adjusted return (252 trading days)
sharpe = portfolio_returns.mean() / portfolio_returns.std() * (252 ** 0.5)

# Max drawdown: worst peak-to-trough decline
max_dd = ((cumulative / cumulative.cummax()) - 1).min()

print(f"Sharpe Ratio: {sharpe:.2f}")
print(f"Total Return: {(cumulative.iloc[-1] - 1) * 100:.1f}%")
print(f"Max Drawdown: {max_dd * 100:.1f}%")

# Visualisation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Top chart: cumulative returns over time
ax1.plot(cumulative.index, cumulative.values,
         label="Composite (Momentum + Profitability + Value)",
         linewidth=2, color="steelblue")
ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5)  # Break-even line
ax1.set_title("Three-Factor Model — Cumulative Returns (2021–2026)")
ax1.set_ylabel("Cumulative Return")
ax1.legend()
ax1.grid(True)

# Bottom chart: drawdown over time
drawdown = (cumulative / cumulative.cummax()) - 1
ax2.fill_between(drawdown.index, drawdown.values, 0,
                 color='red', alpha=0.3, label="Drawdown")
ax2.set_title("Drawdown")
ax2.set_ylabel("Drawdown")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()