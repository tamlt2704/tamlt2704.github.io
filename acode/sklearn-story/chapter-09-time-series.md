# Chapter 9: The Model Works — Until Next Month

[← Chapter 8: Which Features Actually Matter?](chapter-08-feature-importance.md) | [Chapter 10: Ship It →](chapter-10-production.md)

---

## The Disaster

It's July. The model has been running for two weeks. Predictions are solid — MAE around $380, Chef Marco is happy, Priya is happy.

Then August hits. A new restaurant joins (greenleaf_013). A heatwave pushes temperatures to 38°C — higher than anything in training data. A food festival brings 3× normal traffic to three locations.

The model's predictions are suddenly off by $1,500+. Chef Marco calls again.

> "Your thing said 150 covers. I got 450. I ran out of everything by 7pm."

You check the metrics. The model hasn't changed. The *world* changed.

---

## The Problem: Random Splits Lie About Time

```python
# chapter_09.py
"""Chapter 9: Temporal validation, data drift, and retraining strategies."""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
df = df.sort_values("date").reset_index(drop=True)

numeric_features = ["temperature_c", "marketing_spend", "month", "is_weekend"]
categorical_features = ["day_of_week", "restaurant_id"]

X = df[numeric_features + categorical_features]
y = df["revenue"]
```

Remember our cross-validation from earlier? It used random 5-fold splits. That means future data leaked into training folds. A model trained on June data was tested on January data — which it had already "seen" patterns from.

In real life, you train on the past and predict the future. Random splits don't simulate this.

```python
# Standard random CV (what we've been doing)
pipeline = Pipeline([
    ("preprocessor", ColumnTransformer(transformers=[
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
        ]), categorical_features),
    ])),
    ("model", GradientBoostingRegressor(n_estimators=300, max_depth=5, random_state=42)),
])

random_cv = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
print(f"Random CV R²: {random_cv.mean():.4f} ± {random_cv.std():.4f}")
```

```
Random CV R²: 0.8567 ± 0.0038
```

### Temporal Split: The Honest Evaluation

```python
# Time-series split: always train on past, test on future
tscv = TimeSeriesSplit(n_splits=5)

temporal_cv = cross_val_score(pipeline, X, y, cv=tscv, scoring="r2")
print(f"Temporal CV R²: {temporal_cv.mean():.4f} ± {temporal_cv.std():.4f}")
```

```
Temporal CV R²: 0.7823 ± 0.0234
```

Lower and more variable. This is the honest number — how the model actually performs when predicting the future. The gap (0.86 vs 0.78) is the "temporal leakage" we were hiding.

---

## Visualize the Temporal Splits

```python
fig, axes = plt.subplots(5, 1, figsize=(12, 10), sharex=True)

for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
    train_dates = df.iloc[train_idx]["date"]
    test_dates = df.iloc[test_idx]["date"]

    axes[i].axvspan(train_dates.min(), train_dates.max(), alpha=0.3, color="blue", label="Train")
    axes[i].axvspan(test_dates.min(), test_dates.max(), alpha=0.3, color="orange", label="Test")
    axes[i].set_title(f"Fold {i+1}: Train {train_dates.min().date()} → {train_dates.max().date()} | "
                      f"Test {test_dates.min().date()} → {test_dates.max().date()}")
    axes[i].legend(loc="upper left")

plt.tight_layout()
plt.savefig("plots/ch09_temporal_splits.png", dpi=150)
plt.show()
```

Each fold trains on everything before a cutoff date and tests on everything after. This is how the model will actually be used.

---

## Detect Drift: When the World Changes

```python
# Split into monthly chunks and track performance
df["year_month"] = df["date"].dt.to_period("M")

# Train on first 12 months, evaluate on each subsequent month
train_end = "2023-12-31"
train_mask = df["date"] <= train_end

X_train_full = X[train_mask]
y_train_full = y[train_mask]

pipeline.fit(X_train_full, y_train_full)

# Evaluate on each month of 2024
monthly_scores = []
for period, group in df[~train_mask].groupby("year_month"):
    X_month = X.loc[group.index]
    y_month = y.loc[group.index]
    y_pred = pipeline.predict(X_month)

    mae = mean_absolute_error(y_month, y_pred)
    r2 = r2_score(y_month, y_pred)
    monthly_scores.append({"month": str(period), "mae": mae, "r2": r2, "n_rows": len(group)})

scores_df = pd.DataFrame(monthly_scores)
print(scores_df.to_string(index=False))
```

```
    month      mae      r2  n_rows
  2024-01   398.45  0.7912     372
  2024-02   412.34  0.7834     348
  2024-03   425.67  0.7756     372
  2024-04   456.78  0.7523     360
  2024-05   489.12  0.7345     372
  2024-06   534.56  0.7012     360
```

Performance degrades over time. Each month further from training data, the model gets worse. This is **data drift** — the relationship between features and target slowly changes.

```python
# Plot the degradation
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(scores_df["month"], scores_df["mae"], "o-", color="red", label="MAE ($)")
ax1.set_xlabel("Month")
ax1.set_ylabel("MAE ($)", color="red")
ax1.tick_params(axis="y", labelcolor="red")

ax2 = ax1.twinx()
ax2.plot(scores_df["month"], scores_df["r2"], "s-", color="blue", label="R²")
ax2.set_ylabel("R²", color="blue")
ax2.tick_params(axis="y", labelcolor="blue")

ax1.set_title("Model Performance Over Time (Trained on 2023 Data)")
fig.legend(loc="upper right", bbox_to_anchor=(0.85, 0.85))
plt.tight_layout()
plt.savefig("plots/ch09_drift.png", dpi=150)
plt.show()
```

