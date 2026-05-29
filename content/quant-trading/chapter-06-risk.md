# Chapter 6: Risk Management

[prev: Chapter 5 - Strategies](chapter-05-strategies.md) | [next: Chapter 7 - Machine Learning](chapter-07-ml.md)

---

Risk management is what separates surviving traders from blown-up accounts. A mediocre strategy with great risk management will outperform a great strategy with no risk management.

**Warning: No risk management system is perfect. Markets can gap, liquidity can vanish, and correlations can spike to 1 in a crisis.**

## Position Sizing: Kelly Criterion

The Kelly criterion determines the optimal fraction of capital to bet, maximizing long-term growth:

```python
import numpy as np
import pandas as pd
import yfinance as yf

def kelly_fraction(win_rate, win_loss_ratio):
    """Kelly criterion: f* = (bp - q) / b
    b = win/loss ratio, p = win probability, q = loss probability"""
    b = win_loss_ratio
    p = win_rate
    q = 1 - p
    return (b * p - q) / b

# Calculate from historical trades
df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

# Simulate a strategy's trade outcomes
signal = np.where(df["Close"].rolling(20).mean() > df["Close"].rolling(50).mean(), 1, 0)
strategy_returns = pd.Series(signal, index=df.index).shift(1) * returns
trades = strategy_returns[strategy_returns != 0]

wins = trades[trades > 0]
losses = trades[trades < 0]

win_rate = len(wins) / len(trades)
avg_win = wins.mean()
avg_loss = abs(losses.mean())
win_loss_ratio = avg_win / avg_loss

kelly = kelly_fraction(win_rate, win_loss_ratio)
half_kelly = kelly / 2  # Half-Kelly is more conservative

print(f"Win Rate: {win_rate:.2%}")
print(f"Avg Win / Avg Loss: {win_loss_ratio:.2f}")
print(f"Full Kelly: {kelly:.2%}")
print(f"Half Kelly: {half_kelly:.2%}")
```

In practice, use half-Kelly or less. Full Kelly is too aggressive and assumes perfect knowledge of probabilities.

## Position Sizing: Fixed Fractional

Risk a fixed percentage of capital per trade:

```python
import numpy as np

def fixed_fractional_size(capital, risk_per_trade, entry_price, stop_loss_price):
    """Calculate position size based on fixed risk percentage."""
    risk_amount = capital * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)
    shares = int(risk_amount / risk_per_share)
    position_value = shares * entry_price
    return {
        "shares": shares,
        "position_value": position_value,
        "risk_amount": risk_amount,
        "pct_of_capital": position_value / capital,
    }

# Example: risk 2% per trade
result = fixed_fractional_size(
    capital=100000,
    risk_per_trade=0.02,
    entry_price=150.0,
    stop_loss_price=145.0
)
for k, v in result.items():
    print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")
```

## Stop-Loss and Take-Profit

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")

def backtest_with_stops(df, stop_loss_pct=0.05, take_profit_pct=0.10):
    """Backtest with stop-loss and take-profit."""
    close = df["Close"]
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()

    position = 0
    entry_price = 0
    trades = []

    for i in range(50, len(df)):
        price = close.iloc[i]

        if position == 0:
            # Entry: SMA crossover
            if sma_20.iloc[i] > sma_50.iloc[i] and sma_20.iloc[i-1] <= sma_50.iloc[i-1]:
                position = 1
                entry_price = price
        else:
            pnl_pct = (price - entry_price) / entry_price

            # Stop-loss
            if pnl_pct <= -stop_loss_pct:
                trades.append(-stop_loss_pct)
                position = 0

            # Take-profit
            elif pnl_pct >= take_profit_pct:
                trades.append(take_profit_pct)
                position = 0

            # Exit signal
            elif sma_20.iloc[i] < sma_50.iloc[i]:
                trades.append(pnl_pct)
                position = 0

    trades = pd.Series(trades)
    print(f"Stop: {stop_loss_pct:.0%}, TP: {take_profit_pct:.0%}")
    print(f"  Trades: {len(trades)}, Win Rate: {(trades > 0).mean():.2%}")
    print(f"  Avg Trade: {trades.mean():.2%}, Total: {trades.sum():.2%}")
    return trades

