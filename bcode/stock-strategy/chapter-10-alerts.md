# Chapter 10: Alerts & Automation

[← Chapter 9: Stock Screener](chapter-09-screener.md)

---

## Stop Watching Charts

You've built strategies, backtested them, and screened for candidates. The last piece: automation. Let the code watch the market and alert you when something interesting happens.

> **Disclaimer:** This is educational content, not financial advice. Automated alerts are tools for awareness, not trading signals.

## Define Alert Conditions

```python
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def check_alerts(watchlist, conditions):
    """Check alert conditions for a list of tickers."""
    alerts = []

    for ticker in watchlist:
        try:
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty:
                continue

            info = yf.Ticker(ticker).info
            price = df['Close'].iloc[-1]

            # Calculate indicators
            sma_20 = df['Close'].rolling(20).mean().iloc[-1]
            sma_50 = df['Close'].rolling(50).mean().iloc[-1]

            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]

            avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
            today_vol = df['Volume'].iloc[-1]

            # Check conditions
            if rsi < 30:
                alerts.append(f"🟢 {ticker}: RSI oversold ({rsi:.0f})")
            if rsi > 70:
                alerts.append(f"🔴 {ticker}: RSI overbought ({rsi:.0f})")
            if price > sma_20 and df['Close'].iloc[-2] <= df['Close'].rolling(20).mean().iloc[-2]:
                alerts.append(f"📈 {ticker}: Price crossed above SMA20")
            if price < sma_20 and df['Close'].iloc[-2] >= df['Close'].rolling(20).mean().iloc[-2]:
                alerts.append(f"📉 {ticker}: Price crossed below SMA20")
            if today_vol > avg_vol * 2:
                alerts.append(f"🔊 {ticker}: Volume spike ({today_vol/avg_vol:.1f}x average)")

        except Exception as e:
            alerts.append(f"⚠️ {ticker}: Error — {e}")

    return alerts

# Run alerts
watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMD", "META"]
alerts = check_alerts(watchlist, {})

print(f"\n--- Alerts ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---")
if alerts:
    for alert in alerts:
        print(f"  {alert}")
else:
    print("  No alerts triggered today.")
```

## Sending Email Alerts

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(alerts, recipient):
    """Send alert summary via email (Gmail example)."""
    if not alerts:
        return

    subject = f"Stock Alerts — {datetime.now().strftime('%Y-%m-%d')}"
    body = "Today's alerts:\n\n" + "\n".join(alerts)
    body += "\n\n---\nThis is automated, not financial advice."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"
    msg['To'] = recipient

    # Use app password, not your real password
    # Generate at: https://myaccount.google.com/apppasswords
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)

    print(f"Email sent to {recipient}")

# Uncomment to send:
# send_email_alert(alerts, "you@example.com")
```

## Scheduling with Cron

Save your alert script as `daily_alerts.py`, then schedule it:

```bash
# Run every weekday at 4:30 PM ET (after market close)
# Edit crontab: crontab -e
30 16 * * 1-5 /usr/bin/python3 /path/to/daily_alerts.py >> /path/to/alerts.log 2>&1
```

For Windows, use Task Scheduler. For cloud, use AWS Lambda + CloudWatch Events or a simple cron on a $5/month VPS.

## Simple Streamlit Dashboard

```python
# Save as dashboard.py, run with: streamlit run dashboard.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Portfolio Dashboard")
st.caption("Educational tool — not financial advice")

# Sidebar — portfolio input
watchlist = st.sidebar.text_input(
    "Watchlist (comma-separated)", "AAPL,MSFT,GOOGL,NVDA"
).split(",")
watchlist = [t.strip().upper() for t in watchlist]
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)

# Fetch data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(tickers, period):
    return yf.download(tickers, period=period, progress=False)

data = load_data(watchlist, period)

# Price chart
st.subheader("Price Performance")
normalized = data['Close'] / data['Close'].iloc[0] * 100
fig = go.Figure()
for ticker in watchlist:
    if ticker in normalized.columns:
        fig.add_trace(go.Scatter(x=normalized.index, y=normalized[ticker],
                                 name=ticker, mode='lines'))
fig.update_layout(yaxis_title="Normalized (Base=100)", height=400)
st.plotly_chart(fig, use_container_width=True)

# Alerts section
st.subheader("🚨 Active Alerts")
for ticker in watchlist:
    try:
        df = data['Close'][[ticker]].dropna() if ticker in data['Close'].columns else pd.DataFrame()
        if df.empty:
            continue
        prices = df[ticker]
        rsi_delta = prices.diff()
        gain = rsi_delta.where(rsi_delta > 0, 0).rolling(14).mean()
        loss = -rsi_delta.where(rsi_delta < 0, 0).rolling(14).mean()
        rsi = (100 - (100 / (1 + gain / loss))).iloc[-1]

        if rsi < 30:
            st.warning(f"{ticker}: RSI oversold ({rsi:.0f})")
        elif rsi > 70:
            st.error(f"{ticker}: RSI overbought ({rsi:.0f})")
        else:
            st.success(f"{ticker}: RSI neutral ({rsi:.0f})")
    except Exception:
        pass

# Quick stats table
st.subheader("Quick Stats")
stats = []
for ticker in watchlist:
    if ticker in data['Close'].columns:
        prices = data['Close'][ticker].dropna()
        stats.append({
            'Ticker': ticker,
            'Price': f"${prices.iloc[-1]:.2f}",
            'Change': f"{(prices.iloc[-1]/prices.iloc[0]-1)*100:+.1f}%",
            'High': f"${prices.max():.2f}",
            'Low': f"${prices.min():.2f}",
        })
st.dataframe(pd.DataFrame(stats).set_index('Ticker'), use_container_width=True)
```

Run it:
```bash
pip install streamlit
streamlit run dashboard.py
```

## Earnings Calendar Alert

```python
def check_upcoming_earnings(tickers, days_ahead=7):
    """Alert if earnings are within N days."""
    from datetime import timedelta
    today = datetime.now()
    alerts = []

    for ticker in tickers:
        try:
            cal = yf.Ticker(ticker).calendar
            if cal is not None and 'Earnings Date' in cal:
                earnings_date = cal['Earnings Date'][0]
                days_until = (earnings_date - today).days
                if 0 < days_until <= days_ahead:
                    alerts.append(f"📅 {ticker}: Earnings in {days_until} days ({earnings_date.strftime('%b %d')})")
        except Exception:
            pass

    return alerts

earnings_alerts = check_upcoming_earnings(watchlist)
for a in earnings_alerts:
    print(a)
```

## What You Learned

- **Alert conditions** — RSI extremes, MA crossovers, volume spikes
- **Email notifications** — automated alerts via SMTP
- **Cron scheduling** — run checks daily without manual effort
- **Streamlit dashboard** — visual portfolio monitor in ~50 lines
- **Earnings calendar** — never be surprised by an earnings date

## Course Complete

You now have a complete toolkit:

1. **Fetch data** — yfinance for price and fundamental data
2. **Visualize** — candlestick charts, interactive plotly
3. **Analyze** — technical indicators and fundamental metrics
4. **Strategize** — rule-based entry/exit signals
5. **Backtest** — simulate before risking real money
6. **Manage risk** — position sizing, stop-losses, diversification
7. **Monitor** — portfolio analysis and rebalancing
8. **Screen** — find new candidates systematically
9. **Automate** — alerts and dashboards

**Remember:** This entire course is educational. The market is humbling. Start with paper trading, keep positions small, and never stop learning.

---

[← Chapter 9: Stock Screener](chapter-09-screener.md)
