# Chapter 8: Execution

[prev: Chapter 7 - Machine Learning](chapter-07-ml.md) | [next: Chapter 9 - Going Live](chapter-09-live.md)

---

A profitable strategy is worthless without proper execution. This chapter covers the bridge between backtesting and live trading.

**Warning: Paper trade extensively before risking real capital. Start with the smallest possible position sizes.**

## Paper Trading

Always paper trade first to verify:

- Signal generation works in real-time
- Order logic handles edge cases
- Infrastructure is reliable
- Performance matches backtest expectations

```python
import pandas as pd
from datetime import datetime

class PaperTrader:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_history = []

    def buy(self, symbol, price, shares):
        cost = price * shares
        if cost > self.capital:
            shares = int(self.capital / price)
            cost = price * shares
        self.capital -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + shares
        self.trades.append({
            "time": datetime.now(), "action": "BUY",
            "symbol": symbol, "price": price, "shares": shares
        })

    def sell(self, symbol, price, shares=None):
        if symbol not in self.positions:
            return
        shares = shares or self.positions[symbol]
        self.capital += price * shares
        self.positions[symbol] -= shares
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        self.trades.append({
            "time": datetime.now(), "action": "SELL",
            "symbol": symbol, "price": price, "shares": shares
        })

    def portfolio_value(self, prices):
        value = self.capital
        for symbol, shares in self.positions.items():
            value += shares * prices.get(symbol, 0)
        return value

    def summary(self):
        df = pd.DataFrame(self.trades)
        print(f"Capital: {self.capital:,.2f}")
        print(f"Positions: {self.positions}")
        print(f"Total Trades: {len(self.trades)}")
        return df

# Usage
trader = PaperTrader(100000)
trader.buy("AAPL", 150.0, 100)
trader.sell("AAPL", 160.0, 100)
trader.summary()
```

## Alpaca API (Commission-Free US Stocks)

```python
from alpaca_trade_api import REST
import pandas as pd

# Paper trading endpoint
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, SECRET_KEY, BASE_URL)

# Account info
account = api.get_account()
print(f"Cash: {account.cash}")
print(f"Portfolio Value: {account.portfolio_value}")

# Get current price
bars = api.get_bars("AAPL", "1Day", limit=1)
current_price = bars[0].c
print(f"AAPL Price: {current_price}")

# Submit market order
order = api.submit_order(
    symbol="AAPL",
    qty=10,
    side="buy",
    type="market",
    time_in_force="day"
)
print(f"Order ID: {order.id}, Status: {order.status}")

# Submit limit order
order = api.submit_order(
    symbol="AAPL",
    qty=10,
    side="buy",
    type="limit",
    limit_price=145.00,
    time_in_force="gtc"
)

# Check positions
positions = api.list_positions()
for p in positions:
    print(f"{p.symbol}: {p.qty} shares, PnL: {p.unrealized_pl}")
```

## Interactive Brokers (via ib_insync)

```python
from ib_insync import IB, Stock, MarketOrder, LimitOrder

# Connect to TWS or IB Gateway
ib = IB()
ib.connect("127.0.0.1", 7497, clientId=1)  # 7497 = paper, 7496 = live

# Define contract
aapl = Stock("AAPL", "SMART", "USD")
ib.qualifyContracts(aapl)

# Get market data
ticker = ib.reqMktData(aapl)
ib.sleep(2)
print(f"AAPL Last: {ticker.last}, Bid: {ticker.bid}, Ask: {ticker.ask}")

# Market order
order = MarketOrder("BUY", 100)
trade = ib.placeOrder(aapl, order)
ib.sleep(1)
print(f"Order status: {trade.orderStatus.status}")

# Limit order
order = LimitOrder("BUY", 100, 145.00)
trade = ib.placeOrder(aapl, order)

# Check positions
positions = ib.positions()
for pos in positions:
    print(f"{pos.contract.symbol}: {pos.position} @ {pos.avgCost:.2f}")

ib.disconnect()
```

## Binance (Crypto)

```python
from binance.client import Client
import pandas as pd

API_KEY = "YOUR_API_KEY"
SECRET = "YOUR_SECRET"
client = Client(API_KEY, SECRET, testnet=True)  # testnet for paper trading

# Account balance
account = client.get_account()
balances = {b["asset"]: float(b["free"]) for b in account["balances"] if float(b["free"]) > 0}
print(balances)

# Current price
price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
print(f"BTC/USDT: {price}")

# Market order
order = client.create_order(
    symbol="BTCUSDT",
    side="BUY",
    type="MARKET",
    quantity=0.001
)

# Limit order
order = client.create_order(
    symbol="BTCUSDT",
    side="BUY",
    type="LIMIT",
    timeInForce="GTC",
    quantity=0.001,
    price="40000.00"
)

# Stop-loss order
order = client.create_order(
    symbol="BTCUSDT",
    side="SELL",
    type="STOP_LOSS_LIMIT",
    timeInForce="GTC",
    quantity=0.001,
    price="38000.00",
    stopPrice="38500.00"
)
```

## Order Types

| Type          | Description                                  | Use Case                       |
| ------------- | -------------------------------------------- | ------------------------------ |
| Market        | Execute immediately at best price            | Urgent entry/exit              |
| Limit         | Execute at specified price or better         | Patient entry, reduce slippage |
| Stop          | Becomes market order when price hits trigger | Stop-loss                      |
| Stop-Limit    | Becomes limit order when triggered           | Controlled stop-loss           |
| Trailing Stop | Stop moves with price                        | Lock in profits                |

