# Chapter 9: Stock Screener

[← Chapter 8: Portfolio](chapter-08-portfolio.md) | [Chapter 10: Alerts & Automation →](chapter-10-alerts.md)

---

## Why Screen?

There are ~5,000 stocks on US exchanges. You can't analyze them all manually. A screener filters the universe down to a watchlist of candidates that match YOUR criteria — not some newsletter's picks.

> **Disclaimer:** This is educational content, not financial advice. Passing a screen doesn't mean a stock will go up.

## Define Your Criteria

```python
import yfinance as yf
import pandas as pd
import numpy as np

def screen_stock(ticker):
    """Fetch fundamentals and technicals for screening."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo")

        if hist.empty or not info.get('marketCap'):
            return None

        # Calculate RSI
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]

        return {
            'ticker': ticker,
            'name': info.get('shortName', ''),
            'sector': info.get('sector', 'N/A'),
            'market_cap_B': round(info.get('marketCap', 0) / 1e9, 1),
            'pe_ratio': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'profit_margin': info.get('profitMargin'),
            'debt_equity': info.get('debtToEquity'),
            'rsi': round(rsi, 1),
            'avg_volume': int(hist['Volume'].mean()),
            'price': round(hist['Close'].iloc[-1], 2),
        }
    except Exception:
        return None
```

## Screening a Universe

```python
# Large-cap tech universe (expand this for broader screening)
universe = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
    "ORCL", "CRM", "AMD", "ADBE", "INTC", "CSCO", "NFLX", "QCOM",
    "IBM", "NOW", "UBER", "SQ", "SHOP", "SNOW", "PLTR", "PANW"
]

print("Screening stocks...")
results = []
for ticker in universe:
    data = screen_stock(ticker)
    if data:
        results.append(data)
        print(f"  ✓ {ticker}")

df = pd.DataFrame(results).set_index('ticker')
print(f"\nScreened {len(df)} stocks successfully")
```

## Applying Filters

```python
def apply_filters(df, filters):
    """Apply screening filters and return matching stocks."""
    filtered = df.copy()

    for column, (op, value) in filters.items():
        if column not in filtered.columns:
            continue
        col = filtered[column]
        if op == '>': filtered = filtered[col > value]
        elif op == '<': filtered = filtered[col < value]
        elif op == '>=': filtered = filtered[col >= value]
        elif op == '<=': filtered = filtered[col <= value]
        elif op == '==': filtered = filtered[col == value]

    return filtered

# Example: "Large-cap tech with RSI < 35 and positive earnings growth"
filters = {
    'market_cap_B': ('>', 50),           # Large cap (>$50B)
    'rsi': ('<', 35),                     # Oversold
    'earnings_growth': ('>', 0),          # Positive earnings growth
}

watchlist = apply_filters(df, filters)
print(f"\n--- Watchlist: Oversold Large-Cap Tech with Growth ---")
print(f"Found {len(watchlist)} stocks matching criteria:\n")
if not watchlist.empty:
    print(watchlist[['name', 'market_cap_B', 'pe_ratio', 'rsi', 'earnings_growth']].to_string())
else:
    print("No stocks match all criteria right now.")
    print("Try relaxing filters (RSI < 40, or market_cap > 20B)")
```

## Composite Scoring

Rank stocks by multiple factors combined into one score.

```python
def composite_score(df):
    """Rank stocks by composite score (0-100). Higher = more attractive."""
    scored = df.copy()

    # Normalize each metric to 0-1 (handle direction)
    # Lower P/E is better → invert
    if scored['pe_ratio'].notna().any():
        pe_rank = scored['pe_ratio'].rank(ascending=True, pct=True)
    else:
        pe_rank = 0.5

    # Higher growth is better
    growth_rank = scored['revenue_growth'].rank(ascending=False, pct=True)

    # Higher margin is better
    margin_rank = scored['profit_margin'].rank(ascending=False, pct=True)

    # Lower RSI is better (more oversold = more opportunity)
    rsi_rank = scored['rsi'].rank(ascending=True, pct=True)

    # Lower debt is better
    debt_rank = scored['debt_equity'].rank(ascending=True, pct=True)

    # Weighted composite (adjust weights to your preference)
    scored['score'] = (
        pe_rank * 0.20 +
        growth_rank * 0.25 +
        margin_rank * 0.20 +
        rsi_rank * 0.20 +
        debt_rank * 0.15
    ) * 100

    return scored.sort_values('score', ascending=False)

ranked = composite_score(df)
print("\n--- Top 10 by Composite Score ---")
print(ranked[['name', 'score', 'pe_ratio', 'revenue_growth', 'rsi']].head(10).to_string())
```

## Building a Watchlist

```python
def build_watchlist(ranked, top_n=5):
    """Create a formatted watchlist from top-ranked stocks."""
    watchlist = ranked.head(top_n)

    print(f"\n{'='*60}")
    print(f"  WATCHLIST — Top {top_n} Candidates")
    print(f"{'='*60}")

    for ticker, row in watchlist.iterrows():
        print(f"\n  {ticker} — {row['name']}")
        print(f"    Score: {row['score']:.0f}/100")
        print(f"    Price: ${row['price']:.2f} | P/E: {row.get('pe_ratio', 'N/A')}")
        print(f"    RSI: {row['rsi']:.0f} | Rev Growth: {row['revenue_growth']*100:+.1f}%")
        reasons = []
        if row['rsi'] < 35: reasons.append("oversold")
        if row.get('revenue_growth', 0) > 0.15: reasons.append("strong growth")
        if row.get('pe_ratio') and row['pe_ratio'] < 20: reasons.append("low valuation")
        if reasons:
            print(f"    Why: {', '.join(reasons)}")

    print(f"\n{'='*60}")
    return watchlist

build_watchlist(ranked)
```

## Saving and Updating

```python
# Save screener results
ranked.to_csv("screener_results.csv")
print("Saved to screener_results.csv")

# Load and compare with previous run
# previous = pd.read_csv("screener_results_last_week.csv", index_col='ticker')
# new_entries = set(ranked.head(10).index) - set(previous.head(10).index)
# print(f"New in top 10: {new_entries}")
```

## Caveats

- **Screening is step 1, not the final answer** — always do deeper research
- **yfinance data can lag** — don't rely on it for real-time decisions
- **Survivorship bias** — your universe only includes stocks that exist today
- **Screens work until they don't** — when everyone uses the same screen, the edge disappears

## What You Learned

- **Stock screener** — filter thousands of stocks by your criteria
- **Fundamental filters** — market cap, P/E, growth, margins
- **Technical filters** — RSI, volume, price relative to moving averages
- **Composite scoring** — rank by multiple weighted factors
- **Watchlist** — actionable output from your screening process

You have a watchlist. Now let's automate the monitoring — get alerts when conditions trigger, without watching charts all day.

---

[← Chapter 8: Portfolio](chapter-08-portfolio.md) | [Chapter 10: Alerts & Automation →](chapter-10-alerts.md)
