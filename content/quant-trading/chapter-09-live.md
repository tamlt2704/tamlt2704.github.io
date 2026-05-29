# Chapter 9: Going Live

[prev: Chapter 8 - Execution](chapter-08-execution.md) | [next: Overview](chapter-00-overview.md)

---

Going live is the final step — and the most dangerous. This chapter covers the infrastructure and safeguards needed to run a trading system in production.

**Warning: Live trading with real money carries substantial risk of loss. Start with the minimum possible capital. Never trade money you cannot afford to lose.**

## Infrastructure

### VPS / Cloud Options

| Provider           | Use Case            | Cost         |
| ------------------ | ------------------- | ------------ |
| AWS EC2 (t3.small) | General purpose     | ~`$15`/month |
| DigitalOcean       | Simple deployment   | ~`$12`/month |
| Google Cloud       | ML-heavy strategies | Variable     |
| Dedicated VPS      | Low-latency         | ~`$30`/month |

Key requirements:

- Low latency to broker/exchange
- High uptime (99.9%+)
- Automatic restart on failure
- Sufficient RAM for data processing

```python
# systemd service file for auto-restart: /etc/systemd/system/trading-bot.service
# [Unit]
# Description=Trading Bot
# After=network.target
#
# [Service]
# Type=simple
# User=trader
# WorkingDirectory=/home/trader/bot
# ExecStart=/home/trader/bot/venv/bin/python main.py
# Restart=always
# RestartSec=10
#
# [Install]
# WantedBy=multi-user.target
```

## Real-Time Data Feeds (WebSocket)

```python
import asyncio
import websockets
import json
from datetime import datetime

class BinanceWebSocket:
    def __init__(self, symbol="btcusdt", on_price=None):
        self.url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        self.on_price = on_price

    async def connect(self):
        async with websockets.connect(self.url) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                price = float(data["p"])
                timestamp = datetime.fromtimestamp(data["T"] / 1000)

                if self.on_price:
                    self.on_price(price, timestamp)

def handle_price(price, timestamp):
    print(f"[{timestamp}] BTC/USDT: {price:.2f}")

# Usage:
# ws = BinanceWebSocket("btcusdt", on_price=handle_price)
# asyncio.run(ws.connect())
```

### Alpaca WebSocket for US Stocks

```python
import asyncio
import websockets
import json

async def alpaca_stream(api_key, secret_key, symbols):
    url = "wss://stream.data.alpaca.markets/v2/iex"

    async with websockets.connect(url) as ws:
        # Authenticate
        auth = {"action": "auth", "key": api_key, "secret": secret_key}
        await ws.send(json.dumps(auth))
        response = await ws.recv()
        print(f"Auth: {response}")

        # Subscribe to trades
        subscribe = {"action": "subscribe", "trades": symbols}
        await ws.send(json.dumps(subscribe))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            for trade in data:
                if trade.get("T") == "t":
                    print(f"{trade['S']}: {trade['p']} x {trade['s']}")

# asyncio.run(alpaca_stream("KEY", "SECRET", ["AAPL", "MSFT"]))
```

## Order Management System

```python
import pandas as pd
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderManager:
    def __init__(self):
        self.orders = {}
        self.order_id = 0

    def create_order(self, symbol, side, qty, order_type="market", price=None):
        self.order_id += 1
        order = {
            "id": self.order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "type": order_type,
            "price": price,
            "status": OrderStatus.PENDING,
            "created_at": datetime.now(),
            "filled_at": None,
            "fill_price": None,
        }
        self.orders[self.order_id] = order
        return self.order_id

    def fill_order(self, order_id, fill_price):
        order = self.orders[order_id]
        order["status"] = OrderStatus.FILLED
        order["filled_at"] = datetime.now()
        order["fill_price"] = fill_price

    def cancel_order(self, order_id):
        self.orders[order_id]["status"] = OrderStatus.CANCELLED

    def open_orders(self):
        return {k: v for k, v in self.orders.items() if v["status"] == OrderStatus.PENDING}

    def filled_orders(self):
        return {k: v for k, v in self.orders.items() if v["status"] == OrderStatus.FILLED}

# Usage
om = OrderManager()
oid = om.create_order("AAPL", "buy", 100, "limit", 150.0)
om.fill_order(oid, 149.95)
print(om.orders[oid])
```

## Risk Checks Before Execution

