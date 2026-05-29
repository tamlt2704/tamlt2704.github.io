# Chapter 2: Statistical Foundations

[prev: Chapter 1 - Market Data](chapter-01-market-data.md) | [next: Chapter 3 - Technical Analysis](chapter-03-technical.md)

---

Statistics is the language of quantitative trading. Every strategy decision — from signal generation to risk management — relies on statistical reasoning.

## Simple vs Log Returns

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
close = df["Close"]

# Simple (arithmetic) returns
simple_returns = close.pct_change().dropna()

# Log (logarithmic) returns
log_returns = np.log(close / close.shift(1)).dropna()

print(f"Simple return mean: {simple_returns.mean():.6f}")
print(f"Log return mean:    {log_returns.mean():.6f}")
```

**Why log returns?**

- Additive over time: multi-period return = sum of single-period log returns
- Symmetric: +10% and -10% have equal magnitude
- Better statistical properties (closer to normal distribution)

**Why simple returns?**

- Additive across assets in a portfolio
- Easier to interpret (a 5% return means 5% gain)

## Mean, Variance, Standard Deviation

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

mean_daily = returns.mean()
var_daily = returns.var()
std_daily = returns.std()

# Annualize (252 trading days)
mean_annual = mean_daily * 252
std_annual = std_daily * np.sqrt(252)

print(f"Daily:  mean={mean_daily:.6f}, std={std_daily:.6f}")
print(f"Annual: mean={mean_annual:.4f}, std={std_annual:.4f}")
```

## Sharpe Ratio

The Sharpe ratio measures risk-adjusted return: how much excess return you get per unit of risk.

```python
import numpy as np
import pandas as pd
import yfinance as yf

def sharpe_ratio(returns, risk_free_rate=0.05, periods=252):
    """Annualized Sharpe ratio."""
    excess_returns = returns - risk_free_rate / periods
    return np.sqrt(periods) * excess_returns.mean() / excess_returns.std()

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

sr = sharpe_ratio(returns)
print(f"AAPL Sharpe Ratio: {sr:.3f}")
```

Interpretation:

- Below 1.0: subpar
- 1.0 - 2.0: acceptable
- 2.0 - 3.0: very good
- Above 3.0: excellent (or suspicious — check for overfitting)

## Sortino Ratio

Like Sharpe but only penalizes downside volatility:

```python
import numpy as np
import pandas as pd
import yfinance as yf

def sortino_ratio(returns, risk_free_rate=0.05, periods=252):
    """Annualized Sortino ratio."""
    excess_returns = returns - risk_free_rate / periods
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.sqrt((downside_returns ** 2).mean())
    return np.sqrt(periods) * excess_returns.mean() / downside_std

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

print(f"Sortino Ratio: {sortino_ratio(returns):.3f}")
```

## Maximum Drawdown

