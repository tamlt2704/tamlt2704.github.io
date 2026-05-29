# Chapter 1: Setup & NumPy Basics

[← Overview](./chapter-00-overview.md) | [Next: Linear Regression →](./chapter-02-linear-regression.md)

---

## Environment Setup

```bash
python -m venv ml-env
ml-env\Scripts\activate  # Windows
pip install numpy scipy scikit-learn matplotlib pandas jupyter
```

## NumPy Fundamentals

### Arrays and Operations

```python
import numpy as np

# Vectors and matrices
x = np.array([1, 2, 3, 4, 5])
A = np.array([[1, 2], [3, 4], [5, 6]])

print(A.shape)        # (3, 2)
print(A.T.shape)      # (2, 3)

# Element-wise operations
y = x * 2 + 1        # Broadcasting: [3, 5, 7, 9, 11]
```

### Linear Algebra Essentials

The dot product measures similarity between vectors:

`\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i = \|\mathbf{a}\| \|\mathbf{b}\| \cos\theta`

```python
from scipy import linalg

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
dot = np.dot(a, b)  # 32

# Matrix multiplication
A = np.random.randn(3, 4)
B = np.random.randn(4, 2)
C = A @ B  # (3, 2)

# Solving linear systems: Ax = b
A = np.array([[2, 1], [1, 3]])
b = np.array([5, 7])
x = linalg.solve(A, b)  # [1.6, 1.8]
```

### Statistical Operations

```python
data = np.random.randn(1000)

mean = np.mean(data)
std = np.std(data)
percentile_95 = np.percentile(data, 95)

# Covariance matrix
X = np.random.randn(100, 3)
cov_matrix = np.cov(X.T)  # (3, 3)
```

### Broadcasting Rules

```python
# Dimensions are compatible when equal or one is 1
matrix = np.random.randn(5, 3)
row_means = matrix.mean(axis=0)   # (3,)
centered = matrix - row_means     # (5,3) - broadcasts (3,) to (5,3)
```

## SciPy for Scientific Computing

```python
from scipy import stats, optimize

# Probability distributions
normal = stats.norm(loc=0, scale=1)
print(normal.pdf(0))    # 0.3989...
print(normal.cdf(1.96)) # 0.975

# Optimization
result = optimize.minimize(lambda x: (x - 3)**2 + 1, x0=0)
print(result.x)  # [3.0]
```

## Exercise: Data Exploration

```python
from sklearn.datasets import load_iris
import pandas as pd

iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['target'] = iris.target

print(df.describe())
print(f"Correlation matrix:\n{df.corr()}")
```

---

[← Overview](./chapter-00-overview.md) | [Next: Linear Regression →](./chapter-02-linear-regression.md)
