# Chapter 7: Risk Management

[← Chapter 6: Backtesting](chapter-06-backtest.md) | [Chapter 8: Portfolio →](chapter-08-portfolio.md)

---

## Risk Is the Only Thing You Control

You can't control whether a stock goes up. You CAN control how much you lose when it goes down. Risk management is the difference between a bad month and a blown account.

> **Disclaimer:** This is educational content, not financial advice. Risk management reduces losses but doesn't eliminate them.

## Position Sizing: Fixed Percentage

Never risk more than X% of your portfolio on a single trade. Common rule: 1-2% risk per trade.

```python
import numpy as np
import pandas as pd

def fixed_percent_position(capital, risk_pct, entry_price, stop_loss_price):
    """Calculate position size based on fixed % risk."""
    risk_per_share = entry_price - stop_loss_price
    dollar_risk = capital * risk_pct
    shares = int(dollar_risk / risk_per_share)
    position_value = shares * entry_price
    print(f"Capital: ${capital:,.0f}")
    print(f"Risk per trade: {risk_pct*100}% = ${dollar_risk:,.0f}")
    print(f"Entry: ${entry_price:.2f}, Stop: ${stop_loss_price:.2f}")
    print(f"Risk/share: ${risk_per_share:.2f}")
    print(f"Position: {shares} shares (${position_value:,.0f})")
    print(f"Max loss if stopped out: ${shares * risk_per_share:,.0f}")
    return shares

# Example: $50,000 portfolio, 2% risk, buying at $150 with stop at $140
shares = fixed_percent_position(50000, 0.02, 150, 140)
```

## Position Sizing: Kelly Criterion

Kelly tells you the *optimal* bet size based on your win rate and payoff ratio. In practice, use half-Kelly (full Kelly is too aggressive).

```python
def kelly_criterion(win_rate, avg_win, avg_loss):
    """Calculate Kelly fraction (optimal position size)."""
    # Kelly formula: f = (bp - q) / b
    # b = avg_win / avg_loss, p = win_rate, q = 1 - win_rate
    b = abs(avg_win / avg_loss)
    p = win_rate
    q = 1 - p
    kelly = (b * p - q) / b
    half_kelly = kelly / 2  # More conservative

    print(f"Win rate: {p*100:.0f}%")
    print(f"Avg win: +{avg_win:.1f}%, Avg loss: {avg_loss:.1f}%")
    print(f"Full Kelly: {kelly*100:.1f}% of capital per trade")
    print(f"Half Kelly: {half_kelly*100:.1f}% (recommended)")
    return half_kelly

# From our backtest: 60% win rate, avg win +8%, avg loss -4%
kelly = kelly_criterion(0.60, 8.0, -4.0)
```

## Stop-Loss: Fixed and Trailing

```python
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="6mo")

# Fixed stop-loss: sell if price drops X% from entry
entry_price = df['Close'].iloc[0]
fixed_stop = entry_price * 0.92  # 8% below entry

# Trailing stop-loss: sell if price drops X% from HIGHEST point since entry
trail_pct = 0.08
df['Trailing_Stop'] = df['Close'].cummax() * (1 - trail_pct)

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Price', linewidth=1.5)
plt.axhline(fixed_stop, color='red', linestyle='--', label=f'Fixed Stop (${fixed_stop:.0f})')
plt.plot(df.index, df['Trailing_Stop'], color='orange', linestyle='-',
         label='Trailing Stop (8%)', linewidth=1.5)
plt.title("Fixed vs Trailing Stop-Loss")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

Trailing stops lock in profits as the stock rises, while still giving room for normal pullbacks.

## Diversification: Correlation Matrix

Holding 10 tech stocks isn't diversification — they all move together. True diversification means low correlation.

```python
tickers = ["AAPL", "JPM", "JNJ", "XOM", "VNQ", "GLD", "TLT"]
# Tech, Finance, Healthcare, Energy, Real Estate, Gold, Bonds
data = yf.download(tickers, period="2y")['Close']
returns = data.pct_change().dropna()

