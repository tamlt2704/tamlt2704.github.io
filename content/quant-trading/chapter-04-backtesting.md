# Chapter 4: Backtesting

[prev: Chapter 3 - Technical Analysis](chapter-03-technical.md) | [next: Chapter 5 - Strategies](chapter-05-strategies.md)

---

Backtesting simulates a strategy on historical data to estimate how it would have performed. It is the most critical step before risking real capital.

**Warning: A profitable backtest does NOT guarantee future profits. Markets change, and backtests are prone to many biases.**

## Vectorized Backtesting with pandas

The fastest approach — compute signals and returns as vectors:

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Strategy: SMA crossover
df["SMA_20"] = close.rolling(20).mean()
df["SMA_50"] = close.rolling(50).mean()

# Signal: 1 = long, 0 = flat
df["signal"] = np.where(df["SMA_20"] > df["SMA_50"], 1, 0)

# Shift signal by 1 day (trade on next open, avoid look-ahead)
df["position"] = df["signal"].shift(1)

# Daily returns
df["market_return"] = close.pct_change()
df["strategy_return"] = df["position"] * df["market_return"]

# Cumulative returns
df["market_cumulative"] = (1 + df["market_return"]).cumprod()
df["strategy_cumulative"] = (1 + df["strategy_return"]).cumprod()

# Plot
plt.figure(figsize=(12, 5))
plt.plot(df["market_cumulative"], label="Buy & Hold")
plt.plot(df["strategy_cumulative"], label="SMA Crossover")
plt.title("SMA Crossover Backtest")
plt.legend()
plt.savefig("backtest_sma.png")
plt.close()

# Performance
total_return = df["strategy_cumulative"].iloc[-1] - 1
annual_return = (1 + total_return) ** (252 / len(df.dropna())) - 1
sharpe = df["strategy_return"].mean() / df["strategy_return"].std() * np.sqrt(252)
print(f"Total Return: {total_return:.2%}")
print(f"Annual Return: {annual_return:.2%}")
print(f"Sharpe Ratio: {sharpe:.3f}")
```

## Event-Driven Backtesting

More realistic — processes one bar at a time, tracks positions and cash:

```python
import numpy as np
import pandas as pd
import yfinance as yf

class SimpleBacktester:
    def __init__(self, data, initial_capital=100000):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.trades = []
        self.portfolio_values = []

    def run(self, signal_func):
        for i in range(1, len(self.data)):
            row = self.data.iloc[i]
            prev_rows = self.data.iloc[:i]
            signal = signal_func(prev_rows)
            price = row["Close"]

            # Execute signal
            if signal == 1 and self.position == 0:
                shares = int(self.cash / price)
                self.position = shares
                self.cash -= shares * price
                self.trades.append(("BUY", self.data.index[i], price, shares))

            elif signal == -1 and self.position > 0:
                self.cash += self.position * price
                self.trades.append(("SELL", self.data.index[i], price, self.position))
                self.position = 0

            portfolio_value = self.cash + self.position * price
            self.portfolio_values.append(portfolio_value)

        return pd.Series(self.portfolio_values, index=self.data.index[1:])

# Signal function: SMA crossover
def sma_signal(data):
    if len(data) < 50:
        return 0
    sma_20 = data["Close"].iloc[-20:].mean()
    sma_50 = data["Close"].iloc[-50:].mean()
    if sma_20 > sma_50:
        return 1
    elif sma_20 < sma_50:
        return -1
    return 0

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
bt = SimpleBacktester(df)
portfolio = bt.run(sma_signal)

print(f"Final value: {portfolio.iloc[-1]:,.2f}")
print(f"Return: {(portfolio.iloc[-1] / bt.initial_capital - 1):.2%}")
print(f"Trades: {len(bt.trades)}")
```

## backtesting.py Framework

A popular lightweight framework:

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
df = df[["Open", "High", "Low", "Close", "Volume"]]

class SmaCross(Strategy):
    n1 = 20
    n2 = 50

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

bt = Backtest(df, SmaCross, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot(filename="backtest_result.html", open_browser=False)
```

## Zipline (Institutional-Grade)

```python
# Zipline requires specific setup; here's the pattern:
# pip install zipline-reloaded

from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, record
import pandas as pd

def initialize(context):
    context.asset = symbol("AAPL")
    context.short_window = 20
    context.long_window = 50

def handle_data(context, data):
    short_mavg = data.history(context.asset, "price", context.short_window, "1d").mean()
    long_mavg = data.history(context.asset, "price", context.long_window, "1d").mean()

    if short_mavg > long_mavg:
        order_target_percent(context.asset, 1.0)
    elif short_mavg < long_mavg:
        order_target_percent(context.asset, 0.0)

    record(short_mavg=short_mavg, long_mavg=long_mavg)

# Run with: zipline run -f strategy.py --start 2020-1-1 --end 2024-1-1
```

## Performance Metrics

