import pandas as pd
import yfinance as yf


def compute_profitability(tickers):
    """
    Computes the profitability factor using Return on Equity (ROE).

    ROE = Net Income / Shareholders Equity
    Higher ROE = more profitable = higher rank.

    Data is pulled from yfinance financials (most recent fiscal year).

    Known limitation: Companies with negative equity (e.g. ABBV due to
    heavy buybacks) produce negative ROE, which distorts rankings.
    These should be handled carefully in production systems.

    Args:
        tickers: list of stock ticker strings

    Returns:
        roe_series: pandas Series of ROE values indexed by ticker
    """
    roe_dict = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # Pull income statement and balance sheet
            income = stock.financials
            balance = stock.balance_sheet

            # Use most recent fiscal year (iloc[0])
            net_income = income.loc["Net Income"].iloc[0]
            equity = balance.loc["Stockholders Equity"].iloc[0]

            # Compute ROE
            roe = net_income / equity
            roe_dict[ticker] = roe

        except:
            # If data is unavailable for a ticker, store None
            roe_dict[ticker] = None

    roe_series = pd.Series(roe_dict)
    return roe_series


if __name__ == "__main__":
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "JPM", "V", "UNH",
        "XOM", "JNJ", "WMT", "PG", "MA",
        "HD", "CVX", "MRK", "ABBV", "PEP"
    ]

    roe = compute_profitability(tickers)

    # Rank by ROE — higher ROE gets higher rank
    roe_ranked = roe.rank(ascending=True)

    print("ROE scores:")
    print(roe.sort_values(ascending=False))
    print("\nRankings (higher = more profitable):")
    print(roe_ranked.sort_values(ascending=False))