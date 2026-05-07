# Chapter 7: Linear Regression Isn't Enough

[← Chapter 6: Features on Different Scales](chapter-06-scaling.md) | [Chapter 8: Which Features Actually Matter? →](chapter-08-feature-importance.md)

---

## The Task

Priya saw the Random Forest number (R² = 0.82) and wants to understand it:

> "Linear models assume a straight-line relationship. Revenue doesn't work that way — a 30°C day isn't just 'more' than 20°C, it's a different kind of busy. Show me what trees do differently, and find the best model."

---

## Why Linear Models Hit a Ceiling

```python
# chapter_07.py
"""Chapter 7: Decision Trees, Random Forests, model comparison."""
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

numeric_features = ["temperature_c", "marketing_spend", "staff_count",
                    "menu_items_available", "month", "is_weekend"]
categorical_features = ["day_of_week", "restaurant_id"]
target = "revenue"

X = df[numeric_features + categorical_features]
y = df[target]
```

Linear regression fits one equation: `revenue = a×temp + b×marketing + c×staff + ...`

This means:
- Every degree of temperature adds the same amount of revenue (whether going from 0→1 or 30→31)
- The effect of marketing is the same on Monday and Saturday
- There are no "if-then" rules

Real life isn't like that. A restaurant on a 32°C Saturday with a holiday nearby behaves completely differently than the sum of those individual effects.

---

## Decision Trees: If-Then Rules

A decision tree asks questions and splits the data:

```python
# Simple tree to visualize
from sklearn.model_selection import train_test_split

# Use only numeric features for visualization
X_simple = df[["temperature_c", "marketing_spend", "is_weekend"]].dropna()
y_simple = df.loc[X_simple.index, target]

X_train, X_test, y_train, y_test = train_test_split(X_simple, y_simple, test_size=0.2, random_state=42)

tree = DecisionTreeRegressor(max_depth=3, random_state=42)
tree.fit(X_train, y_train)

# Print the tree
print(export_text(tree, feature_names=["temperature_c", "marketing_spend", "is_weekend"]))
```

```
|--- is_weekend <= 0.50
|   |--- temperature_c <= 15.45
|   |   |--- marketing_spend <= 87.50
|   |   |   |--- value: [2834.12]
|   |   |--- marketing_spend >  87.50
|   |   |   |--- value: [3245.67]
|   |--- temperature_c >  15.45
|   |   |--- marketing_spend <= 120.30
|   |   |   |--- value: [3678.90]
|   |   |--- marketing_spend >  120.30
|   |   |   |--- value: [4123.45]
|--- is_weekend >  0.50
|   |--- temperature_c <= 18.90
|   |   |--- marketing_spend <= 95.00
|   |   |   |--- value: [4567.89]
|   |   |--- marketing_spend >  95.00
|   |   |   |--- value: [5234.56]
|   |--- temperature_c >  18.90
|   |   |--- marketing_spend <= 130.00
|   |   |   |--- value: [5890.12]
|   |   |--- marketing_spend >  130.00
|   |   |   |--- value: [6345.78]
```

The tree learned: "First check if it's a weekend. Then check temperature. Then check marketing." It captures **interactions** (weekend + warm + high marketing = very high revenue) that linear models miss.

---

## The Problem with One Tree

```python
# Single deep tree
deep_tree = DecisionTreeRegressor(random_state=42)  # no max_depth = grows until pure
deep_tree.fit(X_train, y_train)

print(f"Train R²: {deep_tree.score(X_train, y_train):.4f}")
print(f"Test R²:  {deep_tree.score(X_test, y_test):.4f}")
```

```
Train R²: 1.0000
Test R²:  0.6234
```

Overfitting again. A single tree with no constraints memorizes every training point. It creates a leaf for nearly every row.

---

## Random Forest: Wisdom of the Crowd

A Random Forest builds hundreds of trees, each on a random subset of data and features. Then it averages their predictions. Individual trees overfit — but their errors cancel out.

```python
# Full pipeline with Random Forest
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])

# Random Forest pipeline (no scaling needed)
pipeline_rf = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
])

cv_rf = cross_val_score(pipeline_rf, X, y, cv=5, scoring="r2")
print(f"Random Forest: R² = {cv_rf.mean():.4f} ± {cv_rf.std():.4f}")
```

```
Random Forest: R² = 0.8312 ± 0.0045
```

---

## Gradient Boosting: Trees That Learn from Mistakes

Gradient Boosting builds trees sequentially. Each new tree focuses on the errors of the previous ones. It's like a student who reviews their wrong answers after each test.

