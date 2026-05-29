# Chapter 3: Technical Analysis

[prev: Chapter 2 - Statistics](chapter-02-statistics.md) | [next: Chapter 4 - Backtesting](chapter-04-backtesting.md)

---

Technical analysis uses price and volume history to identify patterns and generate trading signals. Here we implement the most common indicators from scratch.

## Simple Moving Average (SMA)

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
close = df["Close"]

# SMA from scratch
def sma(series, window):
    return series.rolling(window=window).mean()

df["SMA_20"] = sma(close, 20)
df["SMA_50"] = sma(close, 50)

plt.figure(figsize=(12, 5))
plt.plot(close, label="Price", alpha=0.7)
plt.plot(df["SMA_20"], label="SMA 20")
plt.plot(df["SMA_50"], label="SMA 50")
plt.title("AAPL with SMA")
plt.legend()
plt.savefig("sma.png")
plt.close()
```

## Exponential Moving Average (EMA)

EMA gives more weight to recent prices:

```python
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
close = df["Close"]

# EMA from scratch
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

df["EMA_12"] = ema(close, 12)
df["EMA_26"] = ema(close, 26)
```

## Moving Average Crossover Signal

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
close = df["Close"]

df["SMA_20"] = close.rolling(20).mean()
df["SMA_50"] = close.rolling(50).mean()

# Signal: 1 when short MA > long MA, 0 otherwise
df["signal"] = np.where(df["SMA_20"] > df["SMA_50"], 1, 0)
df["position"] = df["signal"].diff()

plt.figure(figsize=(12, 5))
plt.plot(close, alpha=0.7, label="Price")
plt.plot(df["SMA_20"], label="SMA 20")
plt.plot(df["SMA_50"], label="SMA 50")

# Mark buy/sell points
buys = df[df["position"] == 1]
sells = df[df["position"] == -1]
plt.scatter(buys.index, close[buys.index], marker="^", color="green", s=100, label="Buy")
plt.scatter(sells.index, close[sells.index], marker="v", color="red", s=100, label="Sell")

plt.title("SMA Crossover Strategy")
plt.legend()
plt.savefig("sma_crossover.png")
plt.close()
```

## RSI (Relative Strength Index)

RSI measures momentum on a 0-100 scale. Above 70 = overbought, below 30 = oversold.

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def rsi(series, period=14):
    """Calculate RSI from scratch."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
df["RSI"] = rsi(df["Close"], 14)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
ax1.plot(df["Close"])
ax1.set_title("AAPL Price")

ax2.plot(df["RSI"])
ax2.axhline(70, color="red", linestyle="--", alpha=0.7)
ax2.axhline(30, color="green", linestyle="--", alpha=0.7)
ax2.set_title("RSI (14)")
ax2.set_ylim(0, 100)

plt.tight_layout()
plt.savefig("rsi.png")
plt.close()
```

## MACD (Moving Average Convergence Divergence)

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def macd(series, fast=12, slow=26, signal=9):
    """Calculate MACD from scratch."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
df["MACD"], df["Signal"], df["Hist"] = macd(df["Close"])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
ax1.plot(df["Close"])
ax1.set_title("AAPL Price")

ax2.plot(df["MACD"], label="MACD")
ax2.plot(df["Signal"], label="Signal")
ax2.bar(df.index, df["Hist"], alpha=0.3, color="gray", label="Histogram")
ax2.axhline(0, color="black", linewidth=0.5)
ax2.legend()
ax2.set_title("MACD")

plt.tight_layout()
plt.savefig("macd.png")
plt.close()
```

## Bollinger Bands

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def bollinger_bands(series, window=20, num_std=2):
    """Calculate Bollinger Bands."""
    middle = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
close = df["Close"]
upper, middle, lower = bollinger_bands(close)

plt.figure(figsize=(12, 5))
plt.plot(close, label="Price", alpha=0.7)
plt.plot(upper, label="Upper Band", linestyle="--", color="red")
plt.plot(middle, label="Middle (SMA 20)", color="orange")
plt.plot(lower, label="Lower Band", linestyle="--", color="green")
plt.fill_between(close.index, lower, upper, alpha=0.1)
plt.title("Bollinger Bands")
plt.legend()
plt.savefig("bollinger.png")
plt.close()
```

