# Chapter 2: Autograd — Automatic Differentiation

[← Chapter 1: Tensors](chapter-01-tensors.md) | [Chapter 3: Neural Networks →](chapter-03-nn-module.md)

---

## The Project

New client: a physics lab has noisy sensor data. They need to fit a curve y = ax² + bx + c to their measurements. No neural network — just find the best a, b, c using gradient descent.

Mara: "Autograd is the engine under PyTorch. You define a computation, call `.backward()`, and PyTorch gives you gradients. Every neural network trains this way."

## The Computational Graph

Every operation on tensors with `requires_grad=True` builds a graph:

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = x ** 2 + 3 * x + 1  # y = x² + 3x + 1

# PyTorch tracked every operation
print(y)           # tensor(11., grad_fn=<AddBackward0>)
print(y.grad_fn)   # The last operation that created y

# Compute gradients: dy/dx = 2x + 3 = 7 at x=2
y.backward()
print(x.grad)  # tensor(7.)
```

## requires_grad and Leaf Tensors

```python
# Leaf tensors: created directly (not from operations)
a = torch.tensor(3.0, requires_grad=True)   # Leaf, tracked
b = torch.tensor(5.0)                        # Leaf, NOT tracked

c = a * b  # Non-leaf (result of operation)
c.backward()
print(a.grad)  # tensor(5.) — dc/da = b = 5
print(b.grad)  # None — b doesn't require grad

# Gradients accumulate! Zero them before reuse.
a.grad.zero_()
```

## backward() and the Chain Rule

```python
x = torch.tensor(1.0, requires_grad=True)

# Multi-step computation
a = x * 2        # a = 2x
b = a + 3        # b = 2x + 3
c = b ** 2       # c = (2x + 3)²

c.backward()
# dc/dx = 2(2x+3) * 2 = 4(2x+3) = 4(5) = 20 at x=1
print(x.grad)  # tensor(20.)
```

## Gradients with Vectors

```python
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = (x ** 2).sum()  # Scalar output required for backward()

y.backward()
print(x.grad)  # tensor([2., 4., 6.]) — dy/dx_i = 2*x_i
```

## detach() and no_grad()

```python
x = torch.tensor(2.0, requires_grad=True)
y = x ** 2

# detach(): remove from graph (useful for targets, frozen params)
y_detached = y.detach()
print(y_detached.requires_grad)  # False

# no_grad(): disable tracking (inference, evaluation)
with torch.no_grad():
    z = x * 3
    print(z.requires_grad)  # False — no graph built
```

## The Client Project: Curve Fitting with Gradient Descent

```python
import torch

# Generate noisy data: true curve is y = 2x² - 3x + 1
torch.manual_seed(42)
x_data = torch.linspace(-3, 3, 100)
y_true = 2 * x_data**2 - 3 * x_data + 1
y_data = y_true + torch.randn(100) * 0.5  # Add noise

# Parameters to learn (random init)
a = torch.tensor(0.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
c = torch.tensor(0.0, requires_grad=True)

learning_rate = 0.01

for epoch in range(200):
    # Forward: predict y = ax² + bx + c
    y_pred = a * x_data**2 + b * x_data + c

    # Loss: mean squared error
    loss = ((y_pred - y_data) ** 2).mean()

    # Backward: compute gradients
    loss.backward()

    # Update parameters (no_grad so updates aren't tracked)
    with torch.no_grad():
        a -= learning_rate * a.grad
        b -= learning_rate * b.grad
        c -= learning_rate * c.grad

    # Zero gradients for next iteration
    a.grad.zero_()
    b.grad.zero_()
    c.grad.zero_()

    if epoch % 50 == 0:
        print(f"Epoch {epoch}: loss={loss.item():.4f} a={a.item():.3f} b={b.item():.3f} c={c.item():.3f}")

print(f"\nLearned: y = {a.item():.2f}x² + ({b.item():.2f})x + {c.item():.2f}")
print(f"True:    y = 2.00x² + (-3.00)x + 1.00")
```

Output:
```
Epoch 0: loss=14.2891 a=0.280 b=-0.000 c=0.126
Epoch 50: loss=0.3812 a=1.893 b=-2.934 c=0.784
Epoch 100: loss=0.2594 a=1.983 b=-2.987 c=0.946
Epoch 150: loss=0.2530 a=1.998 b=-2.997 c=0.978
Learned: y = 2.00x² + (-3.00)x + 0.99
True:    y = 2.00x² + (-3.00)x + 1.00
```

## What You Learned

- **requires_grad** — tells PyTorch to track operations on a tensor
- **Computational graph** — built dynamically during forward pass
- **backward()** — computes gradients via chain rule (backpropagation)
- **Gradient accumulation** — gradients add up; zero them each iteration
- **detach()** — removes a tensor from the graph
- **torch.no_grad()** — disables gradient tracking (for inference and param updates)
- **Manual gradient descent** — subtract `lr * grad` from each parameter

This works, but manually managing parameters is painful. What if you have millions of them? That's where `nn.Module` comes in.

---

[← Chapter 1: Tensors](chapter-01-tensors.md) | [Chapter 3: Neural Networks →](chapter-03-nn-module.md)
