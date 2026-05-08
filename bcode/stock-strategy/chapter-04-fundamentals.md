# Chapter 4: Fundamental Analysis

[← Chapter 3: Technical Indicators](chapter-03-indicators.md) | [Chapter 5: Strategy →](chapter-05-strategy.md)

---

## Price vs. Value

Technical analysis looks at *price*. Fundamental analysis looks at the *business*. A stock can be expensive (high price) but cheap (low valuation relative to earnings). Or vice versa.

> **Disclaimer:** This is educational content, not financial advice. Fundamentals change, and "cheap" stocks can stay cheap for years.

## Key Metrics with yfinance

```python
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")
info = ticker.info

# Valuation
pe_ratio = info.get('trailingPE')           # Price / Earnings
forward_pe = info.get('forwardPE')          # Price / Expected Earnings
peg_ratio = info.get('pegRatio')            # PE / Growth rate (< 1 = undervalued)

# Profitability
eps = info.get('trailingEps')               # Earnings per share
profit_margin = info.get('profitMargin')    # Net income / Revenue
roe = info.get('returnOnEquity')            # Net income / Shareholder equity

# Growth
revenue_growth = info.get('revenueGrowth')  # YoY revenue growth
earnings_growth = info.get('earningsGrowth')

# Financial health
debt_to_equity = info.get('debtToEquity')   # Total debt / Equity (lower = safer)
current_ratio = info.get('currentRatio')    # Current assets / Current liabilities
free_cash_flow = info.get('freeCashflow')   # Cash generated after expenses

print(f"{'Metric':<20} {'Value':>12}")
print("-" * 34)
print(f"{'P/E Ratio':<20} {pe_ratio:>12.1f}")
print(f"{'Forward P/E':<20} {forward_pe:>12.1f}")
print(f"{'EPS':<20} ${eps:>11.2f}")
print(f"{'Revenue Growth':<20} {revenue_growth*100:>11.1f}%")
print(f"{'Profit Margin':<20} {profit_margin*100:>11.1f}%")
print(f"{'Debt/Equity':<20} {debt_to_equity:>12.1f}")
print(f"{'Free Cash Flow':<20} ${free_cash_flow/1e9:>9.1f}B")
```

## What Each Metric Tells You

| Metric | Good Sign | Red Flag |
|--------|-----------|----------|
| P/E Ratio | < sector average | > 50 (unless high growth) |
| Revenue Growth | > 10% YoY | Negative for 2+ quarters |
| Profit Margin | > 15% | Declining trend |
| Debt/Equity | < 100 | > 200 |
| Free Cash Flow | Positive, growing | Negative |
| ROE | > 15% | < 5% |

## Comparing Sector Peers

```python
def get_fundamentals(ticker_symbol):
    """Extract key fundamentals for a single stock."""
    try:
        info = yf.Ticker(ticker_symbol).info
        return {
            'Ticker': ticker_symbol,
            'Name': info.get('shortName', 'N/A'),
            'P/E': info.get('trailingPE'),
            'Fwd P/E': info.get('forwardPE'),
            'EPS': info.get('trailingEps'),
            'Rev Growth': info.get('revenueGrowth'),
            'Margin': info.get('profitMargin'),
            'D/E': info.get('debtToEquity'),
            'FCF ($B)': round(info.get('freeCashflow', 0) / 1e9, 1),
            'Mkt Cap ($B)': round(info.get('marketCap', 0) / 1e9, 0),
        }
    except Exception as e:
        return {'Ticker': ticker_symbol, 'Error': str(e)}

# Compare big tech
tech_peers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
fundamentals = pd.DataFrame([get_fundamentals(t) for t in tech_peers])
fundamentals = fundamentals.set_index('Ticker')
print(fundamentals.to_string())
```

This gives you a side-by-side comparison. Which stock is cheapest relative to earnings? Which has the best growth? Which carries the most debt?

## Building a Simple Value Score

Combine multiple metrics into one score. This is opinionated — adjust weights to match YOUR investing philosophy.

```python
import numpy as np

def value_score(info):
    """Score a stock 0-100 based on fundamentals. Higher = more attractive."""
    score = 0
    max_score = 0

    # Low P/E is better (weight: 25)
    pe = info.get('trailingPE')
    if pe and pe > 0:
        max_score += 25
        if pe < 15: score += 25
        elif pe < 25: score += 15
        elif pe < 35: score += 5

    # Revenue growth (weight: 25)
    growth = info.get('revenueGrowth')
    if growth is not None:
        max_score += 25
        if growth > 0.20: score += 25
        elif growth > 0.10: score += 20
        elif growth > 0.05: score += 10
        elif growth > 0: score += 5

    # Profit margin (weight: 25)
    margin = info.get('profitMargin')
    if margin is not None:
        max_score += 25
        if margin > 0.25: score += 25
        elif margin > 0.15: score += 20
        elif margin > 0.05: score += 10

    # Low debt (weight: 25)
    de = info.get('debtToEquity')
    if de is not None:
        max_score += 25
        if de < 50: score += 25
        elif de < 100: score += 20
        elif de < 150: score += 10

    return round(score / max_score * 100) if max_score > 0 else None

# Score our tech peers
for ticker in tech_peers:
    info = yf.Ticker(ticker).info
    s = value_score(info)
    print(f"{ticker}: {s}/100")
```

## Revenue and Earnings Trends

```python
ticker = yf.Ticker("AAPL")
income = ticker.income_stmt

# Revenue trend (last 4 years)
revenue = income.loc['Total Revenue'] / 1e9  # Convert to billions
print("Annual Revenue ($B):")
print(revenue.sort_index())

# Plot it
import matplotlib.pyplot as plt
revenue_sorted = revenue.sort_index()
plt.figure(figsize=(8, 4))
plt.bar(revenue_sorted.index.year, revenue_sorted.values, color='steelblue')
plt.title("AAPL Annual Revenue ($B)")
plt.ylabel("Revenue ($B)")
plt.grid(axis='y', alpha=0.3)
plt.show()
```

## Caveats

- **yfinance data can be stale** — it's scraped from Yahoo, not a real-time feed
- **Metrics vary by sector** — a P/E of 30 is normal for tech, expensive for utilities
- **Backward-looking** — last year's earnings don't guarantee next year's
- **One metric is never enough** — always look at the full picture

## What You Learned

- **P/E ratio** — what you pay per dollar of earnings
- **Revenue growth** — is the business expanding?
- **Profit margin** — how much revenue becomes profit
- **Debt/Equity** — financial health and risk
- **Free cash flow** — actual cash the business generates
- **Peer comparison** — context matters more than absolute numbers
- **Value score** — combine metrics into a single ranking

You can now read both the chart (technical) and the business (fundamental). Time to turn these insights into actual trading strategies.

---

[← Chapter 3: Technical Indicators](chapter-03-indicators.md) | [Chapter 5: Strategy →](chapter-05-strategy.md)
