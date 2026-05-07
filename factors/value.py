import pandas as pd
import yfinance as yf
import os


def compute_value_tv(returns):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load book value and prices
    bv_raw = pd.read_csv(os.path.join(base, 'data', 'book_value_annual.csv'))
    bv_raw['date'] = pd.to_datetime(bv_raw['date']).dt.tz_localize(None)

    prices = pd.read_csv(os.path.join(base, 'data', 'prices.csv'),
                         index_col=0, parse_dates=True)
    prices.index = prices.index.tz_localize(None)

    # Pivot book value
    bv_pivot = bv_raw.pivot_table(index='date', columns='ticker', values='book_value_per_share')

    # Reindex to full daily calendar (not just trading days) then forward fill
    full_index = pd.date_range(start=bv_pivot.index.min(),
                               end=returns.index.max(), freq='D')
    bv_daily_full = bv_pivot.reindex(full_index).ffill()

    # Now select only trading days from returns index
    returns_index_normalized = returns.index.normalize()
    bv_daily = bv_daily_full.reindex(returns_index_normalized)
    bv_daily.index = returns.index  # restore original index

    # Align with prices and compute P/B
    common = bv_daily.columns.intersection(prices.columns)
    pb_daily = prices[common] / bv_daily[common]

    return pb_daily

def compute_value(tickers):
    """Legacy static version — kept for compatibility."""
    pb_dict = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            pb = stock.info.get("priceToBook", None)
            pb_dict[ticker] = pb
        except:
            pb_dict[ticker] = None
    pb_series = pd.Series(pb_dict)
    pb_ranked = pb_series.rank(ascending=False)
    return pb_series, pb_ranked