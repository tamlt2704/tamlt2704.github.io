# Chapter 3: Your First Model is Terrible

[← Chapter 2: Why is Tuesday Weird?](chapter-02-eda.md) | [Chapter 4: The Avocado Incident →](chapter-04-overfitting.md)

---

## The Task

Priya's standup:

> "Predict tomorrow's revenue for each restaurant. Start with the simplest thing that could work. I want a number I can show Chef Marco."

Simple. You know linear regression from school. Fit a line. Make predictions. Ship it.

How hard can it be?

---

## The Simplest Thing That Could Work

```python
# chapter_03.py
"""Chapter 3: First model — Linear Regression, train/test split, baseline metrics."""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])

# Drop rows with missing revenue (our target)
df = df.dropna(subset=["revenue"])
print(f"Working with {len(df)} rows")
```

### Pick Features

From the EDA, we know temperature, marketing spend, and covers correlate with revenue. Let's use the numeric columns:

```python
feature_cols = ["temperature_c", "marketing_spend", "covers", "staff_count", "menu_items_available"]
target = "revenue"

# Drop rows with missing features (for now — we'll handle this properly in Ch5)
model_df = df[feature_cols + [target]].dropna()
print(f"After dropping NaN: {len(model_df)} rows")

X = model_df[feature_cols]
y = model_df[target]
```

### Train/Test Split

Here's where most beginners make their first mistake: they train on all the data and evaluate on the same data. That's like grading a test with the answer key open.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)} rows")
print(f"Test:  {len(X_test)} rows")
```

```
Train: 4984 rows
Test:  1246 rows
```

The model sees the training data. It never sees the test data until evaluation. This simulates "predicting the future" — the whole point.

---

## Fit the Model

```python
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions on test set
y_pred = model.predict(X_test)
```

Three lines. That's it. scikit-learn's API is always the same: `.fit(X, y)` then `.predict(X)`.

---

## How Bad Is It?

```python
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"MAE:  ${mae:.2f}")
print(f"RMSE: ${rmse:.2f}")
print(f"R²:   {r2:.4f}")
```

```
MAE:  $412.35
RMSE: $548.92
R²:   0.8567
```

Is that good? You have no idea. You need a **baseline** to compare against.

---

## The Baseline: How Dumb Can We Be?

The dumbest possible prediction: always guess the average revenue.

```python
# Baseline: predict the mean of training revenue for every row
baseline_pred = np.full_like(y_test, y_train.mean())

baseline_mae = mean_absolute_error(y_test, baseline_pred)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
baseline_r2 = r2_score(y_test, baseline_pred)

print(f"\n--- Baseline (always predict mean) ---")
print(f"MAE:  ${baseline_mae:.2f}")
print(f"RMSE: ${baseline_rmse:.2f}")
print(f"R²:   {baseline_r2:.4f}")
```

```
--- Baseline (always predict mean) ---
MAE:  $1,156.78
RMSE: $1,452.34
R²:   0.0000
```

| Metric | Baseline | Linear Regression | Improvement |
|---|---|---|---|
| MAE | $1,157 | $412 | 64% better |
| RMSE | $1,452 | $549 | 62% better |
| R² | 0.00 | 0.86 | — |

OK, so the model is significantly better than guessing. R² of 0.86 means it explains 86% of the variance. Not bad for a first attempt.

But is it good *enough*?

---

## What the Metrics Mean

- **MAE** (Mean Absolute Error): On average, predictions are off by $412. For a restaurant making $4,000/day, that's a 10% error.
- **RMSE** (Root Mean Squared Error): Penalizes big misses more. $549 means some predictions are way off.
- **R²**: 1.0 = perfect, 0.0 = no better than guessing the mean. 0.86 is decent but not production-ready.

### Look at the Worst Predictions

```python
results = pd.DataFrame({"actual": y_test, "predicted": y_pred})
results["error"] = results["actual"] - results["predicted"]
results["abs_error"] = results["error"].abs()