```python
class PreTradeRiskCheck:
    def __init__(self, max_position_pct=0.20, max_daily_loss=0.02,
                 max_order_value=50000, max_orders_per_day=50):
        self.max_position_pct = max_position_pct
        self.max_daily_loss = max_daily_loss
        self.max_order_value = max_order_value
        self.max_orders_per_day = max_orders_per_day
        self.daily_orders = 0
        self.daily_pnl = 0

    def check(self, order, portfolio_value, current_positions):
        """Return (approved, reason)."""
        order_value = order["qty"] * (order["price"] or 0)

        # Check max order size
        if order_value > self.max_order_value:
            return False, f"Order value {order_value} exceeds max {self.max_order_value}"

        # Check position concentration
        position_pct = order_value / portfolio_value
        if position_pct > self.max_position_pct:
            return False, f"Position {position_pct:.1%} exceeds max {self.max_position_pct:.1%}"

        # Check daily loss limit
        if self.daily_pnl / portfolio_value < -self.max_daily_loss:
            return False, f"Daily loss limit reached"

        # Check order count
        if self.daily_orders >= self.max_orders_per_day:
            return False, f"Max daily orders reached"

        self.daily_orders += 1
        return True, "Approved"

# Usage
risk = PreTradeRiskCheck()
order = {"symbol": "AAPL", "side": "buy", "qty": 100, "price": 150.0}
approved, reason = risk.check(order, portfolio_value=100000, current_positions={})
print(f"{'APPROVED' if approved else 'REJECTED'}: {reason}")
```

## Position Tracking

```python
import pandas as pd
from datetime import datetime

class PositionTracker:
    def __init__(self):
        self.positions = {}  # symbol -> {qty, avg_cost, realized_pnl}

    def update(self, symbol, side, qty, price):
        if symbol not in self.positions:
            self.positions[symbol] = {"qty": 0, "avg_cost": 0, "realized_pnl": 0}

        pos = self.positions[symbol]

        if side == "buy":
            total_cost = pos["avg_cost"] * pos["qty"] + price * qty
            pos["qty"] += qty
            pos["avg_cost"] = total_cost / pos["qty"] if pos["qty"] > 0 else 0
        elif side == "sell":
            pnl = (price - pos["avg_cost"]) * qty
            pos["realized_pnl"] += pnl
            pos["qty"] -= qty
            if pos["qty"] == 0:
                pos["avg_cost"] = 0

    def unrealized_pnl(self, current_prices):
        total = 0
        for symbol, pos in self.positions.items():
            if pos["qty"] > 0 and symbol in current_prices:
                total += (current_prices[symbol] - pos["avg_cost"]) * pos["qty"]
        return total

    def summary(self, current_prices=None):
        for symbol, pos in self.positions.items():
            unrealized = 0
            if current_prices and symbol in current_prices:
                unrealized = (current_prices[symbol] - pos["avg_cost"]) * pos["qty"]
            print(f"{symbol}: {pos['qty']} shares @ {pos['avg_cost']:.2f}, "
                  f"Realized: {pos['realized_pnl']:.2f}, Unrealized: {unrealized:.2f}")

# Usage
tracker = PositionTracker()
tracker.update("AAPL", "buy", 100, 150.0)
tracker.update("AAPL", "buy", 50, 155.0)
tracker.update("AAPL", "sell", 75, 160.0)
tracker.summary({"AAPL": 158.0})
```

## PnL Calculation

```python
import pandas as pd
from datetime import datetime

class PnLCalculator:
    def __init__(self):
        self.trades = []

    def add_trade(self, symbol, side, qty, price, timestamp=None):
        self.trades.append({
            "timestamp": timestamp or datetime.now(),
            "symbol": symbol, "side": side, "qty": qty, "price": price
        })

    def calculate(self):
        df = pd.DataFrame(self.trades)
        if df.empty:
            return {}

        results = {}
        for symbol in df["symbol"].unique():
            sym_trades = df[df["symbol"] == symbol].copy()
            buys = sym_trades[sym_trades["side"] == "buy"]
            sells = sym_trades[sym_trades["side"] == "sell"]

            total_bought = (buys["qty"] * buys["price"]).sum()
            total_sold = (sells["qty"] * sells["price"]).sum()
            net_qty = buys["qty"].sum() - sells["qty"].sum()

            results[symbol] = {
                "realized_pnl": total_sold - total_bought * (sells["qty"].sum() / buys["qty"].sum()) if buys["qty"].sum() > 0 else 0,
                "net_position": net_qty,
                "num_trades": len(sym_trades),
            }
        return results

calc = PnLCalculator()
calc.add_trade("AAPL", "buy", 100, 150.0)
calc.add_trade("AAPL", "sell", 50, 160.0)
print(calc.calculate())
```

## Alerts (Telegram)

