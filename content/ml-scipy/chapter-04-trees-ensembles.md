# Chapter 4: Decision Trees & Random Forest

[← Classification](./chapter-03-classification.md) | [Next: Clustering →](./chapter-05-clustering.md)

---

## Decision Trees

### Mathematical Intuition

Trees split data by maximizing **information gain**.

**Gini Impurity:** `G = 1 - \sum_{k=1}^{K} p_k^2`

**Entropy:** `H = -\sum_{k=1}^{K} p_k \log_2(p_k)`

**Information Gain:** `IG = H(parent) - \sum \frac{n_{child}}{n_{parent}} H(child)`

### From Scratch (Split Logic)

```python
import numpy as np

def gini(y):
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    return 1 - np.sum(probs**2)

def best_split(X, y):
    best_gain, best_feat, best_thresh = -1, None, None
    parent_gini = gini(y)

    for feat in range(X.shape[1]):
        for t in np.unique(X[:, feat]):
            left = y[X[:, feat] <= t]
            right = y[X[:, feat] > t]
            if len(left) == 0 or len(right) == 0:
                continue
            weighted = (len(left)*gini(left) + len(right)*gini(right)) / len(y)
            gain = parent_gini - weighted
            if gain > best_gain:
                best_gain, best_feat, best_thresh = gain, feat, t

    return best_feat, best_thresh
```

## Random Forest

Single trees overfit. Random forests reduce variance via:

1. **Bagging** — each tree trains on a bootstrap sample
2. **Feature randomness** — each split uses a random feature subset

`\hat{y} = \text{mode}(T_1(\mathbf{x}), \ldots, T_B(\mathbf{x}))`

## Scikit-Learn

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import numpy as np

data = load_wine()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

models = {
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boost': GradientBoostingClassifier(n_estimators=100, random_state=42),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"{name:15s} — Accuracy: {acc:.4f}")

# Feature importance
rf = models['Random Forest']
top = np.argsort(rf.feature_importances_)[::-1][:5]
for i in top:
    print(f"  {data.feature_names[i]:30s}: {rf.feature_importances_[i]:.4f}")
```

## Hyperparameter Guide

| Parameter           | Effect               | Typical Range      |
| ------------------- | -------------------- | ------------------ |
| `max_depth`         | Tree complexity      | 3–20               |
| `n_estimators`      | Number of trees      | 100–1000           |
| `min_samples_split` | Min samples to split | 2–20               |
| `max_features`      | Features per split   | `'sqrt'`, `'log2'` |

---

[← Classification](./chapter-03-classification.md) | [Next: Clustering →](./chapter-05-clustering.md)
