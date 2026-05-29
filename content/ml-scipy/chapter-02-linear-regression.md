# Chapter 2: Linear Regression

[← Setup & NumPy](./chapter-01-setup-numpy.md) | [Next: Classification →](./chapter-03-classification.md)

---

## Mathematical Intuition

Linear regression finds the best-fit line by minimizing squared residuals.

**Model:** `\hat{y} = \mathbf{X}\boldsymbol{\beta} + \epsilon`

**Cost function (MSE):**

`J(\boldsymbol{\beta}) = \frac{1}{n}\|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|^2`

**Closed-form (Normal Equation):**

`\boldsymbol{\beta} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}`

## From Scratch

```python
import numpy as np
from scipy import linalg

class LinearRegressionScratch:
    def fit(self, X, y):
        X_b = np.c_[np.ones(X.shape[0]), X]
        self.beta = linalg.solve(X_b.T @ X_b, X_b.T @ y)
        return self

    def predict(self, X):
        X_b = np.c_[np.ones(X.shape[0]), X]
        return X_b @ self.beta

np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X.ravel() + np.random.randn(100)

model = LinearRegressionScratch().fit(X, y)
print(f"Intercept: {model.beta[0]:.2f}, Slope: {model.beta[1]:.2f}")
```

## Gradient Descent

When `\mathbf{X}^T\mathbf{X}` is too large to invert:

`\boldsymbol{\beta}_{t+1} = \boldsymbol{\beta}_t - \alpha \nabla J(\boldsymbol{\beta}_t)`

```python
def gradient_descent(X, y, lr=0.01, epochs=1000):
    X_b = np.c_[np.ones(X.shape[0]), X]
    beta = np.zeros(X_b.shape[1])
    n = len(y)

    for _ in range(epochs):
        gradient = -2/n * X_b.T @ (y - X_b @ beta)
        beta -= lr * gradient

    return beta

beta = gradient_descent(X, y)
print(f"Intercept: {beta[0]:.2f}, Slope: {beta[1]:.2f}")
```

## Regularization

**Ridge (L2):** `J_{ridge} = \|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|^2 + \lambda\|\boldsymbol{\beta}\|^2`

**Lasso (L1):** `J_{lasso} = \|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|^2 + \lambda\|\boldsymbol{\beta}\|_1`

## Scikit-Learn

```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing

data = fetch_california_housing()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

models = {
    'OLS': LinearRegression(),
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=0.1),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    print(f"{name:6s} — RMSE: {rmse:.4f}, R²: {r2:.4f}")
```

---

[← Setup & NumPy](./chapter-01-setup-numpy.md) | [Next: Classification →](./chapter-03-classification.md)
