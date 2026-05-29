# Chapter 1: Market Data

[prev: Overview](chapter-00-overview.md) | [next: Chapter 2 - Statistics](chapter-02-statistics.md)

---

Market data is the foundation of every quantitative strategy. This chapter covers how to acquire, clean, and store financial data.

## Data Sources

| Source        | Type                  | Cost             | Coverage         |
| ------------- | --------------------- | ---------------- | ---------------- |
| yfinance      | Stocks, ETFs, Crypto  | Free             | Global equities  |
| Alpha Vantage | Stocks, Forex, Crypto | Free tier / Paid | Global           |
| Binance API   | Crypto                | Free             | All crypto pairs |
| Polygon.io    | Stocks, Options       | Paid             | US equities      |

## OHLCV Data

OHLCV stands for Open, High, Low, Close, Volume — the standard format for bar data:

- **Open**: First trade price in the period
- **High**: Highest price in the period
- **Low**: Lowest price in the period
- **Close**: Last trade price in the period
- **Volume**: Total shares/contracts traded

## Fetching Data with yfinance

```python
import yfinance as yf
import pandas as pd

# Single stock
aapl = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
print(aapl.head())

# Multiple stocks
tickers = ["AAPL", "MSFT", "GOOGL"]
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")
print(data["Close"].head())
```

## Alpha Vantage

```python
import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"
symbol = "AAPL"
url = (
    f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
    f"&symbol={symbol}&outputsize=full&apikey={API_KEY}"
)

response = requests.get(url)
data = response.json()["Time Series (Daily)"]
df = pd.DataFrame.from_dict(data, orient="index", dtype=float)
df.columns = ["open", "high", "low", "close", "volume"]
df.index = pd.to_datetime(df.index)
df = df.sort_index()
print(df.tail())
```

## Binance API (Crypto)

```python
import requests
import pandas as pd

def fetch_binance_klines(symbol="BTCUSDT", interval="1d", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.set_index("open_time")
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

btc = fetch_binance_klines()
print(btc.tail())
```

## Candlestick Charts with mplfinance

```python
import mplfinance as mpf
import yfinance as yf

data = yf.download("AAPL", start="2024-01-01", end="2024-03-01")

mpf.plot(
    data,
    type="candle",
    volume=True,
    style="charles",
    title="AAPL Daily Candlestick",
    savefig="aapl_candle.png"
)
```

## Tick Data vs Bar Data

**Tick data**: Every individual trade (timestamp, price, size). Highest granularity but massive storage requirements.

**Bar data**: Aggregated into time intervals (1min, 5min, 1h, 1d). Most strategies use bar data.

```python
# Simulating tick-to-bar conversion
import numpy as np

# Simulated tick data
np.random.seed(42)
n_ticks = 10000
timestamps = pd.date_range("2024-01-01 09:30", periods=n_ticks, freq="s")
prices = 100 + np.cumsum(np.random.randn(n_ticks) * 0.01)
volumes = np.random.randint(1, 100, n_ticks)

ticks = pd.DataFrame({"price": prices, "volume": volumes}, index=timestamps)

# Convert to 1-minute bars
bars = ticks.resample("1min").agg({
    "price": ["first", "max", "min", "last"],
    "volume": "sum"
})
bars.columns = ["open", "high", "low", "close", "volume"]
print(bars.head())
```

## Data Cleaning

```python
import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")

# Check for missing values
print(f"Missing values:\n{df.isnull().sum()}")

# Forward fill small gaps (weekends/holidays are already excluded)
df = df.ffill()

# Remove zero-volume days (likely bad data)
df = df[df["Volume"] > 0]

# Remove extreme outliers (price changes > 50% in one day)
returns = df["Close"].pct_change()
df = df[returns.abs() < 0.5]

# Verify data integrity
print(f"Date range: {df.index[0]} to {df.index[-1]}")
print(f"Total trading days: {len(df)}")
print(f"Any NaN remaining: {df.isnull().any().any()}")
```

## Storing in pandas DataFrame

```python
import yfinance as yf
import pandas as pd

# Download and save to CSV
df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
df.to_csv("data/aapl_daily.csv")

# Read back
df = pd.read_csv("data/aapl_daily.csv", index_col="Date", parse_dates=True)

# Save to Parquet (faster, smaller, preserves types)
df.to_parquet("data/aapl_daily.parquet")
df = pd.read_parquet("data/aapl_daily.parquet")
```

## Resampling Timeframes

```python
import yfinance as yf

# Get daily data
df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")

# Resample to weekly
weekly = df.resample("W").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum"
})

# Resample to monthly
monthly = df.resample("ME").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum"
})

print("Daily shape:", df.shape)
print("Weekly shape:", weekly.shape)
print("Monthly shape:", monthly.shape)
```

## Building a Data Pipeline

```python
import yfinance as yf
import pandas as pd
from pathlib import Path

class MarketDataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def fetch(self, symbol, start="2020-01-01", end="2024-01-01"):
        cache_path = self.data_dir / f"{symbol}_daily.parquet"

        if cache_path.exists():
            df = pd.read_parquet(cache_path)
        else:
            df = yf.download(symbol, start=start, end=end)
            df = df.ffill().dropna()
            df = df[df["Volume"] > 0]
            df.to_parquet(cache_path)

        return df

# Usage
loader = MarketDataLoader()
aapl = loader.fetch("AAPL")
print(aapl.tail())
```

---

## Key Takeaways

- yfinance is the easiest free source for stock data
- Always clean data before using it in strategies
- Parquet format is preferred over CSV for storage
- Understand the difference between tick and bar data
- Resampling lets you test strategies on multiple timeframes

---

[prev: Overview](chapter-00-overview.md) | [next: Chapter 2 - Statistics](chapter-02-statistics.md)
