# Chapter 8: Portfolio Analysis

[← Chapter 7: Risk Management](chapter-07-risk.md) | [Chapter 9: Stock Screener →](chapter-09-screener.md)

---

## From Stocks to Portfolio

Individual stock analysis is useful. But your *portfolio* — the combination of all your holdings — is what determines your actual returns. A great stock in a terrible portfolio still loses money.

> **Disclaimer:** This is educational content, not financial advice. Portfolio theory has assumptions that don't always hold in real markets.

## Current Allocation

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

# Define your portfolio (ticker, shares, cost basis)
holdings = {
    'AAPL': {'shares': 50, 'cost_basis': 145.00},
    'MSFT': {'shares': 30, 'cost_basis': 310.00},
    'GOOGL': {'shares': 25, 'cost_basis': 125.00},
    'JPM':  {'shares': 40, 'cost_basis': 155.00},
    'JNJ':  {'shares': 35, 'cost_basis': 160.00},
    'VTI':  {'shares': 60, 'cost_basis': 210.00},
}

# Get current prices
tickers = list(holdings.keys())
data = yf.download(tickers, period="1d")
current_prices = data['Close'].iloc[-1]

# Calculate current values
portfolio_df = pd.DataFrame(holdings).T
portfolio_df['current_price'] = current_prices
portfolio_df['market_value'] = portfolio_df['shares'] * portfolio_df['current_price']
portfolio_df['cost_total'] = portfolio_df['shares'] * portfolio_df['cost_basis']
portfolio_df['gain_loss'] = portfolio_df['market_value'] - portfolio_df['cost_total']
portfolio_df['gain_pct'] = (portfolio_df['gain_loss'] / portfolio_df['cost_total']) * 100
portfolio_df['weight'] = portfolio_df['market_value'] / portfolio_df['market_value'].sum() * 100

print(portfolio_df[['market_value', 'weight', 'gain_pct']].round(1).to_string())
print(f"\nTotal value: ${portfolio_df['market_value'].sum():,.0f}")

# Pie chart
plt.figure(figsize=(8, 8))
plt.pie(portfolio_df['market_value'], labels=portfolio_df.index,
        autopct='%1.1f%%', startangle=90)
plt.title("Portfolio Allocation")
plt.show()
```

## Sector Exposure

```python
# Get sector for each holding
sectors = {}
for ticker in tickers:
    info = yf.Ticker(ticker).info
    sectors[ticker] = info.get('sector', 'ETF/Other')

portfolio_df['sector'] = pd.Series(sectors)

# Sector breakdown
sector_weights = portfolio_df.groupby('sector')['market_value'].sum()
sector_pct = sector_weights / sector_weights.sum() * 100

print("\nSector Exposure:")
for sector, pct in sector_pct.sort_values(ascending=False).items():
    print(f"  {sector:<25} {pct:.1f}%")
```

## Portfolio Return vs Benchmark

```python
# Historical portfolio performance vs S&P 500
hist_data = yf.download(tickers + ['SPY'], period="1y")['Close']

# Portfolio return (weighted by current allocation)
weights = (portfolio_df['market_value'] / portfolio_df['market_value'].sum()).values
portfolio_returns = hist_data[tickers].pct_change().dropna()
weighted_returns = (portfolio_returns * weights).sum(axis=1)
portfolio_cumulative = (1 + weighted_returns).cumprod()

# Benchmark (SPY)
spy_returns = hist_data['SPY'].pct_change().dropna()
spy_cumulative = (1 + spy_returns).cumprod()

plt.figure(figsize=(12, 6))
plt.plot(portfolio_cumulative.index, portfolio_cumulative, label='Your Portfolio', linewidth=2)
plt.plot(spy_cumulative.index, spy_cumulative, label='S&P 500 (SPY)', linewidth=2, alpha=0.7)
plt.title("Portfolio vs Benchmark (1 Year)")
plt.ylabel("Growth of $1")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Stats
port_ann = weighted_returns.mean() * 252 * 100
spy_ann = spy_returns.mean() * 252 * 100
print(f"Portfolio annualized return: {port_ann:.1f}%")
print(f"S&P 500 annualized return:  {spy_ann:.1f}%")
print(f"Alpha (excess return):      {port_ann - spy_ann:+.1f}%")
```

## Correlation Heatmap

```python
import seaborn as sns

corr = portfolio_returns.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='RdYlGn_r', center=0,
            vmin=-1, vmax=1, fmt='.2f', square=True)
plt.title("Portfolio Correlation Heatmap")
plt.tight_layout()
plt.show()

# Flag highly correlated pairs
print("\nHighly correlated pairs (>0.7):")
for i in range(len(tickers)):
    for j in range(i+1, len(tickers)):
        if abs(corr.iloc[i, j]) > 0.7:
            print(f"  {tickers[i]} & {tickers[j]}: {corr.iloc[i,j]:.2f}")
```

## Rebalancing Triggers

When a position drifts more than 5% from target, it's time to rebalance.

```python
# Define target allocation
targets = {'AAPL': 20, 'MSFT': 15, 'GOOGL': 15, 'JPM': 15, 'JNJ': 15, 'VTI': 20}

print(f"{'Ticker':<8} {'Target':>8} {'Actual':>8} {'Drift':>8} {'Action':<12}")
print("-" * 48)
for ticker in tickers:
    target = targets[ticker]
    actual = portfolio_df.loc[ticker, 'weight']
    drift = actual - target
    action = ""
    if drift > 5: action = "SELL (trim)"
    elif drift < -5: action = "BUY (add)"
    print(f"{ticker:<8} {target:>7.1f}% {actual:>7.1f}% {drift:>+7.1f}% {action}")
```

## Efficient Frontier (Simplified)

Find the portfolio weights that maximize return for a given risk level.

```python
# Monte Carlo simulation of random portfolios
n_portfolios = 5000
results = []
returns_annual = portfolio_returns.mean() * 252
cov_matrix = portfolio_returns.cov() * 252

for _ in range(n_portfolios):
    w = np.random.dirichlet(np.ones(len(tickers)))  # Random weights summing to 1
    port_return = np.dot(w, returns_annual)
    port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
    sharpe = (port_return - 0.04) / port_vol
    results.append([port_return * 100, port_vol * 100, sharpe])

results = np.array(results)

plt.figure(figsize=(10, 6))
scatter = plt.scatter(results[:, 1], results[:, 0], c=results[:, 2],
                      cmap='viridis', alpha=0.5, s=10)
plt.colorbar(scatter, label='Sharpe Ratio')
plt.xlabel("Volatility (%)")
plt.ylabel("Expected Return (%)")
plt.title("Efficient Frontier (Monte Carlo)")

# Mark current portfolio
curr_ret = np.dot(weights, returns_annual) * 100
curr_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * 100
plt.scatter(curr_vol, curr_ret, color='red', s=200, marker='*', label='Current Portfolio')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## What You Learned

- **Allocation pie chart** — see where your money actually is
- **Sector exposure** — avoid hidden concentration risk
- **Portfolio vs benchmark** — are you beating the market?
- **Correlation heatmap** — find redundant holdings
- **Rebalancing triggers** — drift > 5% = time to act
- **Efficient frontier** — visualize the risk/return tradeoff

You know your portfolio. Now let's find new stocks to add to it — with a systematic screener.

---

[← Chapter 7: Risk Management](chapter-07-risk.md) | [Chapter 9: Stock Screener →](chapter-09-screener.md)