```python
import numpy as np
import pandas as pd

def backtest_metrics(returns, risk_free_rate=0.05):
    """Calculate comprehensive backtest metrics."""
    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    n_years = len(returns) / 252

    # CAGR
    cagr = (1 + total_return) ** (1 / n_years) - 1

    # Sharpe
    sharpe = (returns.mean() - risk_free_rate / 252) / returns.std() * np.sqrt(252)

    # Max Drawdown
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    # Win Rate
    winning_days = (returns > 0).sum()
    total_days = (returns != 0).sum()
    win_rate = winning_days / total_days if total_days > 0 else 0

    # Profit Factor
    gross_profit = returns[returns > 0].sum()
    gross_loss = abs(returns[returns < 0].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

    return {
        "CAGR": f"{cagr:.2%}",
        "Sharpe Ratio": f"{sharpe:.3f}",
        "Max Drawdown": f"{max_dd:.2%}",
        "Win Rate": f"{win_rate:.2%}",
        "Profit Factor": f"{profit_factor:.2f}",
        "Total Trades (days)": total_days,
    }

# Example usage
np.random.seed(42)
returns = pd.Series(np.random.normal(0.0005, 0.015, 1000))
metrics = backtest_metrics(returns)
for k, v in metrics.items():
    print(f"{k:20s}: {v}")
```

## Avoiding Look-Ahead Bias

Look-ahead bias occurs when your strategy uses information that would not have been available at the time of the trade.

```python
import numpy as np
import pandas as pd

# WRONG: using today's close to decide today's trade
df["signal_wrong"] = np.where(df["Close"] > df["Close"].rolling(20).mean(), 1, 0)
df["return_wrong"] = df["signal_wrong"] * df["Close"].pct_change()  # BUG!

# CORRECT: shift signal by 1 day
df["signal_correct"] = np.where(df["Close"] > df["Close"].rolling(20).mean(), 1, 0)
df["return_correct"] = df["signal_correct"].shift(1) * df["Close"].pct_change()
```

Common sources of look-ahead bias:

- Using close price to generate signal AND execute trade on same bar
- Using future data in feature calculation (e.g., centered rolling windows)
- Filling missing data with future values

## Survivorship Bias

Survivorship bias occurs when you only test on stocks that still exist today, ignoring delisted companies.

```python
# Example: S&P 500 backtest
# WRONG: Use today's S&P 500 constituents for a 2010 backtest
# Many of today's members weren't in the index in 2010
# Companies that went bankrupt or were acquired are excluded

# CORRECT approach:
# 1. Use historical index membership data
# 2. Include delisted stocks in your universe
# 3. Account for mergers, splits, and delistings

# Practical mitigation: use ETFs (SPY) instead of individual stocks
# for index-level strategies
```

## Overfitting

Overfitting means your strategy is tuned to historical noise rather than real patterns.

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

# Split into in-sample and out-of-sample
split_date = "2022-01-01"
in_sample = returns[returns.index < split_date]
out_of_sample = returns[returns.index >= split_date]

# Test multiple SMA combinations on in-sample
best_sharpe = -np.inf
best_params = None

for short in range(5, 30, 5):
    for long in range(30, 100, 10):
        close_is = df["Close"][df.index < split_date]
        signal = np.where(
            close_is.rolling(short).mean() > close_is.rolling(long).mean(), 1, 0
        )
        strat_returns = pd.Series(signal, index=close_is.index).shift(1) * in_sample
        sharpe = strat_returns.mean() / strat_returns.std() * np.sqrt(252)

        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (short, long)

print(f"Best in-sample params: SMA({best_params[0]}, {best_params[1]})")
print(f"In-sample Sharpe: {best_sharpe:.3f}")

# Validate on out-of-sample
close_oos = df["Close"][df.index >= split_date]
signal_oos = np.where(
    close_oos.rolling(best_params[0]).mean() > close_oos.rolling(best_params[1]).mean(), 1, 0
)
strat_oos = pd.Series(signal_oos, index=close_oos.index).shift(1) * out_of_sample
oos_sharpe = strat_oos.mean() / strat_oos.std() * np.sqrt(252)
print(f"Out-of-sample Sharpe: {oos_sharpe:.3f}")
print(f"Degradation: {(best_sharpe - oos_sharpe) / best_sharpe:.1%}")
```

Signs of overfitting:

- Large performance gap between in-sample and out-of-sample
- Strategy has many parameters
- Strategy only works on one specific asset/timeframe
- Sharpe ratio above 3.0 in backtest

---

## Key Takeaways

- Vectorized backtesting is fast for prototyping; event-driven is more realistic
- Always shift signals by at least 1 bar to avoid look-ahead bias
- Split data into in-sample (training) and out-of-sample (validation)
- Fewer parameters = less overfitting risk
- Include transaction costs and slippage in backtests
- A strategy that works on multiple assets/timeframes is more robust

---

[prev: Chapter 3 - Technical Analysis](chapter-03-technical.md) | [next: Chapter 5 - Strategies](chapter-05-strategies.md)