# Compare different stop levels
backtest_with_stops(df, 0.03, 0.06)
backtest_with_stops(df, 0.05, 0.10)
backtest_with_stops(df, 0.08, 0.15)
```

## Portfolio Optimization: Markowitz Mean-Variance

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"]
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")
returns = data["Close"].pct_change().dropna()

# Expected returns and covariance
mu = returns.mean() * 252
cov = returns.cov() * 252
n_assets = len(tickers)

# Monte Carlo: random portfolios
n_portfolios = 10000
results = np.zeros((n_portfolios, 3))
weights_record = []

for i in range(n_portfolios):
    w = np.random.random(n_assets)
    w /= w.sum()
    weights_record.append(w)

    port_return = np.dot(w, mu)
    port_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
    sharpe = port_return / port_vol

    results[i] = [port_vol, port_return, sharpe]

# Find optimal portfolios
max_sharpe_idx = results[:, 2].argmax()
min_vol_idx = results[:, 0].argmin()

print("Maximum Sharpe Portfolio:")
print(f"  Return: {results[max_sharpe_idx, 1]:.2%}")
print(f"  Volatility: {results[max_sharpe_idx, 0]:.2%}")
print(f"  Sharpe: {results[max_sharpe_idx, 2]:.3f}")
print(f"  Weights: {dict(zip(tickers, weights_record[max_sharpe_idx].round(3)))}")

print("\nMinimum Variance Portfolio:")
print(f"  Return: {results[min_vol_idx, 1]:.2%}")
print(f"  Volatility: {results[min_vol_idx, 0]:.2%}")
print(f"  Weights: {dict(zip(tickers, weights_record[min_vol_idx].round(3)))}")

# Efficient frontier plot
plt.figure(figsize=(10, 6))
plt.scatter(results[:, 0], results[:, 1], c=results[:, 2], cmap="viridis", alpha=0.3, s=5)
plt.colorbar(label="Sharpe Ratio")
plt.scatter(results[max_sharpe_idx, 0], results[max_sharpe_idx, 1],
            marker="*", color="red", s=300, label="Max Sharpe")
plt.scatter(results[min_vol_idx, 0], results[min_vol_idx, 1],
            marker="*", color="blue", s=300, label="Min Variance")
plt.xlabel("Volatility")
plt.ylabel("Return")
plt.title("Efficient Frontier")
plt.legend()
plt.savefig("efficient_frontier.png")
plt.close()
```

## Minimum Variance Portfolio (Analytical)

```python
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"]
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")
returns = data["Close"].pct_change().dropna()

cov = returns.cov() * 252
cov_inv = np.linalg.inv(cov.values)
ones = np.ones(len(tickers))

# Minimum variance weights: w = (Σ^-1 * 1) / (1^T * Σ^-1 * 1)
weights = cov_inv @ ones / (ones @ cov_inv @ ones)

print("Minimum Variance Weights:")
for ticker, w in zip(tickers, weights):
    print(f"  {ticker}: {w:.3f}")

port_vol = np.sqrt(weights @ cov.values @ weights)
print(f"\nPortfolio Volatility: {port_vol:.2%}")
```

## Value at Risk (VaR)

VaR estimates the maximum loss at a given confidence level:

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

portfolio_value = 1000000  # 1M portfolio

# Historical VaR
confidence = 0.95
var_95 = returns.quantile(1 - confidence)
var_99 = returns.quantile(0.01)

print(f"95% Daily VaR: {var_95:.4f} ({portfolio_value * abs(var_95):,.0f})")
print(f"99% Daily VaR: {var_99:.4f} ({portfolio_value * abs(var_99):,.0f})")

# Parametric VaR (assumes normal distribution)
from scipy import stats
z_95 = stats.norm.ppf(1 - confidence)
parametric_var = returns.mean() + z_95 * returns.std()
print(f"Parametric 95% VaR: {parametric_var:.4f}")

