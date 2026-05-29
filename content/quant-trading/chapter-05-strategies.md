# Chapter 5: Trading Strategies

[prev: Chapter 4 - Backtesting](chapter-04-backtesting.md) | [next: Chapter 6 - Risk Management](chapter-06-risk.md)

---

This chapter implements complete trading strategies with full backtest code. Each strategy represents a different market hypothesis.

**Disclaimer: These strategies are for educational purposes only. Do not trade real money without extensive testing and risk management.**

## Mean Reversion: Pairs Trading

Pairs trading exploits the tendency of correlated assets to revert to their historical relationship.

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Download correlated pair
data = yf.download(["KO", "PEP"], start="2020-01-01", end="2024-01-01")
close = data["Close"]

# Calculate spread (log price ratio)
spread = np.log(close["KO"]) - np.log(close["PEP"])

# Z-score of spread
window = 60
spread_mean = spread.rolling(window).mean()
spread_std = spread.rolling(window).std()
zscore = (spread - spread_mean) / spread_std

# Trading signals
# Buy spread (long KO, short PEP) when z < -2
# Sell spread (short KO, long PEP) when z > 2
# Exit when z crosses 0
signal = pd.Series(0, index=zscore.index)
signal[zscore < -2] = 1   # Long spread
signal[zscore > 2] = -1   # Short spread
signal[zscore.abs() < 0.5] = 0  # Exit

# Forward fill positions (hold until exit)
position = signal.replace(0, np.nan).ffill().fillna(0)
position = position.shift(1)  # Avoid look-ahead

# Returns: long KO - short PEP (or vice versa)
ko_returns = close["KO"].pct_change()
pep_returns = close["PEP"].pct_change()
strategy_returns = position * (ko_returns - pep_returns)

