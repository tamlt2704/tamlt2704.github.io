---
title: "Chapter 1: Tensors & Autograd"
description: "PyTorch fundamentals - tensors and automatic differentiation"
---

# Chapter 1: Tensors & Autograd

## Creating Tensors

```python
import torch

# From data
t = torch.tensor([1, 2, 3, 4])
t2d = torch.tensor([[1, 2], [3, 4]])

# Common constructors
zeros = torch.zeros(3, 4)
ones = torch.ones(2, 3)
rand = torch.randn(3, 3)  # normal distribution

print(t.shape, t.dtype, t.device)
```

## Operations

```python
a = torch.randn(3, 3)
b = torch.randn(3, 3)

# Element-wise
c = a + b
d = a * b

# Matrix multiplication
e = a @ b  # or torch.matmul(a, b)

# Reshaping
x = torch.arange(12)
y = x.reshape(3, 4)
z = y.T  # transpose
```

## GPU Support

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
t = torch.randn(1000, 1000, device=device)
print(t.device)
```

## Autograd

```python
x = torch.tensor(3.0, requires_grad=True)
y = x**2 + 2*x + 1  # y = (x+1)^2

y.backward()
print(x.grad)  # dy/dx = 2x + 2 = 8.0
```

## Gradient in Practice

```python
# Simple linear regression with autograd
x = torch.linspace(0, 1, 100)
y_true = 3 * x + 1 + torch.randn(100) * 0.1

w = torch.tensor(0.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
lr = 0.1

for epoch in range(100):
    y_pred = w * x + b
    loss = ((y_pred - y_true)**2).mean()

    loss.backward()
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_()
    b.grad.zero_()

print(f"w={w.item():.2f}, b={b.item():.2f}")  # ~3.0, ~1.0
```

## Exercises

1. Create a 5x5 identity tensor and verify matrix multiplication with a random tensor.
2. Compute the gradient of `f(x) = sin(x) * exp(-x)` at x=1.
3. Implement gradient descent to find the minimum of `f(x) = (x-3)^2 + 2`.

---

[← prev](./chapter-00-overview.md) | [next →](./chapter-02-nn.md)
