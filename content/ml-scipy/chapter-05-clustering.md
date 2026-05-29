# Chapter 5: Clustering

[← Trees & Ensembles](./chapter-04-trees-ensembles.md) | [Next: Model Evaluation & Projects →](./chapter-06-projects.md)

---

## K-Means

### Mathematical Intuition

Minimize within-cluster sum of squares:

`J = \sum_{k=1}^{K}\sum_{\mathbf{x}_i \in C_k} \|\mathbf{x}_i - \boldsymbol{\mu}_k\|^2`

**Algorithm:** Initialize centroids → assign points → recompute means → repeat.

### From Scratch

```python
import numpy as np
from scipy.spatial.distance import cdist

def kmeans(X, k, max_iter=100):
    centroids = X[np.random.choice(len(X), k, replace=False)]

    for _ in range(max_iter):
        labels = np.argmin(cdist(X, centroids), axis=1)
        new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids

    return labels, centroids

np.random.seed(42)
X = np.vstack([np.random.randn(50, 2) + [i*3, 0] for i in range(3)])
labels, centroids = kmeans(X, k=3)
```

## DBSCAN

Density-based clustering — finds arbitrary shapes without specifying k.

**Parameters:** `eps` (neighborhood radius), `min_samples` (density threshold)

**Point types:** Core (≥ min_samples in eps), Border (near core), Noise (neither)

## Scikit-Learn

```python
from sklearn.datasets import make_blobs, make_moons
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# K-Means
X_blobs, _ = make_blobs(n_samples=300, centers=4, random_state=42)
km = KMeans(n_clusters=4, random_state=42, n_init=10)
labels_km = km.fit_predict(X_blobs)
print(f"K-Means silhouette: {silhouette_score(X_blobs, labels_km):.4f}")

# DBSCAN on non-convex shapes
X_moons, _ = make_moons(n_samples=300, noise=0.05, random_state=42)
X_moons = StandardScaler().fit_transform(X_moons)
db = DBSCAN(eps=0.3, min_samples=5)
labels_db = db.fit_predict(X_moons)
n_clusters = len(set(labels_db)) - (1 if -1 in labels_db else 0)
print(f"DBSCAN: {n_clusters} clusters, {(labels_db==-1).sum()} noise points")
```

## Choosing k: Elbow Method

```python
inertias = []
for k in range(1, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_blobs)
    inertias.append(km.inertia_)
# Plot inertias vs k — optimal k is at the "elbow"
```

| Method  | Pros                            | Cons                               |
| ------- | ------------------------------- | ---------------------------------- |
| K-Means | Fast, scalable                  | Must specify k, spherical clusters |
| DBSCAN  | Arbitrary shapes, detects noise | Sensitive to eps                   |

---

[← Trees & Ensembles](./chapter-04-trees-ensembles.md) | [Next: Model Evaluation & Projects →](./chapter-06-projects.md)