# Conditional VaR (Expected Shortfall) - average loss beyond VaR
cvar_95 = returns[returns <= var_95].mean()
print(f"95% CVaR (Expected Shortfall): {cvar_95:.4f} ({portfolio_value * abs(cvar_95):,.0f})")
```

## Monte Carlo Simulation

Simulate thousands of possible future paths:

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

mu = returns.mean()
sigma = returns.std()
last_price = df["Close"].iloc[-1]

# Simulate 1000 paths, 252 days forward
n_simulations = 1000
n_days = 252

simulations = np.zeros((n_days, n_simulations))
simulations[0] = last_price

for t in range(1, n_days):
    random_returns = np.random.normal(mu, sigma, n_simulations)
    simulations[t] = simulations[t - 1] * (1 + random_returns)

# Analyze outcomes
final_prices = simulations[-1]
print(f"Starting Price: {last_price:.2f}")
print(f"Mean Final Price: {final_prices.mean():.2f}")
print(f"Median Final Price: {np.median(final_prices):.2f}")
print(f"5th Percentile: {np.percentile(final_prices, 5):.2f}")
print(f"95th Percentile: {np.percentile(final_prices, 95):.2f}")
print(f"Probability of Loss: {(final_prices < last_price).mean():.2%}")

# Plot
plt.figure(figsize=(12, 5))
plt.plot(simulations[:, :50], alpha=0.3, linewidth=0.5)
plt.axhline(last_price, color="black", linestyle="--", label="Start Price")
plt.title(f"Monte Carlo Simulation ({n_simulations} paths)")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.savefig("monte_carlo.png")
plt.close()
```

## Correlation Risk

Correlations increase during market stress — diversification fails when you need it most:

```python
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM"]
data = yf.download(tickers, start="2018-01-01", end="2024-01-01")
returns = data["Close"].pct_change().dropna()

# Compare correlations in calm vs stressed periods
spy = yf.download("SPY", start="2018-01-01", end="2024-01-01")
spy_returns = spy["Close"].pct_change().dropna()

# Define stress: SPY daily return < -2%
stress_days = spy_returns[spy_returns < -0.02].index
calm_days = spy_returns[spy_returns >= -0.02].index

# Align indices
stress_returns = returns.loc[returns.index.isin(stress_days)]
calm_returns = returns.loc[returns.index.isin(calm_days)]

print("Average Correlation (Calm Markets):")
print(f"  {calm_returns.corr().values[np.triu_indices(5, 1)].mean():.3f}")

print("Average Correlation (Stress Markets):")
print(f"  {stress_returns.corr().values[np.triu_indices(5, 1)].mean():.3f}")
```

## Drawdown Control

Reduce exposure when drawdown exceeds threshold:

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

def drawdown_controlled_strategy(returns, max_dd_threshold=0.10):
    """Reduce position size when drawdown exceeds threshold."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max

    # Scale position: full size when dd=0, zero when dd >= threshold
    scale = np.clip(1 + drawdown / max_dd_threshold, 0, 1)

    controlled_returns = returns * scale.shift(1)
    return controlled_returns, drawdown

controlled, dd = drawdown_controlled_strategy(returns, 0.10)

# Compare
cum_original = (1 + returns).cumprod()
cum_controlled = (1 + controlled).cumprod()

print(f"Original Max DD: {((cum_original - cum_original.cummax()) / cum_original.cummax()).min():.2%}")
print(f"Controlled Max DD: {((cum_controlled - cum_controlled.cummax()) / cum_controlled.cummax()).min():.2%}")
print(f"Original Return: {cum_original.iloc[-1] - 1:.2%}")
print(f"Controlled Return: {cum_controlled.iloc[-1] - 1:.2%}")
```

---

## Key Takeaways

- Never risk more than 1-2% of capital on a single trade
- Half-Kelly is safer than full Kelly in practice
- Diversification helps in normal markets but fails in crises
- VaR underestimates tail risk — use CVaR/Expected Shortfall
- Monte Carlo reveals the range of possible outcomes
- Drawdown control preserves capital for recovery
- Position sizing matters more than entry signals

---

[prev: Chapter 5 - Strategies](chapter-05-strategies.md) | [next: Chapter 7 - Machine Learning](chapter-07-ml.md)
