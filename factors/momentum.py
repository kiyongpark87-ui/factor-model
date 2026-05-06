import pandas as pd


def compute_momentum(returns):
    """
    Computes the 12-1 momentum factor for each stock.

    Momentum is defined as the cumulative return over the past 12 months,
    excluding the most recent month. This is standard to avoid short-term reversal effects.

    Args:
        returns: DataFrame of daily returns (rows = dates, columns = tickers)

    Returns:
        momentum: DataFrame of momentum scores
        ranks: DataFrame of cross-sectional ranks each day (1 = lowest, 20 = highest)
    """
    # Use a 252-day rolling window (1 trading year)
    # Exclude the last 21 days (1 month) to avoid short-term reversal
    # Convert returns to growth factors (1 + r), multiply them, subtract 1
    momentum = (1 + returns).rolling(window=252).apply(lambda x: x[:-21].prod()) - 1

    # Rank stocks cross-sectionally each day
    # ascending=True means rank 20 = highest momentum (best)
    ranks = momentum.rank(axis=1, ascending=True)

    return momentum, ranks


if __name__ == "__main__":
    import yfinance as yf

    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "JPM", "V", "UNH",
        "XOM", "JNJ", "WMT", "PG", "MA",
        "HD", "CVX", "MRK", "ABBV", "PEP"
    ]

    # Download historical price data and compute daily returns
    data = yf.download(tickers, start="2021-01-01", end="2024-01-01")["Close"]
    returns = data.pct_change().dropna()

    momentum, ranks = compute_momentum(returns)
    print("Momentum scores (last 3 rows):")
    print(momentum.tail(3))
    print("\nRankings (last 3 rows):")
    print(ranks.tail(3))