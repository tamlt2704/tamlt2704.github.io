# Chapter 4: The Avocado Incident

[← Chapter 3: Your First Model](chapter-03-first-model.md) | [Chapter 5: Categorical Columns Crash .fit() →](chapter-05-encoding.md)

---

## The Disaster

It's Friday. You've been tweaking the model all week. You added polynomial features, interaction terms, cranked up the complexity. Training R² hit 0.97. You're feeling good.

You deploy the predictions. Chef Marco at greenleaf_042 gets his forecast:

> "Tomorrow: 312 covers expected. Revenue: $8,400."

He orders accordingly. 200 avocados. 50kg of salmon. Extra staff.

Saturday comes. 87 covers walk in. Revenue: $2,100.

Chef Marco calls Priya. Priya calls you.

> "Your model told him to order for 300 people. Twelve showed up. He's got $3,000 of rotting avocados. What happened?"

You check the training metrics. R² = 0.97. Beautiful. You check the test metrics. R² = 0.31.

You've met **Overfitty** — your model memorized the training data instead of learning patterns.

---

## What Went Wrong

```python
# chapter_04.py
"""Chapter 4: Overfitting, cross-validation, and learning curves."""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
df = df.dropna(subset=["revenue"])

# Valid features (no leakage)
feature_cols = ["temperature_c", "marketing_spend", "staff_count", "menu_items_available"]
model_df = df[feature_cols + ["revenue"]].dropna()

X = model_df[feature_cols]
y = model_df["revenue"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

### Reproduce the Overfit

```python
# What you did: polynomial features degree 5 (way too complex)
poly = PolynomialFeatures(degree=5, include_bias=False)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

print(f"Original features: {X_train.shape[1]}")
print(f"Polynomial features (degree 5): {X_train_poly.shape[1]}")
```

```
Original features: 4
Polynomial features (degree 5): 125
```

4 features became 125. That's 125 coefficients the model can tune to perfectly fit the training data — including its noise.

```python
overfit_model = LinearRegression()
overfit_model.fit(X_train_poly, y_train)

train_r2 = r2_score(y_train, overfit_model.predict(X_train_poly))
test_r2 = r2_score(y_test, overfit_model.predict(X_test_poly))

print(f"Train R²: {train_r2:.4f}")
print(f"Test R²:  {test_r2:.4f}")
print(f"Gap:      {train_r2 - test_r2:.4f}")
```

```
Train R²: 0.9734
Test R²:  0.3102
Gap:      0.6632
```

A gap of 0.66 between train and test R². That's overfitting. The model learned the training noise, not the signal.

---

## The Fix: Cross-Validation

One train/test split can be misleading. Maybe you got lucky (or unlucky) with which rows ended up in the test set. **Cross-validation** splits the data multiple ways and averages the results.

```python
# 5-fold cross-validation on the simple model (no polynomial)
simple_model = LinearRegression()
cv_scores = cross_val_score(simple_model, X, y, cv=5, scoring="r2")

print(f"CV R² scores: {cv_scores.round(4)}")
print(f"Mean R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
```

```
CV R² scores: [0.4287  0.4356  0.4198  0.4412  0.4301]
Mean R²: 0.4311 ± 0.0071
```

Consistent across all 5 folds. The simple model genuinely explains ~43% of variance. No illusions.

Now the overfit model:

```python
from sklearn.pipeline import make_pipeline

overfit_pipeline = make_pipeline(PolynomialFeatures(degree=5), LinearRegression())
cv_scores_overfit = cross_val_score(overfit_pipeline, X, y, cv=5, scoring="r2")

print(f"Overfit CV R² scores: {cv_scores_overfit.round(4)}")
print(f"Mean R²: {cv_scores_overfit.mean():.4f} ± {cv_scores_overfit.std():.4f}")
```

```
Overfit CV R² scores: [0.2987  0.3145  0.2801  0.3234  0.2956]
Mean R²: 0.3025 ± 0.0152
```

Cross-validation exposes the truth: the complex model is *worse* than the simple one. It was only "better" on the specific training set it memorized.

---

## Visualize It: Learning Curves

Learning curves show how train and test scores change as you add more data. They're the best diagnostic for overfitting.

```python
def plot_learning_curve(estimator, X, y, title):
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=5,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring="r2", n_jobs=-1
    )

    train_mean = train_scores.mean(axis=1)
    test_mean = test_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    test_std = test_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="blue")
    ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color="orange")
    ax.plot(train_sizes, train_mean, "o-", color="blue", label="Training score")
    ax.plot(train_sizes, test_mean, "o-", color="orange", label="Cross-validation score")
    ax.set_xlabel("Training Set Size")
    ax.set_ylabel("R² Score")
    ax.set_title(title)
    ax.legend(loc="best")
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    return fig


