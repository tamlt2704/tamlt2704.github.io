# Quantitative Trading with Python: From Market Data to Live Strategies

[next: Chapter 1 - Market Data](chapter-01-market-data.md)

---

**Disclaimer: This content is for educational purposes only and does not constitute financial advice. Trading involves substantial risk of loss. Past performance does not guarantee future results.**

---

## What is Quantitative Trading?

Quantitative trading uses mathematical models, statistical analysis, and programming to identify and execute trading opportunities. Instead of relying on intuition, quant traders build systematic strategies that can be tested against historical data and deployed algorithmically.

## What You Will Learn

This series takes you from raw market data to a live trading system, using Python as the primary tool.

## Chapters

1. [Market Data](chapter-01-market-data.md) — Data sources, fetching historical data, candlestick charts, data cleaning, storage and resampling.

2. [Statistical Foundations](chapter-02-statistics.md) — Returns, risk metrics, Sharpe ratio, drawdown, correlation, distribution analysis, hypothesis testing.

3. [Technical Analysis](chapter-03-technical.md) — Moving averages, RSI, MACD, Bollinger Bands, ATR, implementing indicators from scratch.

4. [Backtesting](chapter-04-backtesting.md) — Vectorized and event-driven backtesting, frameworks, performance metrics, avoiding common pitfalls.

5. [Strategies](chapter-05-strategies.md) — Mean reversion, momentum, statistical arbitrage, market making, factor models with full implementations.

6. [Risk Management](chapter-06-risk.md) — Position sizing, Kelly criterion, portfolio optimization, VaR, Monte Carlo simulation, drawdown control.

7. [Machine Learning for Trading](chapter-07-ml.md) — Feature engineering, time-series splits, Random Forest, XGBoost, LSTM, walk-forward optimization.

8. [Execution](chapter-08-execution.md) — Paper trading, broker APIs, order types, slippage, transaction costs, scheduling, monitoring.

9. [Going Live](chapter-09-live.md) — Infrastructure, real-time feeds, order management, risk checks, PnL tracking, alerts, disaster recovery.

## Prerequisites

- Python 3.9+
- Basic understanding of financial markets
- Familiarity with pandas and numpy

## Core Libraries

```python
pip install pandas numpy matplotlib yfinance mplfinance scikit-learn
pip install ta-lib backtesting xgboost tensorflow alpaca-trade-api
```

## Project Structure

```
quant-trading/
├── data/           # Historical market data
├── strategies/     # Strategy implementations
├── backtest/       # Backtesting engine and results
├── ml/             # Machine learning models
├── execution/      # Live trading scripts
└── utils/          # Shared utilities
```

---

[next: Chapter 1 - Market Data](chapter-01-market-data.md)
