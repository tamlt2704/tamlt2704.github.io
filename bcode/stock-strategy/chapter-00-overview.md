# Chapter 0: Before You Start

[Chapter 1: Fetching Data →](chapter-01-fetch-data.md)

---

## The Honest Truth

Before we write a single line of code, let's be clear:

- **80% of day traders lose money.** This course doesn't teach day trading.
- **You will not beat the S&P 500 consistently.** Index funds exist for a reason.
- **Backtesting is not prediction.** A strategy that worked in 2020 might fail in 2025.
- **This is a tool, not a crystal ball.** Data helps you make *informed* decisions, not *guaranteed* ones.

What this course IS good for:
- Understanding what you own and why
- Screening stocks based on YOUR criteria (not some YouTuber's)
- Testing "what if" scenarios before risking real money
- Building alerts so you don't have to watch charts all day
- Making your portfolio decisions data-driven instead of emotional

## Setup

```bash
pip install yfinance pandas numpy matplotlib plotly ta
```

| Library | Purpose |
|---|---|
| `yfinance` | Free stock data from Yahoo Finance |
| `pandas` | DataFrames for time-series analysis |
| `numpy` | Math operations |
| `matplotlib` | Static charts |
| `plotly` | Interactive charts |
| `ta` | Technical analysis indicators (optional) |

### Quick Test

```python
import yfinance as yf

# Fetch Apple's last month of data
aapl = yf.download("AAPL", period="1mo")
print(aapl.tail())
print(f"\nLatest close: ${aapl['Close'].iloc[-1]:.2f}")
```

If that prints a table of prices, you're ready.

## What Is Stock Data?

Every trading day, a stock has:

| Field | Meaning |
|---|---|
| **Open** | Price at market open (9:30 AM ET) |
| **High** | Highest price during the day |
| **Low** | Lowest price during the day |
| **Close** | Price at market close (4:00 PM ET) |
| **Volume** | Number of shares traded |
| **Adj Close** | Close price adjusted for splits/dividends |

This is called **OHLCV** data. It's the foundation of everything we'll build.

## The Strategies We'll Explore

| Strategy | Type | Idea |
|---|---|---|
| Moving Average Crossover | Trend-following | Buy when short MA crosses above long MA |
| RSI Mean Reversion | Mean-reversion | Buy when oversold (RSI < 30), sell when overbought |
| Momentum | Trend-following | Buy winners, sell losers (relative strength) |
| Value + Quality | Fundamental | Buy cheap stocks with strong earnings |
| Dollar-Cost Averaging | Passive | Buy fixed amount regularly regardless of price |

We'll implement and backtest each one. You'll see which ones actually work (spoiler: simpler is usually better).

## The Cast

| Character | Role |
|---|---|
| **You** | Developer who wants data-driven investing |
| **The Market** | Unpredictable, humbling, occasionally generous |
| **Your Emotions** | The real enemy (FOMO, panic selling, overconfidence) |
| **The Backtest** | Your reality check before risking real money |

## The Rules

1. **Never invest money you can't afford to lose**
2. **Backtest before you trade** — if it doesn't work on history, it won't work live
3. **Start with paper trading** — simulate with fake money first
4. **Diversify** — no single stock should be >10% of your portfolio
5. **Have an exit plan** — know when you'll sell BEFORE you buy

Let's fetch some data.

---

[Chapter 1: Fetching Data →](chapter-01-fetch-data.md)