```python
import requests

class TelegramAlert:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send(self, message):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        return response.ok

    def alert_trade(self, symbol, side, qty, price):
        msg = f"*Trade Executed*\n{side.upper()} {qty} {symbol} @ {price:.2f}"
        self.send(msg)

    def alert_error(self, error_msg):
        msg = f"*ERROR*\n{error_msg}"
        self.send(msg)

    def alert_daily_summary(self, pnl, positions):
        msg = f"*Daily Summary*\nPnL: {pnl:.2f}\nPositions: {positions}"
        self.send(msg)

# Usage:
# alert = TelegramAlert("BOT_TOKEN", "CHAT_ID")
# alert.alert_trade("AAPL", "buy", 100, 150.25)
```

## Email Alerts

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body, to_email, from_email, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.send_message(msg)

# send_email_alert(
#     "Trading Alert: Position Opened",
#     "Bought 100 AAPL @ 150.25",
#     "trader@email.com", "bot@email.com", "app_password"
# )
```

## Disaster Recovery

```python
import json
from pathlib import Path
from datetime import datetime

class StateManager:
    """Persist trading state for crash recovery."""

    def __init__(self, state_file="state/trading_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(exist_ok=True)

    def save(self, positions, pending_orders, capital):
        state = {
            "timestamp": datetime.now().isoformat(),
            "positions": positions,
            "pending_orders": pending_orders,
            "capital": capital,
        }
        self.state_file.write_text(json.dumps(state, indent=2))

    def load(self):
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return None

    def recover(self):
        """Recover state after crash."""
        state = self.load()
        if state is None:
            print("No saved state found. Starting fresh.")
            return None

        print(f"Recovering state from {state['timestamp']}")
        print(f"Positions: {state['positions']}")
        print(f"Pending Orders: {state['pending_orders']}")
        print(f"Capital: {state['capital']}")
        return state

# Save state periodically
sm = StateManager()
sm.save(
    positions={"AAPL": {"qty": 100, "avg_cost": 150.0}},
    pending_orders=[],
    capital=85000.0
)

# On restart
recovered = sm.recover()
```

## Regulatory Considerations

- **Pattern Day Trader (US)**: If you make 4+ day trades in 5 business days with a margin account, you need `$25,000` minimum equity
- **Tax implications**: Short-term capital gains are taxed as ordinary income; keep detailed records
- **Wash sale rule (US)**: Cannot claim a loss if you repurchase the same security within 30 days
- **Crypto**: Regulations vary by jurisdiction; many exchanges require KYC
- **Algorithmic trading registration**: In some jurisdictions, automated trading above certain thresholds requires registration

## Production Checklist

Before going live:

- [ ] Paper traded for 30+ days with consistent results
- [ ] Risk checks prevent catastrophic losses
- [ ] State persistence handles crashes gracefully
- [ ] Alerts notify you of errors and unusual activity
- [ ] Kill switch can flatten all positions immediately
- [ ] Logging captures every decision and execution
- [ ] Backtest matches paper trading results (within reason)
- [ ] Capital is money you can afford to lose
- [ ] You understand the tax implications
- [ ] Infrastructure has redundancy (backup server, multiple internet connections)

## Kill Switch

```python
class KillSwitch:
    """Emergency: close all positions and stop trading."""

    def __init__(self, api):
        self.api = api
        self.active = True

    def trigger(self, reason="Manual trigger"):
        print(f"KILL SWITCH ACTIVATED: {reason}")
        self.active = False

        # Cancel all open orders
        self.api.cancel_all_orders()

        # Close all positions
        positions = self.api.list_positions()
        for pos in positions:
            self.api.submit_order(
                symbol=pos.symbol,
                qty=abs(int(pos.qty)),
                side="sell" if int(pos.qty) > 0 else "buy",
                type="market",
                time_in_force="day"
            )
        print("All positions closed. Trading halted.")

# Usage:
# kill = KillSwitch(alpaca_api)
# kill.trigger("Max daily loss exceeded")
```

---

## Key Takeaways

- Infrastructure reliability is non-negotiable for live trading
- WebSocket feeds provide real-time data; REST APIs for order management
- Pre-trade risk checks prevent catastrophic errors
- Persist state to disk for crash recovery
- Set up alerts for trades, errors, and daily summaries
- Always have a kill switch ready
- Start with minimum capital and scale up only after proving consistency
- Understand regulatory requirements in your jurisdiction

---

**Final Disclaimer: Quantitative trading involves substantial risk. The strategies and code in this series are for educational purposes only. Past performance does not guarantee future results. Never trade with money you cannot afford to lose.**

---

[prev: Chapter 8 - Execution](chapter-08-execution.md) | [next: Overview](chapter-00-overview.md)
