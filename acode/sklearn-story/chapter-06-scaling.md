# Chapter 6: Features on Different Scales Break Everything

[← Chapter 5: Categorical Columns](chapter-05-encoding.md) | [Chapter 7: Linear Regression Isn't Enough →](chapter-07-trees.md)

---

## The Disaster

You're experimenting with different models. You try KNN (K-Nearest Neighbors) — it predicts based on similar historical days. Makes intuitive sense for restaurants.

```python
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_score

# Quick test without scaling
pipeline_knn = Pipeline(steps=[
    ("preprocessor", preprocessor_v2),  # from Chapter 5
    ("model", KNeighborsRegressor(n_neighbors=5)),
])

cv_scores = cross_val_score(pipeline_knn, X_v2, y_v2, cv=5, scoring="r2")
print(f"KNN R²: {cv_scores.mean():.4f}")
```

```
KNN R²: 0.5123
```

Worse than Ridge (0.75). But wait — you already have `StandardScaler` in the numeric transformer from Chapter 5. What if you remove it?

```python
# Without scaling
numeric_no_scale = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    # No scaler!
])

preprocessor_no_scale = ColumnTransformer(transformers=[
    ("num", numeric_no_scale, numeric_features_v2),
    ("cat", categorical_transformer, categorical_features_v2),
])

pipeline_knn_no_scale = Pipeline(steps=[
    ("preprocessor", preprocessor_no_scale),
    ("model", KNeighborsRegressor(n_neighbors=5)),
])

cv_no_scale = cross_val_score(pipeline_knn_no_scale, X_v2, y_v2, cv=5, scoring="r2")
print(f"KNN without scaling: R² = {cv_no_scale.mean():.4f}")
```

```
KNN without scaling: R² = 0.3456
```

Even worse. Scaling matters — but why?

---

## Why Scale Matters

```python
# chapter_06.py
"""Chapter 6: Feature scaling — when it matters and when it doesn't."""
import pandas as pd
import numpy as np

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])

# Look at the raw feature ranges
print(df[["temperature_c", "marketing_spend", "staff_count", "menu_items_available"]].describe())
```

```
       temperature_c  marketing_spend  staff_count  menu_items_available
mean           12.34           100.12         7.45                 34.56
std             8.67            49.78         2.31                  5.78
min           -12.30             0.00         4.00                 25.00
max            35.80           287.45        11.00                 44.00
```

- `temperature_c`: ranges from -12 to 36 (range: 48)
- `marketing_spend`: ranges from 0 to 287 (range: 287)
- `staff_count`: ranges from 4 to 11 (range: 7)

KNN measures "distance" between data points. A difference of 100 in marketing_spend dominates a difference of 5 in temperature — even if temperature is more predictive. The model thinks marketing_spend is 6× more important just because its numbers are bigger.

---

## The Two Main Scalers

### StandardScaler (Z-score normalization)

Transforms each feature to mean=0, std=1.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
# Formula: z = (x - mean) / std

# Example:
# temperature 25°C → (25 - 12.34) / 8.67 = 1.46 standard deviations above mean
# marketing $200  → (200 - 100.12) / 49.78 = 2.01 standard deviations above mean
```

**Use when:** The algorithm uses distances (KNN, SVM) or gradients (neural networks, logistic regression). Also helps regularized models (Ridge, Lasso) penalize coefficients fairly.

### MinMaxScaler (0-1 normalization)

Transforms each feature to the range [0, 1].

```python
from sklearn.preprocessing import MinMaxScaler

minmax = MinMaxScaler()
# Formula: x_scaled = (x - min) / (max - min)

# Example:
# temperature 25°C → (25 - (-12.3)) / (35.8 - (-12.3)) = 0.776
# marketing $200  → (200 - 0) / (287.45 - 0) = 0.696
```

**Use when:** You want bounded values (e.g., for neural networks with sigmoid activations) or when you know the data has no extreme outliers.

---

## When Scaling Doesn't Matter

Tree-based models (Decision Trees, Random Forest, Gradient Boosting) don't care about scale. They split on thresholds: "is temperature > 20?" The actual magnitude doesn't affect the split.

```python
from sklearn.ensemble import RandomForestRegressor

# Random Forest — no scaling needed
pipeline_rf_no_scale = Pipeline(steps=[
    ("preprocessor", preprocessor_no_scale),  # no scaler
    ("model", RandomForestRegressor(n_estimators=100, random_state=42)),
])

pipeline_rf_scaled = Pipeline(steps=[
    ("preprocessor", preprocessor_v2),  # with scaler
    ("model", RandomForestRegressor(n_estimators=100, random_state=42)),
])

cv_rf_no_scale = cross_val_score(pipeline_rf_no_scale, X_v2, y_v2, cv=5, scoring="r2")
cv_rf_scaled = cross_val_score(pipeline_rf_scaled, X_v2, y_v2, cv=5, scoring="r2")

print(f"Random Forest (no scaling): R² = {cv_rf_no_scale.mean():.4f}")
print(f"Random Forest (with scaling): R² = {cv_rf_scaled.mean():.4f}")
```

```
Random Forest (no scaling): R² = 0.8234
Random Forest (with scaling): R² = 0.8231
```

Identical. Trees don't care. But notice — Random Forest just beat everything else. We'll explore that in Chapter 7.

---

## The Cheat Sheet

| Algorithm | Needs Scaling? | Why |
|---|---|---|
| Linear Regression | No* | Coefficients adjust to scale |
| Ridge / Lasso | **Yes** | Regularization penalizes large coefficients — unfair if scales differ |
| KNN | **Yes** | Distance-based — large-scale features dominate |
| SVM | **Yes** | Distance-based + kernel computations |
| Decision Tree | No | Splits on thresholds, scale-invariant |
| Random Forest | No | Ensemble of trees |
| Gradient Boosting | No | Ensemble of trees |
| Neural Networks | **Yes** | Gradient descent converges faster with normalized inputs |

*Linear regression technically doesn't need scaling for predictions, but scaling makes coefficients comparable and helps with numerical stability.

---

## The Right Pipeline (Updated)

```python
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge

# For distance-based models: scale
pipeline_knn_proper = Pipeline(steps=[
    ("preprocessor", preprocessor_v2),  # includes StandardScaler
    ("model", KNeighborsRegressor(n_neighbors=10)),
])

cv_knn_proper = cross_val_score(pipeline_knn_proper, X_v2, y_v2, cv=5, scoring="r2")
print(f"KNN (properly scaled, k=10): R² = {cv_knn_proper.mean():.4f}")
```

```
KNN (properly scaled, k=10): R² = 0.6234
```

Better than unscaled (0.35 → 0.62), but still behind Ridge (0.75) and Random Forest (0.82). KNN struggles with high-dimensional one-hot encoded data — the "curse of dimensionality."

---

## Scaling Pitfall: Don't Fit on Test Data

```python
# ❌ WRONG: fitting scaler on all data
scaler.fit(X_all)  # sees test data statistics
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ✓ RIGHT: fit only on training data
scaler.fit(X_train)  # only sees training statistics
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)  # uses training mean/std

