import yfinance as yf
import pandas as pd
import os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load tickers
tickers = pd.read_csv(os.path.join(base, 'data', 'sp500_tickers.csv'), header=None)[0].tolist()
print(f"Fetching quarterly fundamentals for {len(tickers)} stocks...")
print("This will take 20-30 minutes. Leave it running.")

roe_records = []
pb_records = []

for i, ticker in enumerate(tickers):
    if i % 50 == 0:
        print(f"Progress: {i}/{len(tickers)}")
    try:
        stock = yf.Ticker(ticker)

        # --- ROE: Net Income / Stockholders Equity (quarterly) ---
        income = stock.quarterly_financials
        balance = stock.quarterly_balance_sheet

        if income is not None and balance is not None:
            if "Net Income" in income.index and "Stockholders Equity" in balance.index:
                net_income = income.loc["Net Income"]
                equity = balance.loc["Stockholders Equity"]

                # Align dates and compute ROE for each quarter
                common_dates = net_income.index.intersection(equity.index)
                for date in common_dates:
                    ni = net_income[date]
                    eq = equity[date]
                    if eq and eq != 0:
                        roe_records.append({
                            'ticker': ticker,
                            'date': date,
                            'roe': ni / eq
                        })

        # --- P/B: requires price data + book value per share ---
        info = stock.info
        pb = info.get("priceToBook", None)
        # P/B is static from info — we'll handle time-varying via book value
        balance_annual = stock.balance_sheet
        if balance_annual is not None and "Stockholders Equity" in balance_annual.index:
            shares = info.get("sharesOutstanding", None)
            if shares and shares > 0:
                equity_annual = balance_annual.loc["Stockholders Equity"]
                for date in equity_annual.index:
                    eq = equity_annual[date]
                    if eq and eq != 0:
                        pb_records.append({
                            'ticker': ticker,
                            'date': date,
                            'book_value_per_share': eq / shares
                        })

    except Exception as e:
        continue

# Save results
roe_df = pd.DataFrame(roe_records)
pb_df = pd.DataFrame(pb_records)

roe_df.to_csv(os.path.join(base, 'data', 'roe_quarterly.csv'), index=False)
pb_df.to_csv(os.path.join(base, 'data', 'book_value_annual.csv'), index=False)

print(f"Done. ROE records: {len(roe_df)}, Book value records: {len(pb_df)}")
print("Saved to data/roe_quarterly.csv and data/book_value_annual.csv")