import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factors.momentum import compute_momentum
from factors.profitability import compute_profitability
from factors.value import compute_value

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "V", "UNH",
    "XOM", "JNJ", "WMT", "PG", "MA",
    "HD", "CVX", "MRK", "ABBV", "PEP"
]

# Pull price data
data = yf.download(tickers, start="2021-01-01", end="2026-01-01")["Close"]
returns = data.pct_change().dropna()

# Compute all three factors
momentum, mom_ranks = compute_momentum(returns)
roe = compute_profitability(tickers)
pb, pb_ranks = compute_value(tickers)

# Fix ABBV negative P/B
pb = pb.copy()
pb[pb < 0] = None
pb_ranks = pb.rank(ascending=False)

# Normalise all factors to 0-1
def normalise(series):
    return (series - series.min()) / (series.max() - series.min())

prof_norm = normalise(roe.rank(ascending=True))
value_norm = normalise(pb_ranks)

# Broadcast static factors across time
def broadcast(series, index, columns):
    return pd.DataFrame(
        [series.reindex(columns).values] * len(index),
        index=index,
        columns=columns
    )

mom_norm = mom_ranks.div(mom_ranks.max(axis=1), axis=0)
prof_broadcast = broadcast(prof_norm, mom_ranks.index, mom_ranks.columns)
value_broadcast = broadcast(value_norm, mom_ranks.index, mom_ranks.columns)

# Composite: equal weight
composite = (mom_norm + prof_broadcast + value_broadcast) / 3

# Long top 5, short bottom 5
top5 = composite.rank(axis=1, ascending=True) >= 16
bottom5 = composite.rank(axis=1, ascending=True) <= 5

long_returns = returns[top5].mean(axis=1)
short_returns = returns[bottom5].mean(axis=1)
portfolio_returns = (long_returns - short_returns).dropna()

# Metrics
cumulative = (1 + portfolio_returns).cumprod()
sharpe = portfolio_returns.mean() / portfolio_returns.std() * (252 ** 0.5)
max_dd = ((cumulative / cumulative.cummax()) - 1).min()

print(f"Sharpe Ratio: {sharpe:.2f}")
print(f"Total Return: {(cumulative.iloc[-1] - 1) * 100:.1f}%")
print(f"Max Drawdown: {max_dd * 100:.1f}%")

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

ax1.plot(cumulative.index, cumulative.values,
         label="Composite (Momentum + Profitability + Value)",
         linewidth=2, color="steelblue")
ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
ax1.set_title("Three-Factor Model — Cumulative Returns (2021–2026)")
ax1.set_ylabel("Cumulative Return")
ax1.legend()
ax1.grid(True)

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