# Top 10 worst predictions
worst = results.nlargest(10, "abs_error")
print(worst[["actual", "predicted", "error"]].to_string())
```

```
      actual  predicted    error
3421  8934.5   6012.3    2922.2
1087  1245.8   3567.1   -2321.3
5502  9123.4   6890.1    2233.3
...
```

Some predictions are off by $2,000+. That's the difference between ordering 50 steaks and ordering 120. Chef Marco would not be happy.

---

## Inspect the Coefficients

```python
coef_df = pd.DataFrame({
    "feature": feature_cols,
    "coefficient": model.coef_
}).sort_values("coefficient", key=abs, ascending=False)

print(coef_df.to_string(index=False))
print(f"\nIntercept: ${model.intercept_:.2f}")
```

```
            feature  coefficient
             covers        22.45
      temperature_c        14.87
    marketing_spend         2.31
 menu_items_available       1.12
        staff_count         0.34

Intercept: $312.45
```

Translation: each additional cover adds ~$22 to revenue (average ticket). Each degree of temperature adds ~$15. Marketing spend has a 2.3× multiplier. Staff count barely matters (as we saw in EDA).

---

## The Problem

You show Priya the results. She squints.

> "R² of 0.86 is fine for a first pass. But you're using `covers` as a feature. We don't *know* tomorrow's covers — that's what we're trying to predict. You're leaking the answer into the features."

She's right. If you're predicting tomorrow's revenue, you can't use tomorrow's covers as input — you don't have that number yet. You'd need to predict covers first, which is circular.

This is called **data leakage**: using information that wouldn't be available at prediction time.

### Remove the Leak

```python
# Features we'd actually know the day before
valid_features = ["temperature_c", "marketing_spend", "staff_count", "menu_items_available"]

X_valid = model_df[valid_features]
y_valid = model_df[target]

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X_valid, y_valid, test_size=0.2, random_state=42
)

model2 = LinearRegression()
model2.fit(X_train2, y_train2)
y_pred2 = model2.predict(X_test2)

mae2 = mean_absolute_error(y_test2, y_pred2)
r2_2 = r2_score(y_test2, y_pred2)

print(f"\n--- Without covers (no leakage) ---")
print(f"MAE:  ${mae2:.2f}")
print(f"R²:   {r2_2:.4f}")
```

```
--- Without covers (no leakage) ---
MAE:  $987.65
R²:   0.4312
```

Ouch. R² dropped from 0.86 to 0.43. MAE more than doubled. Without `covers`, the model is barely better than guessing.

This is reality. The easy version was cheating.

---

## Save the Honest Model

```python
# Save predictions for comparison in future chapters
results_honest = pd.DataFrame({
    "actual": y_test2.values,
    "predicted": y_pred2,
})
results_honest.to_csv("data/ch03_predictions.csv", index=False)
print("Saved honest predictions for comparison.")
```

---

## Report to Priya

> **First model results:**
> - Linear regression with valid features (no leakage): R² = 0.43, MAE = $988
> - That's only 15% better than guessing the average
> - Temperature and marketing spend help, but not enough alone
> - We need better features (day of week, seasonality, holidays) and probably a better algorithm
>
> Next step: feature engineering + trying non-linear models.

Priya: "Good. You caught the leakage before I had to. Now make it actually useful — Chef Marco is asking for predictions by Friday."

---

## What You Learned

- **Always split train/test** before fitting — never evaluate on training data
- **Always compare to a baseline** — "is this good?" requires "compared to what?"
- **Data leakage** is the #1 beginner mistake: using future information as features
- **R²** tells you how much variance you explain; **MAE** tells you the average dollar error
- **Coefficients** in linear regression are interpretable — each one says "per unit increase in X, Y changes by this much"
- A model can look great (R² = 0.86) and be completely useless if the features aren't available at prediction time
- The honest model (R² = 0.43) is your real starting point. Everything from here is improvement.

---

[Next: Chapter 4 — "The Avocado Incident" →](chapter-04-overfitting.md)