The largest peak-to-trough decline — measures worst-case loss:

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def max_drawdown(returns):
    """Calculate maximum drawdown from a return series."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

mdd = max_drawdown(returns)
print(f"Max Drawdown: {mdd:.2%}")

# Plot drawdown
cumulative = (1 + returns).cumprod()
running_max = cumulative.cummax()
drawdown = (cumulative - running_max) / running_max

plt.figure(figsize=(12, 4))
drawdown.plot()
plt.title("AAPL Drawdown")
plt.ylabel("Drawdown")
plt.fill_between(drawdown.index, drawdown.values, alpha=0.3, color="red")
plt.savefig("drawdown.png")
plt.close()
```

## Rolling Statistics

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

# 30-day rolling statistics
rolling_mean = returns.rolling(30).mean() * 252
rolling_std = returns.rolling(30).std() * np.sqrt(252)
rolling_sharpe = rolling_mean / rolling_std

fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

axes[0].plot(rolling_mean)
axes[0].set_title("30-Day Rolling Annualized Return")
axes[0].axhline(0, color="black", linewidth=0.5)

axes[1].plot(rolling_std)
axes[1].set_title("30-Day Rolling Annualized Volatility")

axes[2].plot(rolling_sharpe)
axes[2].set_title("30-Day Rolling Sharpe Ratio")
axes[2].axhline(0, color="black", linewidth=0.5)

plt.tight_layout()
plt.savefig("rolling_stats.png")
plt.close()
```

## Correlation Matrix

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
data = yf.download(tickers, start="2020-01-01", end="2024-01-01")
returns = data["Close"].pct_change().dropna()

corr_matrix = returns.corr()
print(corr_matrix.round(3))

# Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr_matrix, cmap="RdYlGn", vmin=-1, vmax=1)
ax.set_xticks(range(len(tickers)))
ax.set_yticks(range(len(tickers)))
ax.set_xticklabels(tickers)
ax.set_yticklabels(tickers)
plt.colorbar(im)
plt.title("Return Correlation Matrix")
plt.savefig("correlation_matrix.png")
plt.close()
```

## Distribution of Returns (Fat Tails)

Financial returns are NOT normally distributed — they have fat tails (extreme events happen more often than a normal distribution predicts).

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy import stats

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

# Descriptive statistics
print(f"Skewness: {returns.skew():.4f}")
print(f"Kurtosis: {returns.kurtosis():.4f}")  # Excess kurtosis; normal = 0

# Jarque-Bera test for normality
jb_stat, jb_pvalue = stats.jarque_bera(returns)
print(f"Jarque-Bera p-value: {jb_pvalue:.6f}")
print(f"Normal distribution? {'No' if jb_pvalue < 0.05 else 'Yes'}")

# Visual comparison
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(returns, bins=100, density=True, alpha=0.7, label="Actual")

# Overlay normal distribution
x = np.linspace(returns.min(), returns.max(), 100)
normal_pdf = stats.norm.pdf(x, returns.mean(), returns.std())
ax.plot(x, normal_pdf, "r-", linewidth=2, label="Normal")

ax.set_title("AAPL Returns vs Normal Distribution")
ax.legend()
plt.savefig("fat_tails.png")
plt.close()
```

## Hypothesis Testing for Strategies

Before trusting a strategy, test whether its returns are statistically significant:

```python
import numpy as np
import pandas as pd
from scipy import stats

def test_strategy_significance(strategy_returns, benchmark_returns=None):
    """Test if strategy returns are significantly different from zero (or benchmark)."""

    # Test: are returns significantly > 0?
    t_stat, p_value = stats.ttest_1samp(strategy_returns, 0)
    print(f"H0: mean return = 0")
    print(f"t-statistic: {t_stat:.4f}")
    print(f"p-value (two-sided): {p_value:.6f}")
    print(f"Significant at 5%? {'Yes' if p_value < 0.05 else 'No'}")

    if benchmark_returns is not None:
        # Test: does strategy beat benchmark?
        t_stat, p_value = stats.ttest_ind(strategy_returns, benchmark_returns)
        print(f"\nH0: strategy return = benchmark return")
        print(f"t-statistic: {t_stat:.4f}")
        print(f"p-value: {p_value:.6f}")
        print(f"Strategy beats benchmark? {'Yes' if p_value < 0.05 and t_stat > 0 else 'No'}")

# Example: simulated strategy
np.random.seed(42)
strategy_returns = pd.Series(np.random.normal(0.0005, 0.02, 500))  # Slight edge
benchmark_returns = pd.Series(np.random.normal(0.0003, 0.015, 500))

test_strategy_significance(strategy_returns, benchmark_returns)
```

**Warning**: With enough backtesting iterations, you will find "significant" results by chance. Apply Bonferroni correction or use out-of-sample testing.

## Complete Performance Summary Function

```python
import numpy as np
import pandas as pd

def performance_summary(returns, risk_free_rate=0.05):
    """Comprehensive performance statistics."""
    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    n_years = len(returns) / 252
    cagr = (1 + total_return) ** (1 / n_years) - 1

    annual_vol = returns.std() * np.sqrt(252)
    sharpe = (cagr - risk_free_rate) / annual_vol

    downside = returns[returns < 0]
    downside_vol = downside.std() * np.sqrt(252)
    sortino = (cagr - risk_free_rate) / downside_vol

    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    return {
        "Total Return": f"{total_return:.2%}",
        "CAGR": f"{cagr:.2%}",
        "Annual Volatility": f"{annual_vol:.2%}",
        "Sharpe Ratio": f"{sharpe:.3f}",
        "Sortino Ratio": f"{sortino:.3f}",
        "Max Drawdown": f"{max_dd:.2%}",
        "Skewness": f"{returns.skew():.4f}",
        "Kurtosis": f"{returns.kurtosis():.4f}",
    }

# Usage
import yfinance as yf
df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
returns = df["Close"].pct_change().dropna()

stats_summary = performance_summary(returns)
for k, v in stats_summary.items():
    print(f"{k:20s}: {v}")
```

---

## Key Takeaways

- Use log returns for time-series analysis, simple returns for portfolio analysis
- Sharpe ratio is the standard risk-adjusted metric; Sortino is better for asymmetric strategies
- Financial returns have fat tails — never assume normality
- Always test statistical significance before trusting backtest results
- Rolling statistics reveal how strategy performance changes over time

---

[prev: Chapter 1 - Market Data](chapter-01-market-data.md) | [next: Chapter 3 - Technical Analysis](chapter-03-technical.md)
