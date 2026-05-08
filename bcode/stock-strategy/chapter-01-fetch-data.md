# Chapter 1: Fetching Stock Data

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Visualization →](chapter-02-visualization.md)

---

## The Basics: yfinance

`yfinance` pulls free data from Yahoo Finance. No API key needed.

```python
import yfinance as yf
import pandas as pd

# Single stock — last 2 years of daily data
aapl = yf.download("AAPL", start="2023-01-01", end="2025-01-01")
print(aapl.head())
```

```
                  Open        High         Low       Close   Adj Close    Volume
Date
2023-01-03  130.279999  130.899994  124.169998  125.070000  124.42...  112117500
2023-01-04  126.889999  128.660004  125.080002  126.360001  125.70...   89113600
...
```

## Periods and Intervals

```python
# By period (relative to today)
data = yf.download("MSFT", period="6mo")    # Last 6 months
data = yf.download("MSFT", period="5y")     # Last 5 years
data = yf.download("MSFT", period="max")    # All available history

# By date range
data = yf.download("MSFT", start="2020-01-01", end="2024-12-31")

# Different intervals (timeframes)
daily = yf.download("MSFT", period="1y", interval="1d")    # Daily
weekly = yf.download("MSFT", period="2y", interval="1wk")  # Weekly
monthly = yf.download("MSFT", period="10y", interval="1mo") # Monthly
intraday = yf.download("MSFT", period="5d", interval="1h")  # Hourly (last 5 days only)
```

## Multiple Tickers at Once

```python
# Download several stocks simultaneously
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
data = yf.download(tickers, start="2023-01-01", end="2025-01-01")

# Access individual stock's close price
aapl_close = data["Close"]["AAPL"]
msft_close = data["Close"]["MSFT"]

# Compare returns
returns = data["Close"].pct_change()  # Daily percentage change
print(returns.tail())
```

## The Ticker Object (More Detail)

```python
ticker = yf.Ticker("AAPL")

# Price history
hist = ticker.history(period="1y")

# Company info
info = ticker.info
print(f"Company: {info.get('longName')}")
print(f"Sector: {info.get('sector')}")
print(f"Market Cap: ${info.get('marketCap', 0)/1e9:.1f}B")
print(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
print(f"Dividend Yield: {info.get('dividendYield', 0)*100:.2f}%")

# Financials
print(ticker.income_stmt)      # Revenue, net income, etc.
print(ticker.balance_sheet)    # Assets, liabilities
print(ticker.cashflow)         # Cash flow statement

# Dividends and splits
print(ticker.dividends)
print(ticker.splits)

# Analyst recommendations
print(ticker.recommendations)
```

## Working with the Data

```python
import yfinance as yf
import pandas as pd

# Fetch data
df = yf.download("AAPL", period="2y")

# Basic stats
print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
print(f"Trading days: {len(df)}")
print(f"Current price: ${df['Close'].iloc[-1]:.2f}")
print(f"52-week high: ${df['High'].tail(252).max():.2f}")
print(f"52-week low: ${df['Low'].tail(252).min():.2f}")

# Daily returns
df['Daily_Return'] = df['Close'].pct_change()
print(f"\nAvg daily return: {df['Daily_Return'].mean()*100:.3f}%")
print(f"Daily volatility: {df['Daily_Return'].std()*100:.3f}%")
print(f"Annualized return: {df['Daily_Return'].mean()*252*100:.1f}%")
print(f"Annualized volatility: {df['Daily_Return'].std()*(252**0.5)*100:.1f}%")

# Cumulative return
df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
print(f"Total return: {df['Cumulative_Return'].iloc[-1]*100:.1f}%")

# Drawdown (peak-to-trough decline)
df['Peak'] = df['Close'].cummax()
df['Drawdown'] = (df['Close'] - df['Peak']) / df['Peak']
print(f"Max drawdown: {df['Drawdown'].min()*100:.1f}%")
```

## Saving and Loading Data

```python
# Save to CSV (avoid re-downloading)
df = yf.download("AAPL", period="5y")
df.to_csv("aapl_5y.csv")

# Load from CSV
df = pd.read_csv("aapl_5y.csv", index_col="Date", parse_dates=True)
```

## Building a Data Pipeline

```python
def fetch_portfolio(tickers: list[str], period: str = "2y") -> dict[str, pd.DataFrame]:
    """Fetch data for multiple stocks, return as dict."""
    portfolio = {}
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, progress=False)
            if not data.empty:
                portfolio[ticker] = data
                print(f"  ✓ {ticker}: {len(data)} days")
            else:
                print(f"  ✗ {ticker}: no data")
        except Exception as e:
            print(f"  ✗ {ticker}: {e}")
    return portfolio

# Usage
my_stocks = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "JPM", "V", "JNJ"]
portfolio = fetch_portfolio(my_stocks)

# Quick summary
print(f"\n{'Ticker':<8} {'Price':>8} {'1Y Return':>10} {'Volatility':>12}")
print("-" * 42)
for ticker, df in portfolio.items():
    price = df['Close'].iloc[-1]
    ret_1y = (df['Close'].iloc[-1] / df['Close'].iloc[-252] - 1) * 100 if len(df) > 252 else 0
    vol = df['Close'].pct_change().std() * (252**0.5) * 100
    print(f"{ticker:<8} ${price:>7.2f} {ret_1y:>9.1f}% {vol:>10.1f}%")
```

## What You Learned

- **yfinance** — free stock data, no API key needed
- **OHLCV** — Open, High, Low, Close, Volume (the raw data)
- **Periods and intervals** — daily, weekly, monthly, intraday
- **Multiple tickers** — download and compare several stocks
- **Ticker object** — company info, financials, dividends
- **Basic metrics** — returns, volatility, drawdown
- **Data pipeline** — fetch, process, save for reuse

You have data. Now let's see it — candlestick charts, volume bars, and patterns that jump off the screen.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Visualization →](chapter-02-visualization.md)
