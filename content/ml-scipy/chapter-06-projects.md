# Chapter 6: Model Evaluation & End-to-End Projects

[← Clustering](./chapter-05-clustering.md) | [Back to Overview →](./chapter-00-overview.md)

---

## Model Evaluation

### Cross-Validation

Never evaluate on training data. K-fold CV gives robust estimates:

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer()
clf = RandomForestClassifier(n_estimators=100, random_state=42)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(clf, data.data, data.target, cv=cv, scoring='accuracy')
print(f"Accuracy: {scores.mean():.4f} ± {scores.std():.4f}")
```

### Metrics

| Metric    | Formula                     | Use When                     |
| --------- | --------------------------- | ---------------------------- |
| Accuracy  | `(TP+TN)/N`                 | Balanced classes             |
| Precision | `TP/(TP+FP)`                | Cost of false positives high |
| Recall    | `TP/(TP+FN)`                | Cost of false negatives high |
| F1        | `2 \cdot P \cdot R / (P+R)` | Imbalanced classes           |
| AUC-ROC   | Area under ROC curve        | Ranking quality              |

## Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.svm import SVC
from scipy.stats import loguniform

# Grid search (exhaustive)
param_grid = {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']}
grid = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy')
grid.fit(data.data, data.target)
print(f"Best: {grid.best_params_}, Score: {grid.best_score_:.4f}")

# Randomized search (faster for large spaces)
param_dist = {'C': loguniform(0.01, 100), 'gamma': loguniform(1e-4, 1)}
rand = RandomizedSearchCV(SVC(kernel='rbf'), param_dist,
                          n_iter=50, cv=5, random_state=42)
rand.fit(data.data, data.target)
print(f"Best: {rand.best_params_}")
```

## End-to-End Project: House Price Prediction

```python
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 1. Load data
data = fetch_california_housing()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 2. Build pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', GradientBoostingRegressor(n_estimators=200, max_depth=5,
                                        learning_rate=0.1, random_state=42))
])

# 3. Cross-validate
cv_scores = cross_val_score(pipe, X_train, y_train, cv=5,
                            scoring='neg_root_mean_squared_error')
print(f"CV RMSE: {-cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# 4. Final evaluation
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
print(f"Test RMSE: {mean_squared_error(y_test, y_pred, squared=False):.4f}")
print(f"Test R²:   {r2_score(y_test, y_pred):.4f}")
```

## Project Checklist

1. **Explore** — distributions, correlations, missing values
2. **Preprocess** — scaling, encoding, feature engineering
3. **Baseline** — simple model to beat
4. **Iterate** — try multiple algorithms
5. **Tune** — hyperparameter search
6. **Evaluate** — hold-out test set, confidence intervals
7. **Deploy** — serialize with `joblib`, serve via API

---

[← Clustering](./chapter-05-clustering.md) | [Back to Overview →](./chapter-00-overview.md)
