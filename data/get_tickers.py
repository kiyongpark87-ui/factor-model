import pandas as pd
import requests
from io import StringIO

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

response = requests.get(url, headers=headers)
table = pd.read_html(StringIO(response.text))
sp500 = table[0]['Symbol'].tolist()

sp500 = [t.replace('.', '-') for t in sp500]

print(f"Total tickers: {len(sp500)}")
print(sp500[:10])

import os
os.makedirs('data', exist_ok=True)
pd.Series(sp500).to_csv('data/sp500_tickers.csv', index=False, header=False)
print("Saved to data/sp500_tickers.csv")