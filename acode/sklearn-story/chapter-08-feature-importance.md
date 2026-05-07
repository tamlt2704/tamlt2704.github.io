# Chapter 8: Which Features Actually Matter?

[← Chapter 7: Linear Regression Isn't Enough](chapter-07-trees.md) | [Chapter 9: The Model Works — Until Next Month →](chapter-09-time-series.md)

---

## The Task

Chef Marco is skeptical:

> "Your computer says I should order 180 covers worth of food tomorrow. Why? What's it looking at? If it's using staff count to predict revenue, that's backwards — I schedule staff *based on* expected revenue."

Fair point. A model that uses the wrong signals will give right answers for wrong reasons — and break the moment something changes.

Priya agrees:

> "Show me feature importance. I want to know what's driving predictions and whether it makes business sense."

---

## Built-in Feature Importance (Tree-Based)

Random Forest and Gradient Boosting track how much each feature reduces prediction error across all splits. This is "impurity-based" importance.

```python
# chapter_08.py
"""Chapter 8: Feature importance, permutation importance, feature selection."""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

numeric_features = ["temperature_c", "marketing_spend", "staff_count",
                    "menu_items_available", "month", "is_weekend"]
categorical_features = ["day_of_week", "restaurant_id"]

X = df[numeric_features + categorical_features]
y = df["revenue"]

# Build and fit the pipeline
numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", GradientBoostingRegressor(n_estimators=300, max_depth=5, random_state=42)),
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)
```

### Extract Importance from the Model

```python
# Get feature names after preprocessing
feature_names = (numeric_features +
                 list(pipeline.named_steps["preprocessor"]
                      .transformers_[1][1]
                      .named_steps["onehot"]
                      .get_feature_names_out(categorical_features)))

importances = pipeline.named_steps["model"].feature_importances_

# Sort and display top 15
importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values("importance", ascending=False).head(15)

print(importance_df.to_string(index=False))
```

```
                    feature  importance
                      month      0.2345
            temperature_c       0.1987
              is_weekend        0.1456
        marketing_spend         0.1234
  day_of_week_Saturday          0.0876
    day_of_week_Friday          0.0765
  restaurant_id_greenleaf_003   0.0432
        staff_count             0.0234
  menu_items_available          0.0198
  ...
```

Top drivers: **month** (seasonality), **temperature** (weather), **is_weekend** (day type), **marketing_spend** (promotion). These make business sense.

`staff_count` is near the bottom — confirming Chef Marco's intuition that it's a response variable, not a driver.

---

## The Problem with Built-in Importance

Built-in importance has a bias: it favors high-cardinality features (features with many unique values). A continuous feature like `temperature_c` gets more splits than a binary feature like `is_weekend`, even if `is_weekend` is more predictive per-split.

Also, correlated features split importance between them. If `temperature_c` and `month` are correlated (they are — summer is warm), each gets half the credit.

---

## Permutation Importance: The Honest Version

Permutation importance asks: "If I randomly shuffle this feature's values, how much does the model's score drop?" If shuffling a feature destroys accuracy, it was important. If nothing changes, it wasn't.

```python
# Permutation importance on TEST set (not training!)
perm_result = permutation_importance(
    pipeline, X_test, y_test,
    n_repeats=10, random_state=42, scoring="r2"
)

perm_df = pd.DataFrame({
    "feature": numeric_features + categorical_features,
    "importance_mean": perm_result.importances_mean,
    "importance_std": perm_result.importances_std,
}).sort_values("importance_mean", ascending=False)

print(perm_df.to_string(index=False))
```

```
            feature  importance_mean  importance_std
       day_of_week           0.2134          0.0089
      restaurant_id          0.1567          0.0076
              month          0.1345          0.0065
      temperature_c          0.0987          0.0054
    marketing_spend          0.0756          0.0043
         is_weekend          0.0534          0.0038
        staff_count          0.0045          0.0012
 menu_items_available        0.0023          0.0009
```

Different story! `day_of_week` and `restaurant_id` are the most important — they capture which day it is and which restaurant's baseline we're predicting. `staff_count` and `menu_items_available` are nearly useless.

### Visualize It

```python
fig, ax = plt.subplots(figsize=(10, 6))
perm_df_sorted = perm_df.sort_values("importance_mean", ascending=True)
ax.barh(perm_df_sorted["feature"], perm_df_sorted["importance_mean"],
        xerr=perm_df_sorted["importance_std"], color="#4ec9b0")
ax.set_xlabel("Mean R² Decrease (Permutation Importance)")
ax.set_title("Feature Importance — What Actually Drives Predictions")
plt.tight_layout()
plt.savefig("plots/ch08_permutation_importance.png", dpi=150)
plt.show()
```

---

## Should We Drop Useless Features?

```python
# Try removing staff_count and menu_items_available
reduced_numeric = ["temperature_c", "marketing_spend", "month", "is_weekend"]

preprocessor_reduced = ColumnTransformer(transformers=[
    ("num", numeric_transformer, reduced_numeric),
    ("cat", categorical_transformer, categorical_features),
])

pipeline_reduced = Pipeline([
    ("preprocessor", preprocessor_reduced),
    ("model", GradientBoostingRegressor(n_estimators=300, max_depth=5, random_state=42)),
])

cv_full = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
cv_reduced = cross_val_score(pipeline_reduced,
                              df[reduced_numeric + categorical_features],
                              y, cv=5, scoring="r2")

print(f"Full features (8):    R² = {cv_full.mean():.4f}")
print(f"Reduced features (6): R² = {cv_reduced.mean():.4f}")
```

```
Full features (8):    R² = 0.8567
Reduced features (6): R² = 0.8545
```

Dropping two useless features barely changes accuracy. The model is simpler, faster, and easier to explain — with no cost.

---

## Partial Dependence: How Each Feature Affects Predictions

Feature importance tells you *what* matters. Partial dependence tells you *how* it matters.

```python
from sklearn.inspection import PartialDependenceDisplay

# Fit on full training data
pipeline.fit(X_train, y_train)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Temperature effect
PartialDependenceDisplay.from_estimator(
    pipeline, X_test, features=["temperature_c"],
    ax=axes[0], kind="average"
)
axes[0].set_title("Effect of Temperature on Revenue")

# Marketing spend effect
PartialDependenceDisplay.from_estimator(
    pipeline, X_test, features=["marketing_spend"],
    ax=axes[1], kind="average"
)
axes[1].set_title("Effect of Marketing Spend")

# Month effect
PartialDependenceDisplay.from_estimator(
    pipeline, X_test, features=["month"],
    ax=axes[2], kind="average"
)
axes[2].set_title("Effect of Month (Seasonality)")

plt.tight_layout()
plt.savefig("plots/ch08_partial_dependence.png", dpi=150)
plt.show()
```

What you see:
- **Temperature**: Revenue increases with temperature up to ~25°C, then plateaus. Non-linear — exactly what trees capture that linear models miss.
- **Marketing**: Roughly linear effect up to ~$200, then diminishing returns.
- **Month**: Clear seasonal curve — peaks in June-August, dips in December-February.

---

## Explaining It to Chef Marco

```python
# For a specific prediction, show feature contributions
# (using a simple approach — for production, use SHAP)

sample = X_test.iloc[[0]]
prediction = pipeline.predict(sample)[0]
actual = y_test.iloc[0]

print(f"Prediction: ${prediction:.2f}")
print(f"Actual:     ${actual:.2f}")
print(f"Sample features:")
print(sample.to_string())
```

> "Chef Marco, here's what the model sees for tomorrow:
> - It's a **Saturday** (weekends are 40% busier than weekdays)
> - Temperature forecast is **24°C** (warm days bring +$400 vs cold days)
> - You're spending **$150 on marketing** (adds ~$350 vs no marketing)
> - It's **June** (peak season, +$500 vs January)
> - Your restaurant's baseline is **$3,800/day**
>
> Combined prediction: **$5,450** (±$380 typical error)
>
> Staff count and menu size don't affect the prediction — they're not drivers."

Chef Marco: "OK, that makes sense. I'll order for 200 covers, not 300."

---

## Report to Priya

> **Feature importance analysis:**
>
> | Feature | Permutation Importance | Business Interpretation |
> |---|---|---|
> | day_of_week | 0.213 | Which day drives traffic patterns |
> | restaurant_id | 0.157 | Each location has a different baseline |
> | month | 0.135 | Seasonal demand cycle |
> | temperature_c | 0.099 | Weather drives walk-in traffic |
> | marketing_spend | 0.076 | Promotions have measurable ROI |
> | is_weekend | 0.053 | Weekend vs weekday split |
> | staff_count | 0.005 | **Not a driver — remove** |
> | menu_items_available | 0.002 | **Not a driver — remove** |
>
> **Recommendation:** Drop staff_count and menu_items_available. They add noise, not signal. The model is now explainable to restaurant owners.

Priya: "Perfect. Ship it. But first — what happens when next month's data looks different from training data?"

---

## What You Learned

- **Built-in feature importance** (tree-based) is fast but biased toward high-cardinality features
- **Permutation importance** is model-agnostic and honest — measures actual impact on test performance
- **Partial dependence plots** show the shape of each feature's effect (linear? threshold? curve?)
- **Dropping useless features** simplifies the model with no accuracy cost
- **Explainability matters** — stakeholders won't trust predictions they can't understand
- Always compute importance on the **test set**, not training set
- Correlated features split importance between them — be aware of this when interpreting

---

[Next: Chapter 9 — "The Model Works — Until Next Month" →](chapter-09-time-series.md)
