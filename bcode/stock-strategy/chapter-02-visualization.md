# Chapter 2: Visualization

[← Chapter 1: Fetching Data](chapter-01-fetch-data.md) | [Chapter 3: Technical Indicators →](chapter-03-indicators.md)

---

## Why Charts Matter

Numbers in a table are hard to read. A candlestick chart shows you price action, volume, and trend at a glance. You'll spot patterns in seconds that would take minutes to find in raw data.

> **Disclaimer:** This is educational content, not financial advice. Charts show history, not the future.

## Candlestick Charts with mplfinance

```python
import yfinance as yf
import mplfinance as mpf

# Fetch 3 months of Apple data
df = yf.download("AAPL", period="3mo")

# Basic candlestick chart
mpf.plot(df, type='candle', title='AAPL - 3 Month', style='charles')
```

Each candle shows one day: the body is open-to-close, wicks are high/low. Green = close > open (up day). Red = close < open (down day).

## Adding Volume and Moving Averages

```python
# Candlestick + volume + moving averages
mpf.plot(
    df,
    type='candle',
    style='charles',
    title='AAPL with Volume & Moving Averages',
    volume=True,
    mav=(20, 50),          # 20-day and 50-day moving averages
    figsize=(12, 8),
    tight_layout=True
)
```

Volume bars below the chart show trading activity. High volume on a move = conviction. Low volume = weak move that might reverse.

## Interactive Charts with Plotly

Static charts are fine for analysis. Interactive charts let you zoom, hover, and explore.

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = yf.download("AAPL", period="6mo")

# Create figure with secondary y-axis for volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.03, row_heights=[0.7, 0.3])

# Candlestick
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'], name='OHLC'
), row=1, col=1)

# 20-day moving average overlay
df['SMA20'] = df['Close'].rolling(20).mean()
fig.add_trace(go.Scatter(
    x=df.index, y=df['SMA20'], name='SMA 20',
    line=dict(color='orange', width=1.5)
), row=1, col=1)

# Volume bars (colored by direction)
colors = ['red' if c < o else 'green'
          for c, o in zip(df['Close'], df['Open'])]
fig.add_trace(go.Bar(
    x=df.index, y=df['Volume'], name='Volume',
    marker_color=colors, opacity=0.7
), row=2, col=1)

fig.update_layout(title='AAPL Interactive Chart',
                  xaxis_rangeslider_visible=False, height=600)
fig.show()
```

Hover over any candle to see exact OHLCV values. Drag to zoom into a specific date range.

## Multiple Stocks on One Chart

Comparing stocks requires normalizing prices (different stocks have different price levels).

```python
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]
data = yf.download(tickers, period="1y")

# Normalize to 100 at start date for fair comparison
normalized = data['Close'] / data['Close'].iloc[0] * 100

plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(normalized.index, normalized[ticker], label=ticker, linewidth=1.5)

plt.title("Normalized Price Comparison (Base = 100)")
plt.xlabel("Date")
plt.ylabel("Normalized Price")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

This shows *relative performance*. A stock at 130 gained 30% regardless of whether it started at $50 or $500.

## Saving Charts

```python
# mplfinance — save to file
mpf.plot(df, type='candle', volume=True, style='charles',
         savefig='aapl_chart.png')

# plotly — save as interactive HTML
fig.write_html("aapl_interactive.html")
```

## What You Learned

- **Candlestick charts** — OHLC in one visual (body = open/close, wicks = high/low)
- **Volume subplot** — confirms strength of price moves
- **Moving average overlay** — smooths noise, shows trend direction
- **mplfinance** — quick static charts with one line of code
- **plotly** — interactive charts you can zoom and hover
- **Normalization** — compare stocks with different price levels fairly

Charts are your first filter. Now let's add the indicators that tell you *when* something interesting is happening.

---

[← Chapter 1: Fetching Data](chapter-01-fetch-data.md) | [Chapter 3: Technical Indicators →](chapter-03-indicators.md)
