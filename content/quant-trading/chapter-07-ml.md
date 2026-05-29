# Chapter 7: Machine Learning for Trading

[prev: Chapter 6 - Risk Management](chapter-06-risk.md) | [next: Chapter 8 - Execution](chapter-08-execution.md)

---

Machine learning can discover non-linear patterns in market data that traditional indicators miss. However, financial ML is uniquely challenging due to low signal-to-noise ratio and non-stationarity.

**Warning: ML models overfit easily on financial data. A model that looks great in backtest will often fail live. Always use proper time-series validation.**

## Feature Engineering

```python
import numpy as np
import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
close = df["Close"]

features = pd.DataFrame(index=df.index)

# Lagged returns
for lag in [1, 2, 3, 5, 10, 21]:
    features[f"return_{lag}d"] = close.pct_change(lag)

# Technical indicators as features
features["sma_ratio"] = close / close.rolling(20).mean()
features["volatility_20"] = close.pct_change().rolling(20).std()
features["volatility_60"] = close.pct_change().rolling(60).std()
features["rsi"] = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() /
                                 close.diff().clip(upper=0).abs().rolling(14).mean())
features["volume_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
features["high_low_range"] = (df["High"] - df["Low"]) / close
features["close_position"] = (close - df["Low"]) / (df["High"] - df["Low"])

# Target: next 5-day return direction (1 = up, 0 = down)
features["target"] = (close.shift(-5) > close).astype(int)

features = features.dropna()
print(f"Features shape: {features.shape}")
print(features.head())
```

## Time Series Train/Test Split

**Never use random splits for time series data.** Future data must not leak into training.

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

# Correct: chronological split
train_end = "2022-12-31"
X_train = features.loc[:train_end].drop("target", axis=1)
y_train = features.loc[:train_end, "target"]
X_test = features.loc[train_end:].drop("target", axis=1)
y_test = features.loc[train_end:, "target"]

print(f"Train: {X_train.index[0]} to {X_train.index[-1]} ({len(X_train)} samples)")
print(f"Test:  {X_test.index[0]} to {X_test.index[-1]} ({len(X_test)} samples)")

# Time Series Cross-Validation
tscv = TimeSeriesSplit(n_splits=5)
for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train)):
    print(f"Fold {fold}: train={len(train_idx)}, val={len(val_idx)}")
```

## Random Forest for Signal Prediction

```python
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
close = df["Close"]

# Build features
features = pd.DataFrame(index=df.index)
for lag in [1, 2, 3, 5, 10, 21]:
    features[f"return_{lag}d"] = close.pct_change(lag)
features["sma_ratio"] = close / close.rolling(20).mean()
features["volatility"] = close.pct_change().rolling(20).std()
features["rsi"] = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() /
                                 close.diff().clip(upper=0).abs().rolling(14).mean())
features["target"] = (close.shift(-5) > close).astype(int)
features = features.dropna()

# Split
train_end = "2022-12-31"
X_train = features.loc[:train_end].drop("target", axis=1)
y_train = features.loc[:train_end, "target"]
X_test = features.loc[train_end:].drop("target", axis=1)
y_test = features.loc[train_end:, "target"]

# Train
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))

# Feature importance
importance = pd.Series(model.feature_importances_, index=X_train.columns)
print("\nFeature Importance:")
print(importance.sort_values(ascending=False))
```

## XGBoost for Signal Prediction

```python
import numpy as np
import pandas as pd
import yfinance as yf
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
close = df["Close"]

# Features (same as above)
features = pd.DataFrame(index=df.index)
for lag in [1, 2, 3, 5, 10, 21]:
    features[f"return_{lag}d"] = close.pct_change(lag)
features["sma_ratio"] = close / close.rolling(20).mean()
features["volatility"] = close.pct_change().rolling(20).std()
features["rsi"] = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() /
                                 close.diff().clip(upper=0).abs().rolling(14).mean())
features["target"] = (close.shift(-5) > close).astype(int)
features = features.dropna()

train_end = "2022-12-31"
X_train = features.loc[:train_end].drop("target", axis=1)
y_train = features.loc[:train_end, "target"]
X_test = features.loc[train_end:].drop("target", axis=1)
y_test = features.loc[train_end:, "target"]

# XGBoost with regularization to prevent overfitting
model = XGBClassifier(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1.0,
    reg_lambda=1.0,
    random_state=42,
    eval_metric="logloss",
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

# Backtest the ML signal
positions = pd.Series(y_pred, index=X_test.index).shift(1)
market_returns = close.pct_change().loc[X_test.index]
strategy_returns = positions * market_returns
cumulative = (1 + strategy_returns).cumprod()
sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
print(f"ML Strategy Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Sharpe: {sharpe:.3f}")
```

## LSTM for Price Prediction

```python
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
close = df["Close"].values.reshape(-1, 1)

# Scale data
scaler = MinMaxScaler()
scaled = scaler.fit_transform(close)

# Create sequences
def create_sequences(data, lookback=60):
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

lookback = 60
X, y = create_sequences(scaled, lookback)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Time-series split
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build LSTM
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(1)
])
model.compile(optimizer="adam", loss="mse")
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1, verbose=0)

