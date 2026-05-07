# Chapter 5: Categorical Columns Crash `.fit()`

[← Chapter 4: The Avocado Incident](chapter-04-overfitting.md) | [Chapter 6: Features on Different Scales →](chapter-06-scaling.md)

---

## The Task

Priya's morning message:

> "Day of week matters. Holidays matter. Restaurant identity matters. Add them. I want R² above 0.7 by Wednesday."

You know from the EDA that Friday revenue is nearly double Monday's. That information is sitting in the `day_of_week` column. You just need to feed it to the model.

```python
X = df[["temperature_c", "marketing_spend", "day_of_week"]]
model.fit(X, y)
```

```
ValueError: could not convert string to float: 'Monday'
```

scikit-learn doesn't speak English. It speaks numbers. You need to translate.

---

## The Wrong Way: Label Encoding

```python
# chapter_05.py
"""Chapter 5: Encoding categoricals, ColumnTransformer, Pipelines."""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["day_encoded"] = le.fit_transform(df["day_of_week"])
print(df[["day_of_week", "day_encoded"]].drop_duplicates().sort_values("day_encoded"))
```

```
  day_of_week  day_encoded
       Friday            0
       Monday            1
     Saturday            2
       Sunday            3
     Thursday            4
      Tuesday            5
    Wednesday            6
```

This assigns arbitrary numbers. The model now thinks Wednesday (6) is "more" than Friday (0), and Saturday (2) is "between" Monday and Sunday. That's nonsense. Days of the week have no natural order.

Label encoding works for **ordinal** categories (small < medium < large). For **nominal** categories (days, colors, restaurant IDs), it introduces fake relationships.

---

## The Right Way: One-Hot Encoding

```python
from sklearn.preprocessing import OneHotEncoder

# One-hot: each category becomes its own binary column
ohe = OneHotEncoder(sparse_output=False, drop="first")  # drop="first" avoids multicollinearity
days_encoded = ohe.fit_transform(df[["day_of_week"]])

print(f"Shape: {days_encoded.shape}")  # (n_rows, 6) — 7 days minus 1 dropped
print(f"Columns: {ohe.get_feature_names_out()}")
```

```
Shape: (6588, 6)
Columns: ['day_of_week_Monday' 'day_of_week_Saturday' 'day_of_week_Sunday'
           'day_of_week_Thursday' 'day_of_week_Tuesday' 'day_of_week_Wednesday']
```

Now "Friday" is represented as all zeros (the dropped reference category). "Saturday" is `[0, 1, 0, 0, 0, 0]`. The model can learn that Saturday adds $X to revenue independently of other days.

---

## The Real Way: ColumnTransformer + Pipeline

In practice, you have a mix of numeric and categorical columns. You need different preprocessing for each. scikit-learn's `ColumnTransformer` handles this cleanly.

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.impute import SimpleImputer

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])

# Define column groups
numeric_features = ["temperature_c", "marketing_spend", "staff_count", "menu_items_available"]
categorical_features = ["day_of_week", "restaurant_id"]
target = "revenue"

X = df[numeric_features + categorical_features]
y = df[target]
```

### Build the Pipeline

```python
# Numeric: impute missing → scale
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

# Categorical: impute missing → one-hot encode
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
])

# Combine
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])

# Full pipeline: preprocess → model
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", Ridge(alpha=1.0)),
])
```

This is the scikit-learn way. One object that handles everything: missing values, encoding, scaling, and modeling. No manual steps. No data leakage between folds.

### Evaluate

```python
cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
print(f"CV R² scores: {cv_scores.round(4)}")
print(f"Mean R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
```

```
CV R² scores: [0.7234  0.7189  0.7312  0.7156  0.7278]
Mean R²: 0.7234 ± 0.0056
```

From 0.43 to 0.72 — just by adding day of week and restaurant identity. The model now knows that Fridays are busy and greenleaf_003 is a high-volume location.

---

## Add More Features: Month and Holiday

```python
# Engineer time features
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

# Update feature lists
numeric_features_v2 = ["temperature_c", "marketing_spend", "staff_count",
                       "menu_items_available", "month", "is_weekend"]
categorical_features_v2 = ["day_of_week", "restaurant_id"]

X_v2 = df[numeric_features_v2 + categorical_features_v2]
y_v2 = df[target]

# Rebuild pipeline with updated features
preprocessor_v2 = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features_v2),
    ("cat", categorical_transformer, categorical_features_v2),
])

