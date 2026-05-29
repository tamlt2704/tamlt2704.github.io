# Chapter 3: Classification

[← Linear Regression](./chapter-02-linear-regression.md) | [Next: Trees & Ensembles →](./chapter-04-trees-ensembles.md)

---

## Logistic Regression

### Mathematical Intuition

Maps linear output to probability via sigmoid:

`\sigma(z) = \frac{1}{1 + e^{-z}}, \quad z = \mathbf{x}^T\boldsymbol{\beta}`

**Loss (Binary Cross-Entropy):**

`J = -\frac{1}{n}\sum_{i=1}^{n}\left[y_i\log(\hat{p}_i) + (1-y_i)\log(1-\hat{p}_i)\right]`

### From Scratch

```python
import numpy as np
from scipy.special import expit  # sigmoid

class LogisticRegressionScratch:
    def fit(self, X, y, lr=0.1, epochs=1000):
        X_b = np.c_[np.ones(X.shape[0]), X]
        self.w = np.zeros(X_b.shape[1])
        for _ in range(epochs):
            p = expit(X_b @ self.w)
            gradient = X_b.T @ (p - y) / len(y)
            self.w -= lr * gradient
        return self

    def predict(self, X):
        X_b = np.c_[np.ones(X.shape[0]), X]
        return (expit(X_b @ self.w) >= 0.5).astype(int)
```

## Support Vector Machines (SVM)

Find the hyperplane maximizing margin between classes:

`\min_{\mathbf{w}, b} \frac{1}{2}\|\mathbf{w}\|^2 \quad \text{s.t.} \quad y_i(\mathbf{w}\cdot\mathbf{x}_i + b) \geq 1`

**Kernel trick** maps to higher dimensions:

- RBF: `K(\mathbf{x}, \mathbf{z}) = \exp(-\gamma\|\mathbf{x}-\mathbf{z}\|^2)`

## K-Nearest Neighbors (KNN)

Classify by majority vote of k closest points:

`d(\mathbf{x}, \mathbf{z}) = \sqrt{\sum_i (x_i - z_i)^2}`

No training phase — lazy learner, all computation at prediction time.

## Scikit-Learn Comparison

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

classifiers = {
    'Logistic': LogisticRegression(max_iter=5000),
    'SVM-RBF': SVC(kernel='rbf', C=1.0),
    'KNN-5':   KNeighborsClassifier(n_neighbors=5),
}

for name, clf in classifiers.items():
    clf.fit(X_train_s, y_train)
    acc = clf.score(X_test_s, y_test)
    print(f"{name:10s} — Accuracy: {acc:.4f}")

best = classifiers['Logistic']
print(classification_report(y_test, best.predict(X_test_s),
                            target_names=data.target_names))
```

## When to Use What

| Algorithm           | Strengths                     | Weaknesses                               |
| ------------------- | ----------------------------- | ---------------------------------------- |
| Logistic Regression | Interpretable, fast           | Linear boundary only                     |
| SVM                 | High dimensions, kernel trick | Slow on large data                       |
| KNN                 | Simple, no training           | Slow prediction, curse of dimensionality |

---

[← Linear Regression](./chapter-02-linear-regression.md) | [Next: Trees & Ensembles →](./chapter-04-trees-ensembles.md)
