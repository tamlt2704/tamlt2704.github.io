# Chapter 3: Technical Indicators

[← Chapter 2: Visualization](chapter-02-visualization.md) | [Chapter 4: Fundamentals →](chapter-04-fundamentals.md)

---

## What Are Indicators?

Indicators are math applied to price/volume data. They don't predict the future — they summarize what's happening *now*. Three categories:

| Type | Measures | Examples |
|------|----------|----------|
| **Trend** | Direction of price movement | SMA, EMA, MACD |
| **Momentum** | Speed/strength of movement | RSI |
| **Volatility** | How much price swings | Bollinger Bands |

> **Disclaimer:** This is educational content, not financial advice. No indicator works all the time.

## SMA — Simple Moving Average

Average of the last N closing prices. Smooths noise, shows trend.

```python
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="1y")

# From scratch
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Price', alpha=0.7)
plt.plot(df.index, df['SMA_20'], label='SMA 20', linewidth=1.5)
plt.plot(df.index, df['SMA_50'], label='SMA 50', linewidth=1.5)
plt.title("AAPL — Simple Moving Averages")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

Price above SMA = uptrend. Price below = downtrend. When short SMA crosses above long SMA = bullish signal (the "Golden Cross").

## EMA — Exponential Moving Average

Weights recent prices more heavily. Reacts faster than SMA.

```python
# From scratch — EMA formula
df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
```

## RSI — Relative Strength Index

Measures momentum on a 0-100 scale. Above 70 = overbought. Below 30 = oversold.

```python
# RSI from scratch
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['Close'])

# Plot RSI with overbought/oversold zones
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
ax1.plot(df.index, df['Close'])
ax1.set_title("AAPL Price")
ax2.plot(df.index, df['RSI'], color='purple')
ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
ax2.fill_between(df.index, 70, 100, alpha=0.1, color='red')
ax2.fill_between(df.index, 0, 30, alpha=0.1, color='green')
ax2.set_title("RSI (14)")
ax2.set_ylim(0, 100)
plt.tight_layout()
plt.show()
```

## MACD — Moving Average Convergence Divergence

Shows trend direction AND momentum. MACD line = EMA12 - EMA26. Signal line = EMA9 of MACD.

```python
# MACD from scratch
df['MACD'] = df['EMA_12'] - df['EMA_26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histogram'] = df['MACD'] - df['Signal']

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
ax1.plot(df.index, df['Close'], label='Price')
ax1.set_title("AAPL Price")
ax2.plot(df.index, df['MACD'], label='MACD', color='blue')
ax2.plot(df.index, df['Signal'], label='Signal', color='orange')
ax2.bar(df.index, df['Histogram'], color=['green' if v >= 0 else 'red'
        for v in df['Histogram']], alpha=0.5)
ax2.set_title("MACD")
ax2.legend()
plt.tight_layout()
plt.show()
```

Buy signal: MACD crosses above Signal. Sell signal: MACD crosses below Signal.

## Bollinger Bands

Price channel based on volatility. Middle = SMA20. Upper/Lower = ±2 standard deviations.

```python
# Bollinger Bands from scratch
df['BB_Mid'] = df['Close'].rolling(20).mean()
df['BB_Std'] = df['Close'].rolling(20).std()
df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Price', color='black', linewidth=1)
plt.plot(df.index, df['BB_Upper'], 'r--', alpha=0.7, label='Upper Band')
plt.plot(df.index, df['BB_Lower'], 'g--', alpha=0.7, label='Lower Band')
plt.fill_between(df.index, df['BB_Upper'], df['BB_Lower'], alpha=0.1)
plt.title("AAPL — Bollinger Bands")
plt.legend()
plt.show()
```

Price touching upper band = potentially overbought. Touching lower = potentially oversold. Bands squeezing = low volatility, big move coming (direction unknown).

## The `ta` Library Shortcut

Once you understand the math, use `ta` to save time:

```python
import ta

df['RSI_ta'] = ta.momentum.RSIIndicator(df['Close']).rsi()
macd = ta.trend.MACD(df['Close'])
df['MACD_ta'] = macd.macd()
df['Signal_ta'] = macd.macd_signal()
bb = ta.volatility.BollingerBands(df['Close'])
df['BB_Upper_ta'] = bb.bollinger_hband()
df['BB_Lower_ta'] = bb.bollinger_lband()
```

Same results, less code. But knowing the math helps you understand *why* an indicator gives a signal.

## What You Learned

- **SMA/EMA** — trend direction (price above = bullish, below = bearish)
- **RSI** — momentum (>70 overbought, <30 oversold)
- **MACD** — trend + momentum (crossovers = signals)
- **Bollinger Bands** — volatility (squeeze = breakout coming)
- **From scratch** — pandas rolling/ewm makes implementation simple
- **`ta` library** — production shortcut once you understand the math

Indicators tell you about price action. But a stock's *value* depends on the business behind it. Let's look at fundamentals.

---

[← Chapter 2: Visualization](chapter-02-visualization.md) | [Chapter 4: Fundamentals →](chapter-04-fundamentals.md)