# Simple model
fig1 = plot_learning_curve(LinearRegression(), X, y, "Learning Curve: Linear Regression")
fig1.savefig("plots/ch04_learning_curve_simple.png", dpi=150)

# Overfit model
fig2 = plot_learning_curve(
    make_pipeline(PolynomialFeatures(degree=5), LinearRegression()),
    X, y, "Learning Curve: Polynomial Degree 5"
)
fig2.savefig("plots/ch04_learning_curve_overfit.png", dpi=150)
plt.show()
```

**Simple model**: Training and validation curves converge. Both plateau around 0.43. This is **underfitting** — the model is too simple to capture the pattern, but at least it's honest.

**Polynomial degree 5**: Training score stays near 1.0. Validation score stays near 0.30. The gap never closes. This is **overfitting** — the model is too complex for the amount of signal in the data.

---

## The Sweet Spot: Regularization

What if we keep some complexity but penalize extreme coefficients? That's **regularization**.

```python
from sklearn.linear_model import Ridge, Lasso

# Try different polynomial degrees with Ridge regularization
results = []
for degree in [1, 2, 3, 4, 5]:
    pipeline = make_pipeline(
        PolynomialFeatures(degree=degree),
        Ridge(alpha=1.0)
    )
    scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
    results.append({
        "degree": degree,
        "mean_r2": scores.mean(),
        "std_r2": scores.std()
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
```

```
 degree  mean_r2  std_r2
      1   0.4311  0.0071
      2   0.4523  0.0089
      3   0.4498  0.0102
      4   0.4412  0.0134
      5   0.4356  0.0178
```

Degree 2 with Ridge gives the best cross-validated R² (0.4523) — a small improvement over the simple model, without overfitting. The gains are marginal because the real problem isn't model complexity — it's missing features (day of week, seasonality, holidays). We'll fix that in Chapter 5.

---

## The Rules of Overfitting

| Sign | What It Means |
|---|---|
| Train score >> Test score | Overfitting — model memorized noise |
| Train score ≈ Test score (both low) | Underfitting — model too simple |
| Train score ≈ Test score (both high) | Good fit — ship it |
| Adding features helps train but hurts test | Features are noise, not signal |
| More data helps test score | Model is data-hungry — get more rows |

---

## Report to Priya (and Chef Marco)

> **The avocado incident — post-mortem:**
> - Model was overfit: 125 polynomial features on 4 inputs
> - Training R² = 0.97 was an illusion — cross-validated R² = 0.30
> - Deployed predictions were based on memorized noise, not real patterns
>
> **Fix:**
> - Using cross-validation (5-fold) as the real metric going forward
> - Degree-2 polynomial with Ridge regularization: CV R² = 0.45
> - Still not good enough for production — need day-of-week and seasonal features
>
> **Rule going forward:** No model ships without cross-validation scores.

Chef Marco gets a gift basket and an apology. Priya adds "cross-validation" to the team's definition of done.

---

## What You Learned

- **Overfitting** = model memorizes training data, fails on new data
- **Underfitting** = model is too simple to capture the pattern
- **Cross-validation** gives honest performance estimates by testing on multiple splits
- **Learning curves** diagnose whether you need more data, more features, or less complexity
- **Regularization** (Ridge, Lasso) penalizes extreme coefficients, preventing overfitting
- **Never trust training metrics alone** — always report cross-validated scores
- The gap between train and test scores is more informative than either score alone

---

[Next: Chapter 5 — "Categorical Columns Crash .fit()" →](chapter-05-encoding.md)