# ✓ BEST: use a Pipeline (handles this automatically)
pipeline.fit(X_train, y_train)  # scaler sees only X_train
pipeline.predict(X_test)         # scaler transforms X_test with training stats
```

This is why pipelines exist. They make it impossible to accidentally leak test data into preprocessing.

---

## Report to Priya

> **Scaling investigation complete:**
> - KNN without scaling: R² = 0.35 (marketing_spend dominated distance calculations)
> - KNN with StandardScaler: R² = 0.62 (fair distance computation)
> - Ridge with scaling: R² = 0.75 (regularization works fairly)
> - Random Forest (no scaling needed): R² = 0.82 ← **new best**
>
> **Recommendation:** Switch to Random Forest. It handles mixed scales naturally and outperforms everything we've tried.

Priya: "Do it. But I want to understand *why* it's better. Show me what it's doing differently."

---

## What You Learned

- **Feature scaling** makes all features contribute equally to distance/gradient calculations
- **StandardScaler**: mean=0, std=1 — best general-purpose choice
- **MinMaxScaler**: range [0,1] — use when you need bounded values
- **Tree-based models don't need scaling** — they split on thresholds, not distances
- **Distance-based models (KNN, SVM) always need scaling** — or large-scale features dominate
- **Regularized models (Ridge, Lasso) need scaling** — or penalties are unfair
- **Never fit the scaler on test data** — use Pipeline to prevent this automatically
- Random Forest just quietly outperformed everything. Trees are powerful. Chapter 7 explains why.

---

[Next: Chapter 7 — "Linear Regression Isn't Enough" →](chapter-07-trees.md)
