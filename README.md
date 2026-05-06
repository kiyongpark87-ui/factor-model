# Three-Factor Equity Model

A quantitative factor model built in Python that ranks stocks using three 
independent signals — momentum, profitability, and value — and backtests 
a long-short portfolio strategy from 2021 to 2026.

---

## Motivation

This project was inspired by my alpha research experience at WorldQuant BRAIN,
where I developed systematic trading signals on US equities. I wanted to build
a full factor model from scratch — from raw price and fundamental data through
to portfolio construction and performance analysis.

---

## Factors

| Factor | Metric | Intuition |
|---|---|---|
| Momentum | 12-1 month return | Stocks that have outperformed recently tend to continue outperforming |
| Profitability | Return on Equity (ROE) | More profitable companies generate higher long-run returns |
| Value | Price-to-Book (P/B) ratio | Cheaper stocks relative to book value tend to outperform over time |

Each factor is normalised to [0, 1] and combined into an equal-weighted 
composite score. The portfolio goes long the top 5 ranked stocks and 
short the bottom 5 ranked stocks each day.

---

## Results

| Metric | Momentum Only | + Profitability | + Value (Final) |
|---|---|---|---|
| Sharpe Ratio | 0.03 | 0.09 | 0.14 |
| Total Return | -6.1% | -0.3% | +1.1% |
| Max Drawdown | -42.3% | -30.5% | -44.9% |

Each additional factor improved the Sharpe ratio, demonstrating the 
diversification benefit of combining uncorrelated signals.

---

## Key Findings

**Momentum crash of 2022–2023:** The standalone momentum strategy suffered 
heavily during the Fed's aggressive rate hiking cycle. High-momentum tech 
stocks (the long leg) sold off sharply while low-momentum energy stocks 
(the short leg) surged on rising oil prices — exactly the wrong outcome. 
This is a well-documented phenomenon in academic literature.

**Factor diversification works:** Adding profitability and value signals 
progressively stabilised the strategy. The composite model recovered strongly 
through 2024–2025, validating the principle that uncorrelated factors reduce 
drawdown risk.

**Known limitations:**
- Universe is only 20 large-cap US stocks — too small for production
- Profitability and value factors are static (point-in-time) rather than 
  time-varying, which introduces look-ahead bias
- ABBV was excluded from value rankings due to negative equity distorting 
  the P/B ratio

---

## Project Structure

```
factor-model/
├── backtest/
│   └── backtest.py        # Portfolio construction and performance metrics
├── factors/
│   ├── momentum.py        # 12-1 month rolling momentum factor
│   ├── profitability.py   # ROE-based profitability factor
│   └── value.py           # Price-to-book value factor
└── README.md
```
---

## Tech Stack

- Python 3
- pandas, numpy — data manipulation
- yfinance — market and fundamental data
- matplotlib — visualisation

---

## What I Learned

- How momentum crashes occur and why rate environments matter for factor performance
- The mechanics of long-short equity portfolio construction
- How combining factors with low correlation improves risk-adjusted returns
- Practical limitations of backtesting with small universes and static fundamentals