cumulative = (1 + strategy_returns).cumprod()
print(f"Pairs Trading Return: {cumulative.iloc[-1] - 1:.2%}")
sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
print(f"Sharpe Ratio: {sharpe:.3f}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
axes[0].plot(close["KO"] / close["KO"].iloc[0], label="KO")
axes[0].plot(close["PEP"] / close["PEP"].iloc[0], label="PEP")
axes[0].legend()
axes[0].set_title("Normalized Prices")

axes[1].plot(zscore)
axes[1].axhline(2, color="red", linestyle="--")
axes[1].axhline(-2, color="green", linestyle="--")
axes[1].axhline(0, color="black", linewidth=0.5)
axes[1].set_title("Z-Score of Spread")

axes[2].plot(cumulative)
axes[2].set_title("Pairs Trading Cumulative Return")

plt.tight_layout()
plt.savefig("pairs_trading.png")
plt.close()
```

## Mean Reversion: Bollinger Bounce

Buy when price touches lower band, sell at middle band:

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Bollinger Bands
window = 20
middle = close.rolling(window).mean()
std = close.rolling(window).std()
upper = middle + 2 * std
lower = middle - 2 * std

# Signals
signal = pd.Series(0, index=close.index)
signal[close < lower] = 1    # Buy at lower band
signal[close > middle] = -1  # Sell at middle band (take profit)

# Position management
position = pd.Series(0.0, index=close.index)
for i in range(1, len(signal)):
    if signal.iloc[i] == 1:
        position.iloc[i] = 1
    elif signal.iloc[i] == -1:
        position.iloc[i] = 0
    else:
        position.iloc[i] = position.iloc[i - 1]

position = position.shift(1)
returns = position * close.pct_change()

cumulative = (1 + returns).cumprod()
sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Bollinger Bounce Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")
```

## Mean Reversion: Z-Score Strategy

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Z-score of price relative to its rolling mean
window = 50
zscore = (close - close.rolling(window).mean()) / close.rolling(window).std()

# Buy when oversold (z < -1.5), sell when overbought (z > 1.5)
position = pd.Series(0.0, index=close.index)
position[zscore < -1.5] = 1
position[zscore > 1.5] = -1
position[(zscore > -0.5) & (zscore < 0.5)] = 0
position = position.replace(0, np.nan).ffill().fillna(0).shift(1)

returns = position * close.pct_change()
cumulative = (1 + returns).cumprod()
sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Z-Score Strategy Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")
```

## Momentum: Trend Following

Go long when price is above its long-term trend, short when below:

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Trend: 200-day SMA
sma_200 = close.rolling(200).mean()

# Momentum filter: 12-month return > 0
momentum = close / close.shift(252) - 1

# Position: long if above SMA AND positive momentum
position = np.where((close > sma_200) & (momentum > 0), 1, 0)
position = pd.Series(position, index=close.index).shift(1)

returns = position * close.pct_change()
cumulative = (1 + returns).cumprod()
buy_hold = (1 + close.pct_change()).cumprod()

sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Trend Following Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Buy & Hold Return: {buy_hold.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")

plt.figure(figsize=(12, 5))
plt.plot(cumulative, label="Trend Following")
plt.plot(buy_hold, label="Buy & Hold")
plt.legend()
plt.title("Trend Following vs Buy & Hold")
plt.savefig("trend_following.png")
plt.close()
```

## Momentum: Breakout Strategy

Enter when price breaks above N-day high:

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Donchian Channel breakout
lookback = 20
upper_channel = close.rolling(lookback).max()
lower_channel = close.rolling(lookback).min()

# Buy on upper breakout, sell on lower breakout
position = pd.Series(0.0, index=close.index)
for i in range(lookback, len(close)):
    if close.iloc[i] >= upper_channel.iloc[i - 1]:
        position.iloc[i] = 1
    elif close.iloc[i] <= lower_channel.iloc[i - 1]:
        position.iloc[i] = 0
    else:
        position.iloc[i] = position.iloc[i - 1]

position = position.shift(1)
returns = position * close.pct_change()
cumulative = (1 + returns).cumprod()
sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Breakout Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")
```

## Momentum: Dual Moving Average

Classic strategy with fast and slow EMA:

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Dual EMA
ema_fast = close.ewm(span=12, adjust=False).mean()
ema_slow = close.ewm(span=26, adjust=False).mean()

# Long when fast > slow, flat otherwise
position = np.where(ema_fast > ema_slow, 1, 0)
position = pd.Series(position, index=close.index).shift(1)

returns = position * close.pct_change()
cumulative = (1 + returns).cumprod()
sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Dual EMA Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")
```

## Statistical Arbitrage

Cross-sectional momentum: buy winners, sell losers within a universe:

```python
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "JNJ"]
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")
close = data["Close"]

# Monthly rebalance: rank by past 1-month return
monthly = close.resample("ME").last()
monthly_returns = monthly.pct_change()

# Long top 3, short bottom 3
portfolio_returns = []
for i in range(1, len(monthly_returns)):
    prev_returns = monthly_returns.iloc[i - 1]
    ranked = prev_returns.dropna().sort_values()

    shorts = ranked.index[:3]
    longs = ranked.index[-3:]

    # Equal weight
    long_return = monthly_returns.iloc[i][longs].mean()
    short_return = monthly_returns.iloc[i][shorts].mean()
    portfolio_returns.append(long_return - short_return)

port_returns = pd.Series(portfolio_returns, index=monthly_returns.index[1:])
cumulative = (1 + port_returns).cumprod()
annual_return = (cumulative.iloc[-1]) ** (12 / len(port_returns)) - 1
sharpe = port_returns.mean() / port_returns.std() * np.sqrt(12)

print(f"Stat Arb Annual Return: {annual_return:.2%}")
print(f"Sharpe (monthly): {sharpe:.3f}")
```

## Market Making Basics

Market makers profit from the bid-ask spread. Simplified simulation:

```python
import numpy as np
import pandas as pd

np.random.seed(42)

# Simulate order book
n_steps = 10000
mid_price = 100 + np.cumsum(np.random.randn(n_steps) * 0.01)
spread = 0.05  # Fixed spread

# Market maker quotes bid and ask
bid = mid_price - spread / 2
ask = mid_price + spread / 2

# Random fills (50% chance each side gets filled per step)
bid_fills = np.random.random(n_steps) < 0.3
ask_fills = np.random.random(n_steps) < 0.3

# PnL: earn spread on round trips, lose on inventory risk
inventory = 0
cash = 0
pnl_history = []

for i in range(n_steps):
    if bid_fills[i]:
        inventory += 1
        cash -= bid[i]
    if ask_fills[i]:
        inventory -= 1
        cash += ask[i]

    # Mark-to-market PnL
    pnl_history.append(cash + inventory * mid_price[i])

pnl = pd.Series(pnl_history)
print(f"Final PnL: {pnl.iloc[-1]:.2f}")
print(f"Final Inventory: {inventory}")
print(f"Max PnL: {pnl.max():.2f}")
print(f"Min PnL: {pnl.min():.2f}")
```

**Note**: Real market making requires sub-millisecond execution, sophisticated inventory management, and significant capital. This is a conceptual illustration only.

## Factor Models (Fama-French)

The Fama-French model explains returns through market, size, and value factors:

```python
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression

# Download stock and factor data
stock = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
stock_returns = stock["Close"].pct_change().dropna()

# Simulate Fama-French factors (in practice, download from Kenneth French's website)
# https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
np.random.seed(42)
n = len(stock_returns)
factors = pd.DataFrame({
    "Mkt-RF": np.random.normal(0.0004, 0.01, n),  # Market excess return
    "SMB": np.random.normal(0.0001, 0.005, n),     # Small minus Big
    "HML": np.random.normal(0.0001, 0.005, n),     # High minus Low (value)
    "RF": np.full(n, 0.0002),                       # Risk-free rate
}, index=stock_returns.index)

# Excess returns
excess_returns = stock_returns - factors["RF"]

# Regression
X = factors[["Mkt-RF", "SMB", "HML"]].values
y = excess_returns.values

model = LinearRegression().fit(X, y)
print(f"Alpha (daily): {model.intercept_:.6f}")
print(f"Alpha (annual): {model.intercept_ * 252:.4f}")
print(f"Market Beta: {model.coef_[0]:.4f}")
print(f"Size (SMB) Beta: {model.coef_[1]:.4f}")
print(f"Value (HML) Beta: {model.coef_[2]:.4f}")
print(f"R-squared: {model.score(X, y):.4f}")
```

---

## Strategy Comparison

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]
market_ret = close.pct_change()

