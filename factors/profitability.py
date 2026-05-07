import pandas as pd
import os

def compute_profitability_tv(returns_index):
    """
    Time-varying profitability factor using quarterly ROE.
    Forward-fills quarterly values to daily frequency.
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roe_raw = pd.read_csv(os.path.join(base, 'data', 'roe_quarterly.csv'))
    roe_raw['date'] = pd.to_datetime(roe_raw['date']).dt.tz_localize(None)

    # Pivot to wide format
    roe_pivot = roe_raw.pivot_table(index='date', columns='ticker', values='roe')

    # Reindex to full daily calendar first, then forward-fill
    full_index = pd.date_range(
        start=roe_pivot.index.min(),
        end=pd.Timestamp(returns_index.max()).tz_localize(None),
        freq='D'
    )
    roe_daily_full = roe_pivot.reindex(full_index).ffill()

    # Now select only trading days
    returns_index_normalized = returns_index.normalize()
    if returns_index_normalized.tz is not None:
        returns_index_normalized = returns_index_normalized.tz_localize(None)

    roe_daily = roe_daily_full.reindex(returns_index_normalized)
    roe_daily.index = returns_index

    return roe_daily


def compute_profitability(tickers):
    """Legacy static version."""
    import yfinance as yf
    roe_dict = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            net_income = income.loc["Net Income"].iloc[0]
            equity = balance.loc["Stockholders Equity"].iloc[0]
            roe_dict[ticker] = net_income / equity
        except:
            roe_dict[ticker] = None
    return pd.Series(roe_dict)