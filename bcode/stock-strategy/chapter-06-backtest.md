# Chapter 6: Backtesting

[← Chapter 5: Strategy](chapter-05-strategy.md) | [Chapter 7: Risk Management →](chapter-07-risk.md)

---

## Why Backtest?

A strategy that *sounds* good might lose money in practice. Backtesting runs your strategy on historical data to see how it would have performed. It's not a guarantee — but if a strategy can't even beat buy-and-hold on past data, it won't beat it going forward.

> **Disclaimer:** This is educational content, not financial advice. Backtests are optimistic — real trading has slippage, emotions, and bad timing.

## A Simple Backtest Engine

```python
import yfinance as yf
import pandas as pd
import numpy as np

def backtest_strategy(df, signals, initial_capital=10000, commission=0.001):
    """
    Backtest a strategy given price data and signals.
    signals: Series with 1 (buy/hold), -1 (sell/short), 0 (cash)
    commission: 0.001 = 0.1% per trade (round trip)
    """
    capital = initial_capital
    position = 0          # shares held
    trades = []
    portfolio_value = []

    for i in range(len(df)):
        price = df['Close'].iloc[i]
        signal = signals.iloc[i]
        date = df.index[i]

        # Buy signal — go from cash to invested
        if signal == 1 and position == 0:
            shares = int(capital / price)
            cost = shares * price * (1 + commission)
            if cost <= capital:
                position = shares
                capital -= cost
                trades.append({'date': date, 'action': 'BUY',
                              'price': price, 'shares': shares})

        # Sell signal — go from invested to cash
        elif signal == -1 and position > 0:
            revenue = position * price * (1 - commission)
            capital += revenue
            trades.append({'date': date, 'action': 'SELL',
                          'price': price, 'shares': position})
            position = 0

        # Track portfolio value
        total = capital + position * price
        portfolio_value.append(total)

    # Final value
    final_value = capital + position * df['Close'].iloc[-1]
    portfolio_value = pd.Series(portfolio_value, index=df.index)
    return final_value, trades, portfolio_value
```

## Running the Golden Cross Backtest

```python
df = yf.download("AAPL", start="2019-01-01", end="2025-01-01")
df['SMA_50'] = df['Close'].rolling(50).mean()
df['SMA_200'] = df['Close'].rolling(200).mean()

# Generate signals: 1 when SMA50 > SMA200, -1 otherwise
signals = pd.Series(0, index=df.index)
signals[df['SMA_50'] > df['SMA_200']] = 1
signals[df['SMA_50'] <= df['SMA_200']] = -1

# Only trade on crossovers (not every day)
trade_signals = signals.copy()
trade_signals[signals == signals.shift(1)] = 0  # No change = no action
trade_signals[trade_signals == 0] = np.nan
trade_signals = trade_signals.ffill().fillna(0)

final, trades, portfolio = backtest_strategy(df.iloc[200:], signals.iloc[200:])
print(f"Strategy final value: ${final:,.2f}")
print(f"Number of trades: {len(trades)}")

# Buy and hold comparison
buy_hold_return = df['Close'].iloc[-1] / df['Close'].iloc[200]
buy_hold_final = 10000 * buy_hold_return
print(f"Buy & Hold final value: ${buy_hold_final:,.2f}")
```

## Performance Metrics

```python
def calculate_metrics(portfolio_values, initial_capital=10000, risk_free_rate=0.04):
    """Calculate key performance metrics."""
    returns = portfolio_values.pct_change().dropna()
    trading_days = len(returns)
    years = trading_days / 252

    # Total return
    total_return = (portfolio_values.iloc[-1] / initial_capital - 1) * 100

    # Annualized return
    ann_return = ((portfolio_values.iloc[-1] / initial_capital) ** (1/years) - 1) * 100

    # Volatility (annualized)
    volatility = returns.std() * np.sqrt(252) * 100

    # Sharpe ratio
    excess_return = returns.mean() * 252 - risk_free_rate
    sharpe = excess_return / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

    # Max drawdown
    cummax = portfolio_values.cummax()
    drawdown = (portfolio_values - cummax) / cummax
    max_drawdown = drawdown.min() * 100

    return {
        'Total Return': f"{total_return:.1f}%",
        'Annualized Return': f"{ann_return:.1f}%",
        'Volatility': f"{volatility:.1f}%",
        'Sharpe Ratio': f"{sharpe:.2f}",
        'Max Drawdown': f"{max_drawdown:.1f}%",
        'Trading Days': trading_days,
    }

metrics = calculate_metrics(portfolio)
print("\n--- Strategy Performance ---")
for k, v in metrics.items():
    print(f"  {k:<20} {v}")
```

## Win Rate and Trade Analysis

```python
def analyze_trades(trades):
    """Calculate win rate and average trade stats."""
    if len(trades) < 2:
        return "Not enough trades"

    results = []
    for i in range(0, len(trades) - 1, 2):  # Pair buys with sells
        if i + 1 < len(trades):
            buy = trades[i]
            sell = trades[i + 1]
            pnl = (sell['price'] - buy['price']) / buy['price'] * 100
            results.append(pnl)

    wins = [r for r in results if r > 0]
    losses = [r for r in results if r <= 0]

    print(f"  Total trades: {len(results)}")
    print(f"  Win rate: {len(wins)/len(results)*100:.0f}%")
    print(f"  Avg win: +{np.mean(wins):.1f}%" if wins else "  No wins")
    print(f"  Avg loss: {np.mean(losses):.1f}%" if losses else "  No losses")
    print(f"  Best trade: +{max(results):.1f}%")
    print(f"  Worst trade: {min(results):.1f}%")

analyze_trades(trades)
```

## Plotting Strategy vs Buy-and-Hold

```python
import matplotlib.pyplot as plt

# Normalize both to start at same value
bh_portfolio = 10000 * df['Close'].iloc[200:] / df['Close'].iloc[200]

plt.figure(figsize=(12, 6))
plt.plot(portfolio.index, portfolio, label='Golden Cross Strategy', linewidth=1.5)
plt.plot(bh_portfolio.index, bh_portfolio, label='Buy & Hold', linewidth=1.5, alpha=0.7)
plt.title("Strategy vs Buy & Hold")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## Caveats About Backtesting

- **Survivorship bias** — you're testing stocks that exist today (failures are excluded)
- **Look-ahead bias** — make sure signals only use data available at that time
- **Overfitting** — tuning parameters to fit history perfectly = poor future performance
- **Transaction costs** — commissions, spread, and slippage eat into returns
- **Taxes** — short-term gains are taxed higher than long-term holds

## What You Learned

- **Backtest engine** — simulate trades on historical data with transaction costs
- **Key metrics** — total return, annualized return, Sharpe ratio, max drawdown
- **Win rate** — percentage of profitable trades
- **Strategy vs benchmark** — always compare against simple buy-and-hold
- **Backtesting pitfalls** — survivorship bias, overfitting, look-ahead bias

A strategy that makes money but has 40% drawdowns will make you panic-sell. Next: risk management — how to protect your capital.

---

[← Chapter 5: Strategy](chapter-05-strategy.md) | [Chapter 7: Risk Management →](chapter-07-risk.md)
