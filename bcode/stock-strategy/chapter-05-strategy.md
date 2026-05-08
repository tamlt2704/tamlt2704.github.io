# Chapter 5: Building a Trading Strategy

[← Chapter 4: Fundamentals](chapter-04-fundamentals.md) | [Chapter 6: Backtesting →](chapter-06-backtest.md)

---

## What Is a Strategy?

A strategy is a set of rules that tell you when to buy and when to sell. No emotions, no gut feelings — just code.

Every strategy needs:
1. **Entry signal** — condition to buy
2. **Exit signal** — condition to sell
3. **Position sizing** — how much to buy (covered in Chapter 7)

> **Disclaimer:** This is educational content, not financial advice. Past signals don't guarantee future results.

## Strategy 1: Golden Cross (Trend Following)

**Idea:** Buy when the 50-day SMA crosses above the 200-day SMA. Sell when it crosses below.

**Why it works (sometimes):** Captures long-term trends. Avoids buying in downtrends.

```python
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2025-01-01")

# Calculate moving averages
df['SMA_50'] = df['Close'].rolling(50).mean()
df['SMA_200'] = df['Close'].rolling(200).mean()

# Generate signals
df['Signal'] = 0
df.loc[df['SMA_50'] > df['SMA_200'], 'Signal'] = 1   # Bullish
df.loc[df['SMA_50'] <= df['SMA_200'], 'Signal'] = -1  # Bearish

# Find crossover points (signal changes)
df['Position'] = df['Signal'].diff()

# Plot
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Close'], label='Price', alpha=0.7)
plt.plot(df.index, df['SMA_50'], label='SMA 50', linewidth=1.5)
plt.plot(df.index, df['SMA_200'], label='SMA 200', linewidth=1.5)

# Mark buy/sell signals
buys = df[df['Position'] == 2]
sells = df[df['Position'] == -2]
plt.scatter(buys.index, buys['Close'], marker='^', color='green', s=100, label='Buy')
plt.scatter(sells.index, sells['Close'], marker='v', color='red', s=100, label='Sell')

plt.title("Golden Cross Strategy — AAPL")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

**Weakness:** Slow. By the time the cross happens, you've missed the first part of the move. Whipsaws in sideways markets.

## Strategy 2: RSI Mean Reversion

**Idea:** Buy when RSI drops below 30 (oversold). Sell when RSI rises above 70 (overbought).

**Why it works (sometimes):** Stocks tend to bounce after sharp drops. Overbought stocks tend to pull back.

```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df = yf.download("AAPL", start="2020-01-01", end="2025-01-01")
df['RSI'] = calculate_rsi(df['Close'])

# Signals
df['Signal'] = 0
df.loc[df['RSI'] < 30, 'Signal'] = 1    # Buy when oversold
df.loc[df['RSI'] > 70, 'Signal'] = -1   # Sell when overbought

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax1.plot(df.index, df['Close'], label='Price')
buy_signals = df[df['Signal'] == 1]
sell_signals = df[df['Signal'] == -1]
ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=80)
ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=80)
ax1.set_title("RSI Mean Reversion — AAPL")
ax1.legend()

ax2.plot(df.index, df['RSI'], color='purple')
ax2.axhline(70, color='red', linestyle='--')
ax2.axhline(30, color='green', linestyle='--')
ax2.fill_between(df.index, 70, 100, alpha=0.1, color='red')
ax2.fill_between(df.index, 0, 30, alpha=0.1, color='green')
ax2.set_ylabel("RSI")
plt.tight_layout()
plt.show()
```

**Weakness:** In a strong downtrend, RSI can stay below 30 for weeks while the stock keeps falling ("catching a falling knife").

## Strategy 3: Momentum (Buy Winners)

**Idea:** Buy the top N performers over the last 3-6 months. Rebalance monthly. Winners tend to keep winning (for a while).

```python
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ"]
data = yf.download(tickers, start="2022-01-01", end="2025-01-01")['Close']

# Calculate 3-month (63 trading days) momentum
momentum = data.pct_change(63)  # 63-day return

# Rank stocks each day — top 3 get a buy signal
ranks = momentum.rank(axis=1, ascending=False)
signals = (ranks <= 3).astype(int)  # 1 = hold, 0 = don't hold

# Show latest rankings
latest = momentum.iloc[-1].sort_values(ascending=False)
print("Current 3-Month Momentum Ranking:")
print("-" * 35)
for i, (ticker, ret) in enumerate(latest.items(), 1):
    flag = "← BUY" if i <= 3 else ""
    print(f"  {i}. {ticker}: {ret*100:+.1f}% {flag}")
```

**Weakness:** Momentum crashes hard during market reversals. Last year's winners can become this year's losers overnight.

## Combining Signals

No single indicator is reliable alone. Combine them for higher-confidence signals:

```python
df = yf.download("AAPL", start="2022-01-01", end="2025-01-01")
df['SMA_50'] = df['Close'].rolling(50).mean()
df['RSI'] = calculate_rsi(df['Close'])

# Combined signal: buy only when BOTH conditions are true
df['Combined'] = 0
df.loc[(df['Close'] > df['SMA_50']) & (df['RSI'] < 40), 'Combined'] = 1   # Buy
df.loc[(df['Close'] < df['SMA_50']) & (df['RSI'] > 60), 'Combined'] = -1  # Sell

combined_buys = df[df['Combined'] == 1]
print(f"Combined buy signals: {len(combined_buys)} days out of {len(df)}")
print("Fewer signals = higher conviction (in theory)")
```

## What You Learned

- **Strategy = rules** — entry signal + exit signal, no emotions
- **Golden Cross** — trend following, slow but catches big moves
- **RSI Mean Reversion** — buy oversold, sell overbought
- **Momentum** — buy recent winners, rebalance regularly
- **Every strategy has weaknesses** — no holy grail exists
- **Combining signals** — reduces false positives, increases conviction

You have strategies. But do they actually make money? There's only one way to find out — backtest them on historical data.

---

[← Chapter 4: Fundamentals](chapter-04-fundamentals.md) | [Chapter 6: Backtesting →](chapter-06-backtest.md)