# Correlation matrix
corr = returns.corr()
print("Correlation Matrix:")
print(corr.round(2).to_string())

# Heatmap
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr, cmap='RdYlGn_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(tickers)))
ax.set_yticks(range(len(tickers)))
ax.set_xticklabels(tickers)
ax.set_yticklabels(tickers)
for i in range(len(tickers)):
    for j in range(len(tickers)):
        ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha='center', va='center', fontsize=9)
plt.colorbar(im)
plt.title("Asset Correlation Matrix")
plt.tight_layout()
plt.show()
```

Correlation < 0.3 = good diversification. Negative correlation = even better (one zigs when the other zags).

## Value at Risk (VaR)

"What's the worst I can lose on a normal bad day?" VaR answers this at a confidence level.

```python
def calculate_var(returns, confidence=0.95, investment=10000):
    """Calculate Value at Risk (historical method)."""
    # Sort returns, find the percentile cutoff
    var_pct = np.percentile(returns, (1 - confidence) * 100)
    var_dollar = investment * abs(var_pct)

    print(f"Investment: ${investment:,.0f}")
    print(f"Confidence: {confidence*100:.0f}%")
    print(f"Daily VaR: {var_pct*100:.2f}% (${var_dollar:,.0f})")
    print(f"→ On 95% of days, you won't lose more than ${var_dollar:,.0f}")
    print(f"→ On ~1 day per month, losses could exceed this")
    return var_dollar

portfolio_returns = returns.mean(axis=1)  # Equal-weight portfolio
calculate_var(portfolio_returns, confidence=0.95, investment=50000)
```

## Impact on Backtest Results

```python
# Compare: no risk management vs 8% trailing stop
df = yf.download("AAPL", start="2020-01-01", end="2025-01-01")

# Strategy without stop-loss
no_stop_value = 10000 * df['Close'] / df['Close'].iloc[0]

# Strategy with trailing stop (exit when triggered, re-enter when price > stop)
capital = 10000
position = int(capital / df['Close'].iloc[0])
capital -= position * df['Close'].iloc[0]
peak = df['Close'].iloc[0]
stopped_out = False
with_stop = []

for price in df['Close']:
    if not stopped_out:
        peak = max(peak, price)
        if price < peak * 0.92:  # 8% trailing stop hit
            capital += position * price
            position = 0
            stopped_out = True
    else:
        if price > peak:  # Re-enter when new high
            position = int(capital / price)
            capital -= position * price
            peak = price
            stopped_out = False
    with_stop.append(capital + position * price)

with_stop = pd.Series(with_stop, index=df.index)
max_dd_no_stop = ((no_stop_value / no_stop_value.cummax()) - 1).min() * 100
max_dd_with_stop = ((with_stop / with_stop.cummax()) - 1).min() * 100

print(f"Without stop — Final: ${no_stop_value.iloc[-1]:,.0f}, Max DD: {max_dd_no_stop:.1f}%")
print(f"With stop    — Final: ${with_stop.iloc[-1]:,.0f}, Max DD: {max_dd_with_stop:.1f}%")
```

## What You Learned

- **Position sizing** — never risk more than 1-2% per trade
- **Kelly criterion** — mathematically optimal bet size (use half-Kelly)
- **Stop-losses** — fixed (simple) vs trailing (locks in profits)
- **Diversification** — low correlation between holdings reduces portfolio risk
- **Value at Risk** — quantifies your worst expected daily loss
- **Risk management changes everything** — smaller drawdowns, better sleep

You can manage risk on individual trades. Now let's zoom out and manage an entire portfolio.

---

[← Chapter 6: Backtesting](chapter-06-backtest.md) | [Chapter 8: Portfolio →](chapter-08-portfolio.md)