## ATR (Average True Range)

ATR measures volatility — useful for position sizing and stop-loss placement:

```python
import numpy as np
import pandas as pd
import yfinance as yf

def atr(df, period=14):
    """Calculate Average True Range."""
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
df["ATR"] = atr(df, 14)
print(df[["Close", "ATR"]].tail())
```

## Volume Indicators

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

# On-Balance Volume (OBV)
def obv(df):
    """On-Balance Volume: cumulative volume weighted by price direction."""
    direction = np.sign(df["Close"].diff())
    return (direction * df["Volume"]).cumsum()

# Volume Weighted Average Price (VWAP) - intraday approximation
def vwap(df):
    """Simplified VWAP using typical price."""
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    return (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()

df["OBV"] = obv(df)
df["VWAP"] = vwap(df)
print(df[["Close", "Volume", "OBV"]].tail())
```

## Support and Resistance

```python
import numpy as np
import pandas as pd
import yfinance as yf

def find_support_resistance(df, window=20, threshold=3):
    """Find support/resistance levels using local min/max."""
    highs = df["High"].rolling(window, center=True).max()
    lows = df["Low"].rolling(window, center=True).min()

    # Resistance: points where high equals rolling max
    resistance_mask = df["High"] == highs
    resistance_levels = df["High"][resistance_mask]

    # Support: points where low equals rolling min
    support_mask = df["Low"] == lows
    support_levels = df["Low"][support_mask]

    return support_levels, resistance_levels

df = yf.download("AAPL", start="2023-06-01", end="2024-01-01")
support, resistance = find_support_resistance(df)
print(f"Support levels: {support.tail()}")
print(f"Resistance levels: {resistance.tail()}")
```

## Using ta-lib

ta-lib provides optimized C implementations of 150+ indicators:

```python
import talib
import yfinance as yf

df = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

# All indicators in one call
df["RSI"] = talib.RSI(df["Close"], timeperiod=14)
df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = talib.MACD(df["Close"])
df["Upper"], df["Middle"], df["Lower"] = talib.BBANDS(df["Close"])
df["ATR"] = talib.ATR(df["High"], df["Low"], df["Close"], timeperiod=14)
df["ADX"] = talib.ADX(df["High"], df["Low"], df["Close"], timeperiod=14)

print(df[["Close", "RSI", "MACD", "ATR", "ADX"]].tail())
```

Note: ta-lib requires separate installation of the C library. On Windows use `conda install -c conda-forge ta-lib`.

## Combining Indicators for a Signal

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
close = df["Close"]

# Calculate indicators
df["SMA_20"] = close.rolling(20).mean()
df["SMA_50"] = close.rolling(50).mean()

delta = close.diff()
gain = delta.where(delta > 0, 0.0)
loss = -delta.where(delta < 0, 0.0)
avg_gain = gain.ewm(com=13, min_periods=14).mean()
avg_loss = loss.ewm(com=13, min_periods=14).mean()
df["RSI"] = 100 - (100 / (1 + avg_gain / avg_loss))

# Combined signal
df["signal"] = 0
df.loc[(df["SMA_20"] > df["SMA_50"]) & (df["RSI"] < 30), "signal"] = 1   # Buy
df.loc[(df["SMA_20"] < df["SMA_50"]) & (df["RSI"] > 70), "signal"] = -1  # Sell

buy_signals = df[df["signal"] == 1]
sell_signals = df[df["signal"] == -1]
print(f"Buy signals: {len(buy_signals)}")
print(f"Sell signals: {len(sell_signals)}")
```

---

## Key Takeaways

- Implement indicators from scratch to understand them before using libraries
- No single indicator is reliable alone — combine multiple for confirmation
- RSI and Bollinger Bands work best in ranging markets
- MACD and moving average crossovers work best in trending markets
- ATR is essential for dynamic stop-loss and position sizing
- ta-lib is faster but adds a dependency; pandas implementations are portable

---

[prev: Chapter 2 - Statistics](chapter-02-statistics.md) | [next: Chapter 4 - Backtesting](chapter-04-backtesting.md)