## Slippage and Transaction Costs

```python
import numpy as np
import pandas as pd

def backtest_with_costs(returns, signal, commission=0.001, slippage=0.0005):
    """Realistic backtest including transaction costs."""
    position = signal.shift(1)
    trades = position.diff().abs()

    # Cost per trade: commission + slippage
    cost_per_trade = commission + slippage
    total_costs = trades * cost_per_trade

    gross_returns = position * returns
    net_returns = gross_returns - total_costs

    gross_cumulative = (1 + gross_returns).cumprod().iloc[-1] - 1
    net_cumulative = (1 + net_returns).cumprod().iloc[-1] - 1
    total_cost = total_costs.sum()

    print(f"Gross Return: {gross_cumulative:.2%}")
    print(f"Net Return:   {net_cumulative:.2%}")
    print(f"Total Costs:  {total_cost:.2%}")
    print(f"Num Trades:   {int(trades.sum())}")
    return net_returns

# Example
import yfinance as yf
df = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
returns = df["Close"].pct_change()
signal = pd.Series(
    np.where(df["Close"].rolling(20).mean() > df["Close"].rolling(50).mean(), 1, 0),
    index=df.index
)
net = backtest_with_costs(returns, signal)
```

## Latency Considerations

```python
import time
import requests

def measure_api_latency(url, n_requests=10):
    """Measure round-trip latency to trading API."""
    latencies = []
    for _ in range(n_requests):
        start = time.perf_counter()
        requests.get(url)
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)

    print(f"Mean Latency: {np.mean(latencies):.1f} ms")
    print(f"P95 Latency:  {np.percentile(latencies, 95):.1f} ms")
    print(f"Max Latency:  {max(latencies):.1f} ms")

# measure_api_latency("https://paper-api.alpaca.markets/v2/clock")
```

For most strategies (daily/hourly rebalance), latency under 1 second is fine. Only HFT requires sub-millisecond execution.

## Scheduling with APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def trading_job():
    """Run strategy logic."""
    now = datetime.now()
    logging.info(f"Running strategy at {now}")

    # 1. Fetch latest data
    # 2. Generate signals
    # 3. Execute orders
    # 4. Log results

scheduler = BlockingScheduler()

# Run at market open (9:30 AM ET) on weekdays
scheduler.add_job(trading_job, "cron", day_of_week="mon-fri", hour=9, minute=30)

# Run every 5 minutes during market hours
scheduler.add_job(trading_job, "cron", day_of_week="mon-fri",
                  hour="9-15", minute="*/5")

# scheduler.start()  # Blocks forever
```

## Logging Trades

```python
import logging
import json
from datetime import datetime
from pathlib import Path

class TradeLogger:
    def __init__(self, log_dir="logs"):
        Path(log_dir).mkdir(exist_ok=True)
        self.logger = logging.getLogger("trades")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(f"{log_dir}/trades_{datetime.now():%Y%m%d}.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.logger.addHandler(handler)

    def log_signal(self, symbol, signal, price, indicators):
        self.logger.info(json.dumps({
            "type": "signal", "symbol": symbol,
            "signal": signal, "price": price, "indicators": indicators
        }))

    def log_order(self, symbol, side, qty, price, order_id):
        self.logger.info(json.dumps({
            "type": "order", "symbol": symbol,
            "side": side, "qty": qty, "price": price, "order_id": order_id
        }))

    def log_fill(self, order_id, fill_price, fill_qty, commission):
        self.logger.info(json.dumps({
            "type": "fill", "order_id": order_id,
            "fill_price": fill_price, "fill_qty": fill_qty, "commission": commission
        }))

# Usage
logger = TradeLogger()
logger.log_signal("AAPL", "BUY", 150.25, {"rsi": 28, "sma_cross": True})
logger.log_order("AAPL", "BUY", 100, 150.25, "ORD-001")
logger.log_fill("ORD-001", 150.30, 100, 0.50)
```

## Monitoring Dashboard

```python
import pandas as pd
from datetime import datetime

class TradingMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.trades = []
        self.errors = []

    def record_trade(self, symbol, side, qty, price, pnl=0):
        self.trades.append({
            "time": datetime.now(), "symbol": symbol,
            "side": side, "qty": qty, "price": price, "pnl": pnl
        })

    def record_error(self, error_msg):
        self.errors.append({"time": datetime.now(), "error": error_msg})

    def status(self):
        uptime = datetime.now() - self.start_time
        df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()

        print(f"=== Trading Monitor ===")
        print(f"Uptime: {uptime}")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Errors: {len(self.errors)}")
        if len(df) > 0:
            print(f"Total PnL: {df['pnl'].sum():.2f}")
            print(f"Win Rate: {(df['pnl'] > 0).mean():.2%}")

monitor = TradingMonitor()
monitor.record_trade("AAPL", "BUY", 100, 150.0)
monitor.record_trade("AAPL", "SELL", 100, 155.0, pnl=500)
monitor.status()
```

---

## Key Takeaways

- Paper trade for at least 1 month before going live
- Alpaca is easiest for US stocks; Binance for crypto; IB for everything else
- Always account for slippage and commissions in backtests
- Use limit orders to reduce slippage when possible
- Log every signal, order, and fill for post-trade analysis
- APScheduler handles cron-like scheduling within Python
- Monitor for errors and unexpected behavior continuously

---

[prev: Chapter 7 - Machine Learning](chapter-07-ml.md) | [next: Chapter 9 - Going Live](chapter-09-live.md)
