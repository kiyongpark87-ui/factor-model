import pandas as pd
import yfinance as yf


def compute_value(tickers):
    """
    Computes the value factor using Price-to-Book (P/B) ratio.

    P/B = Market Price / Book Value per Share
    Lower P/B = stock is cheaper relative to its accounting value = better value.

    rank ascending=False so that the lowest P/B gets the highest rank.

    Known limitation: Companies with negative equity (e.g. ABBV) produce
    negative P/B ratios, which should be excluded before ranking.

    Args:
        tickers: list of stock ticker strings

    Returns:
        pb_series: pandas Series of raw P/B ratios indexed by ticker
        pb_ranked: pandas Series of ranks (higher rank = better value)
    """
    pb_dict = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # priceToBook is available directly in yfinance info
            pb = stock.info.get("priceToBook", None)
            pb_dict[ticker] = pb

        except:
            # If data is unavailable, store None
            pb_dict[ticker] = None

    pb_series = pd.Series(pb_dict)

    # Lower P/B = better value = should get higher rank
    # ascending=False ensures lowest P/B receives rank 20 (best)
    pb_ranked = pb_series.rank(ascending=False)

    return pb_series, pb_ranked


if __name__ == "__main__":
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "JPM", "V", "UNH",
        "XOM", "JNJ", "WMT", "PG", "MA",
        "HD", "CVX", "MRK", "ABBV", "PEP"
    ]

    pb, pb_ranked = compute_value(tickers)

    print("Price-to-Book ratios:")
    print(pb.sort_values(ascending=True))
    print("\nValue Rankings (higher rank = better value):")
    print(pb_ranked.sort_values(ascending=False))