pipeline_v2 = Pipeline(steps=[
    ("preprocessor", preprocessor_v2),
    ("model", Ridge(alpha=1.0)),
])

cv_scores_v2 = cross_val_score(pipeline_v2, X_v2, y_v2, cv=5, scoring="r2")
print(f"With month + weekend: R² = {cv_scores_v2.mean():.4f} ± {cv_scores_v2.std():.4f}")
```

```
With month + weekend: R² = 0.7456 ± 0.0048
```

Another bump. Month captures seasonality. `is_weekend` is redundant with `day_of_week` but doesn't hurt.

---

## Why Pipelines Matter

Without a pipeline, you'd do this:

```python
# ❌ The manual way (error-prone)
X_train_encoded = encoder.fit_transform(X_train)   # fit on train
X_test_encoded = encoder.transform(X_test)          # transform test (don't fit!)
X_train_scaled = scaler.fit_transform(X_train_encoded)
X_test_scaled = scaler.transform(X_test_encoded)
model.fit(X_train_scaled, y_train)
```

Common mistakes:
1. Fitting the encoder on the full dataset (data leakage)
2. Forgetting to transform the test set
3. Applying steps in the wrong order
4. Losing track of which columns go where

With a pipeline:

```python
# ✓ The pipeline way (correct by construction)
pipeline.fit(X_train, y_train)
pipeline.predict(X_test)
```

The pipeline guarantees that `.fit_transform()` only sees training data during cross-validation. No leakage. No mistakes.

---

## Handle Unknown Categories

What happens when a new restaurant appears in production that wasn't in training data?

```python
# handle_unknown="ignore" in OneHotEncoder means:
# - Unknown categories get all-zeros encoding
# - No crash, just treated as "none of the known categories"
# - This is safe for production
```

Without `handle_unknown="ignore"`, your model crashes the first time it sees a new restaurant. With it, the model gracefully falls back to the intercept for that category.

---

## Report to Priya

> **Categorical features added — R² target hit:**
> - Added day_of_week + restaurant_id via one-hot encoding: R² = 0.72
> - Added month + is_weekend: R² = 0.75
> - Using scikit-learn Pipeline + ColumnTransformer — no leakage risk
> - Missing values handled via SimpleImputer inside the pipeline
>
> **Improvement journey:**
> | Version | Features | CV R² |
> |---|---|---|
> | Ch3 | 4 numeric only | 0.43 |
> | Ch5 v1 | + day_of_week, restaurant_id | 0.72 |
> | Ch5 v2 | + month, is_weekend | 0.75 |

Priya: "0.75 is usable. But I bet a tree-based model does better. Try Random Forest after you handle the scaling question."

---

## What You Learned

- scikit-learn only accepts numbers — categorical columns must be encoded
- **Label encoding** is for ordinal categories (has natural order)
- **One-hot encoding** is for nominal categories (no order) — creates binary columns
- `drop="first"` avoids the dummy variable trap (multicollinearity)
- `handle_unknown="ignore"` prevents crashes on unseen categories in production
- **ColumnTransformer** applies different preprocessing to different column types
- **Pipeline** chains preprocessing + model into one object — prevents data leakage
- Feature engineering (month, is_weekend) is often more valuable than algorithm tuning
- Going from 4 numeric features to including categoricals jumped R² from 0.43 to 0.75

---

[Next: Chapter 6 — "Features on Different Scales" →](chapter-06-scaling.md)