---

## The Fix: Rolling Retrain

Instead of training once and hoping forever, retrain regularly on recent data.

```python
# Strategy: retrain monthly on the last 6 months of data
from sklearn.base import clone

rolling_results = []
months_2024 = df[df["date"] >= "2024-01-01"]["year_month"].unique()

for target_month in months_2024:
    # Training window: 6 months before the target month
    target_start = target_month.start_time
    train_start = target_start - pd.DateOffset(months=6)

    train_mask = (df["date"] >= train_start) & (df["date"] < target_start)
    test_mask = df["year_month"] == target_month

    if train_mask.sum() == 0 or test_mask.sum() == 0:
        continue

    X_train_roll = X[train_mask]
    y_train_roll = y[train_mask]
    X_test_roll = X[test_mask]
    y_test_roll = y[test_mask]

    fresh_pipeline = clone(pipeline)
    fresh_pipeline.fit(X_train_roll, y_train_roll)
    y_pred_roll = fresh_pipeline.predict(X_test_roll)

    mae = mean_absolute_error(y_test_roll, y_pred_roll)
    r2 = r2_score(y_test_roll, y_pred_roll)
    rolling_results.append({"month": str(target_month), "mae": mae, "r2": r2})

rolling_df = pd.DataFrame(rolling_results)
print("\n--- Rolling retrain (6-month window) ---")
print(rolling_df.to_string(index=False))
```

```
--- Rolling retrain (6-month window) ---
    month      mae      r2
  2024-01   387.23  0.8012
  2024-02   392.45  0.7978
  2024-03   395.12  0.7945
  2024-04   401.34  0.7889
  2024-05   398.67  0.7912
  2024-06   405.23  0.7856
```

Much more stable! MAE stays around $400 instead of degrading to $535. The model adapts to recent patterns.

---

## Monitoring: Know When to Retrain

You can't retrain every day (expensive) but you can't wait until Chef Marco calls (too late). Set up monitoring:

```python
def check_drift(recent_mae, baseline_mae, threshold=1.2):
    """Alert if recent MAE exceeds baseline by more than 20%."""
    ratio = recent_mae / baseline_mae
    if ratio > threshold:
        print(f"⚠️  DRIFT DETECTED: MAE ratio = {ratio:.2f} (threshold: {threshold})")
        print(f"    Baseline MAE: ${baseline_mae:.2f}")
        print(f"    Recent MAE:   ${recent_mae:.2f}")
        print(f"    → Retrain recommended")
        return True
    else:
        print(f"✓ Model healthy: MAE ratio = {ratio:.2f}")
        return False

# Example: compare last week's MAE to training MAE
baseline_mae = 395.0  # from cross-validation
recent_mae = 534.56   # from June 2024 (static model)

check_drift(recent_mae, baseline_mae)
```

```
⚠️  DRIFT DETECTED: MAE ratio = 1.35 (threshold: 1.2)
    Baseline MAE: $395.00
    Recent MAE:   $534.56
    → Retrain recommended
```

---

## Handling New Restaurants

greenleaf_013 joined in August. The model has never seen it. With `handle_unknown="ignore"` in OneHotEncoder, it gets all-zeros for the restaurant column — essentially predicting with the average restaurant baseline.

```python
# For new restaurants: use the first 2 weeks of data to establish a baseline
# Then retrain to include them

# Quick check: how does the model do on "unknown" restaurants?
# Simulate by predicting for a restaurant not in training
print("New restaurant gets average-restaurant predictions until retrained.")
print("First 2 weeks: collect data → retrain → personalized predictions.")
```

This is acceptable for the first two weeks. After that, retrain with the new restaurant's data included.

---

## Report to Priya

> **Temporal validation and drift analysis:**
>
> | Strategy | Avg MAE | Stability |
> |---|---|---|
> | Static model (trained once) | $453 (degrades to $535) | Worsens monthly |
> | Rolling retrain (6-month window) | $397 (stable) | Consistent |
>
> **Recommendations:**
> 1. Use `TimeSeriesSplit` for honest evaluation — random CV overestimates by ~8%
> 2. Retrain monthly on a rolling 6-month window
> 3. Monitor MAE weekly — alert if it exceeds 120% of baseline
> 4. New restaurants: 2-week data collection period, then include in next retrain
>
> The model isn't a one-time build. It's a living system that needs feeding.

Priya: "Good. Now package it so anyone on the team can run predictions without understanding scikit-learn."

---

## What You Learned

- **Random cross-validation leaks future data** into training — use `TimeSeriesSplit` for temporal data
- **Data drift** = the world changes after training; model performance degrades over time
- **Rolling retrain** keeps the model fresh by training on recent data
- **Monitoring** detects drift before stakeholders notice bad predictions
- The gap between random CV and temporal CV reveals how much "temporal leakage" inflated your metrics
- New categories (restaurants, products) need a cold-start strategy
- A model in production is a system, not a file — it needs monitoring, retraining, and alerting

---

[Next: Chapter 10 — "Ship It" →](chapter-10-production.md)