```python
pipeline_gb = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42
    )),
])

cv_gb = cross_val_score(pipeline_gb, X, y, cv=5, scoring="r2")
print(f"Gradient Boosting: R² = {cv_gb.mean():.4f} ± {cv_gb.std():.4f}")
```

```
Gradient Boosting: R² = 0.8567 ± 0.0038
```

New champion.

---

## Model Comparison

```python
# Compare all models we've tried
models = {
    "Ridge (linear)": Pipeline([("preprocessor", preprocessor), ("model", Ridge(alpha=1.0))]),
    "Decision Tree (depth=5)": Pipeline([("preprocessor", preprocessor),
                                          ("model", DecisionTreeRegressor(max_depth=5, random_state=42))]),
    "Random Forest (200 trees)": pipeline_rf,
    "Gradient Boosting": pipeline_gb,
}

results = {}
for name, pipeline in models.items():
    scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
    results[name] = {"mean": scores.mean(), "std": scores.std()}
    print(f"{name:30s} R² = {scores.mean():.4f} ± {scores.std():.4f}")
```

```
Ridge (linear)                 R² = 0.7456 ± 0.0048
Decision Tree (depth=5)        R² = 0.7123 ± 0.0134
Random Forest (200 trees)      R² = 0.8312 ± 0.0045
Gradient Boosting              R² = 0.8567 ± 0.0038
```

| Model | R² | MAE | Strengths |
|---|---|---|---|
| Ridge | 0.75 | ~$620 | Interpretable, fast, stable |
| Decision Tree | 0.71 | ~$680 | Interpretable, but unstable |
| Random Forest | 0.83 | ~$430 | Robust, handles interactions |
| Gradient Boosting | 0.86 | ~$380 | Best accuracy, captures complex patterns |

---

## Tune the Winner: GridSearchCV

```python
# Tune Gradient Boosting hyperparameters
param_grid = {
    "model__n_estimators": [100, 200, 300],
    "model__learning_rate": [0.05, 0.1, 0.2],
    "model__max_depth": [3, 5, 7],
}

grid_search = GridSearchCV(
    pipeline_gb, param_grid, cv=5, scoring="r2", n_jobs=-1, verbose=1
)
grid_search.fit(X, y)

print(f"\nBest params: {grid_search.best_params_}")
print(f"Best R²: {grid_search.best_score_:.4f}")
```

```
Best params: {'model__learning_rate': 0.1, 'model__max_depth': 5, 'model__n_estimators': 300}
Best R²: 0.8623
```

Marginal improvement. The defaults were already close to optimal. This is common — scikit-learn's defaults are sensible.

---

## Why Trees Win Here

1. **Non-linear relationships**: Revenue doesn't increase linearly with temperature. Trees capture "warm weekends are special" without being told.
2. **Automatic interactions**: Trees naturally find combinations (weekend × warm × holiday) that linear models need explicit feature engineering for.
3. **Robust to scale**: No scaling needed. No sensitivity to outliers in features.
4. **Handle mixed types well**: After one-hot encoding, trees treat binary columns naturally.

The tradeoff: trees are less interpretable than linear models. You can't point to a single coefficient and say "each degree adds $15." But you can measure feature importance — that's Chapter 8.

---

## Report to Priya

> **Model comparison complete:**
> - Gradient Boosting wins: R² = 0.86, MAE ≈ $380
> - That's a $380 average error on ~$4,000 daily revenue (9.5% error)
> - Compared to our Chapter 3 starting point (R² = 0.43, MAE ≈ $988): massive improvement
>
> **The journey:**
> | Chapter | Model | R² | Key Change |
> |---|---|---|---|
> | 3 | Linear (4 features) | 0.43 | Starting point |
> | 5 | Ridge + categoricals | 0.75 | Added day_of_week, restaurant_id |
> | 7 | Gradient Boosting | 0.86 | Non-linear model |
>
> Next: understanding which features drive the predictions.

Priya: "Good. Now tell me *why* the model predicts what it predicts. Chef Marco doesn't trust black boxes."

---

## What You Learned

- **Decision Trees** split data with if-then rules — capture non-linear relationships and interactions
- **Single trees overfit** — they memorize training data without constraints
- **Random Forest** = many trees on random subsets, averaged → reduces overfitting
- **Gradient Boosting** = sequential trees that correct each other's errors → best accuracy
- **GridSearchCV** searches hyperparameter combinations with cross-validation
- **Trees don't need scaling** — they split on thresholds, not distances
- The progression: linear (0.43) → linear + features (0.75) → trees (0.86) shows that both features and algorithms matter
- scikit-learn's API is consistent: every model has `.fit()` and `.predict()` — swapping models is trivial

---

[Next: Chapter 8 — "Which Features Actually Matter?" →](chapter-08-feature-importance.md)