# Predict
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
actual = scaler.inverse_transform(y_test.reshape(-1, 1))

# Directional accuracy (more useful than price accuracy)
pred_direction = np.sign(np.diff(predictions.flatten()))
actual_direction = np.sign(np.diff(actual.flatten()))
directional_accuracy = (pred_direction == actual_direction).mean()
print(f"Directional Accuracy: {directional_accuracy:.4f}")
```

**Note**: LSTM price prediction is notoriously unreliable for actual trading. Directional accuracy above 55% is considered good. Use as one signal among many, never as sole decision maker.

## Avoiding Overfitting in Financial ML

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit

def check_overfitting(X, y, model_class, **model_params):
    """Compare train vs validation performance across time folds."""
    tscv = TimeSeriesSplit(n_splits=5)
    train_scores = []
    val_scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = model_class(**model_params)
        model.fit(X_tr, y_tr)

        train_scores.append(model.score(X_tr, y_tr))
        val_scores.append(model.score(X_val, y_val))

    print(f"Train Accuracy: {np.mean(train_scores):.4f} +/- {np.std(train_scores):.4f}")
    print(f"Val Accuracy:   {np.mean(val_scores):.4f} +/- {np.std(val_scores):.4f}")
    print(f"Overfit Gap:    {np.mean(train_scores) - np.mean(val_scores):.4f}")

# Example
# check_overfitting(X_train, y_train, RandomForestClassifier,
#                   n_estimators=100, max_depth=5, random_state=42)
```

Rules to prevent overfitting:

- Limit model complexity (shallow trees, fewer estimators)
- Use regularization (L1/L2, dropout)
- Keep feature count low relative to sample size
- Never optimize on test data
- Use walk-forward validation

## Walk-Forward Optimization

The gold standard for financial ML validation — retrain periodically on expanding window:

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def walk_forward_backtest(features, train_window=504, test_window=63):
    """Walk-forward: train on past N days, predict next M days, slide forward."""
    X = features.drop("target", axis=1)
    y = features["target"]

    predictions = []
    actuals = []
    dates = []

    for start in range(0, len(features) - train_window - test_window, test_window):
        train_end = start + train_window
        test_end = train_end + test_window

        X_train = X.iloc[start:train_end]
        y_train = y.iloc[start:train_end]
        X_test = X.iloc[train_end:test_end]
        y_test = y.iloc[train_end:test_end]

        model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        predictions.extend(preds)
        actuals.extend(y_test.values)
        dates.extend(X_test.index)

    results = pd.DataFrame({
        "prediction": predictions,
        "actual": actuals
    }, index=dates)

    accuracy = (results["prediction"] == results["actual"]).mean()
    print(f"Walk-Forward Accuracy: {accuracy:.4f}")
    print(f"Total predictions: {len(results)}")
    return results

# Usage (assuming 'features' DataFrame from earlier)
# results = walk_forward_backtest(features)
```

## Complete ML Trading Pipeline

```python
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# 1. Data
df = yf.download("AAPL", start="2018-01-01", end="2024-01-01")
close = df["Close"]

# 2. Features
features = pd.DataFrame(index=df.index)
for lag in [1, 2, 3, 5, 10, 21]:
    features[f"ret_{lag}"] = close.pct_change(lag)
features["vol_20"] = close.pct_change().rolling(20).std()
features["sma_ratio"] = close / close.rolling(20).mean()
features["rsi"] = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() /
                                 close.diff().clip(upper=0).abs().rolling(14).mean())
features["target"] = (close.shift(-1) > close).astype(int)
features = features.dropna()

# 3. Walk-forward backtest
train_size = 504  # 2 years
step_size = 21    # Retrain monthly

all_preds = []
all_dates = []

for i in range(train_size, len(features) - 1, step_size):
    X_train = features.iloc[i - train_size:i].drop("target", axis=1)
    y_train = features.iloc[i - train_size:i]["target"]

    end = min(i + step_size, len(features))
    X_test = features.iloc[i:end].drop("target", axis=1)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    all_preds.extend(preds)
    all_dates.extend(X_test.index)

# 4. Evaluate
signals = pd.Series(all_preds, index=all_dates)
market_returns = close.pct_change().loc[signals.index]
strategy_returns = signals.shift(1) * market_returns
strategy_returns = strategy_returns.dropna()

cumulative = (1 + strategy_returns).cumprod()
buy_hold = (1 + market_returns.loc[strategy_returns.index]).cumprod()

sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
print(f"ML Strategy Return: {cumulative.iloc[-1] - 1:.2%}")
print(f"Buy & Hold Return: {buy_hold.iloc[-1] - 1:.2%}")
print(f"Sharpe Ratio: {sharpe:.3f}")
```

---

## Key Takeaways

- Feature engineering matters more than model choice
- Never use random train/test splits — always respect time ordering
- Walk-forward optimization is the most realistic validation method
- XGBoost typically outperforms deep learning on tabular financial data
- LSTM is useful for sequence patterns but prone to overfitting
- A 55% directional accuracy can be profitable with proper risk management
- Simpler models generalize better in non-stationary markets

---

[prev: Chapter 6 - Risk Management](chapter-06-risk.md) | [next: Chapter 8 - Execution](chapter-08-execution.md)