strategies = {}

# 1. SMA Crossover
sma20 = close.rolling(20).mean()
sma50 = close.rolling(50).mean()
pos = np.where(sma20 > sma50, 1, 0)
strategies["SMA Cross"] = pd.Series(pos, index=close.index).shift(1) * market_ret

# 2. Mean Reversion (z-score)
z = (close - close.rolling(50).mean()) / close.rolling(50).std()
pos_mr = pd.Series(0.0, index=close.index)
pos_mr[z < -1.5] = 1
pos_mr[z > 1.5] = -1
pos_mr = pos_mr.replace(0, np.nan).ffill().fillna(0).shift(1)
strategies["Mean Reversion"] = pos_mr * market_ret

# 3. Momentum
mom = close / close.shift(252) - 1
pos_mom = np.where((close > close.rolling(200).mean()) & (mom > 0), 1, 0)
strategies["Momentum"] = pd.Series(pos_mom, index=close.index).shift(1) * market_ret

# Compare
print(f"{'Strategy':<20} {'Return':>10} {'Sharpe':>8}")
print("-" * 40)
for name, ret in strategies.items():
    total = (1 + ret).cumprod().iloc[-1] - 1
    sharpe = ret.mean() / ret.std() * np.sqrt(252)
    print(f"{name:<20} {total:>9.2%} {sharpe:>8.3f}")
```

---

## Key Takeaways

- Mean reversion works in ranging markets; momentum works in trending markets
- Pairs trading reduces market exposure (market-neutral)
- Always validate strategies out-of-sample
- Simpler strategies with fewer parameters are more robust
- Factor models help understand what drives your returns
- No single strategy works in all market conditions — diversify

---

[prev: Chapter 4 - Backtesting](chapter-04-backtesting.md) | [next: Chapter 6 - Risk Management](chapter-06-risk.md)
