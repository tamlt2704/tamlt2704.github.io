# Chapter 9 — Loss & Optimizer

[← Chapter 8: Full Model Assembly](chapter-08-inference.md) | [Next → Chapter 10: Training Loop](chapter-10-quantize.md)

---

## Goal

Learn CrossEntropyLoss, Adam optimizer, and autograd, then run one training step on our model.

---

## PyTorch Concept: CrossEntropyLoss + Adam + Autograd

### Loss Function

CrossEntropyLoss measures how wrong our predictions are. Lower = better.

```python
import torch
import torch.nn as nn

loss_fn = nn.CrossEntropyLoss()

# Model predicts 3 classes, batch of 2
predictions = torch.tensor([[2.0, 1.0, 0.1], [0.5, 2.5, 0.3]])
targets = torch.tensor([0, 1])  # correct classes

loss = loss_fn(predictions, targets)
print(f"Loss: {loss.item():.4f}")  # ~0.42
```

### Optimizer

Adam adjusts model weights to reduce loss. It adapts learning rates per-parameter.

```python
model = nn.Linear(4, 2)
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
```

### Autograd (.backward)

PyTorch tracks operations on tensors. Calling `.backward()` computes gradients automatically.

```python
x = torch.randn(1, 4)
out = model(x)
loss = out.sum()
loss.backward()        # compute gradients
optimizer.step()       # update weights using gradients
optimizer.zero_grad()  # reset for next step
```

---

## Applying It: One Training Step on EmacsGPT

```python
# src/train_step.py
import torch
import torch.nn as nn
from model.gpt import EmacsGPT

model = EmacsGPT()
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
loss_fn = nn.CrossEntropyLoss()

# Fake batch: predict next token from previous tokens
input_ids = torch.randint(0, 8192, (4, 128))   # batch=4, seq=128
target_ids = torch.randint(0, 8192, (4, 128))  # what comes next

# Forward pass
logits = model(input_ids)  # (4, 128, 8192)

# Reshape for loss: (batch*seq, vocab) vs (batch*seq,)
loss = loss_fn(logits.view(-1, 8192), target_ids.view(-1))

# Backward pass
loss.backward()
optimizer.step()
optimizer.zero_grad()

print(f"Loss: {loss.item():.4f}")  # ~9.0 (random, untrained)
```

---

## Why Is the Loss ~9.0?

With vocab_size=8192, random guessing gives loss = ln(8192) ≈ 9.01. After training, we expect this to drop to ~3-4 for coherent text.

---

## What You Learned

- **PyTorch concept**: `CrossEntropyLoss` scores predictions, `Adam` updates weights, `.backward()` computes gradients
- **Build step**: One complete forward → loss → backward → update cycle on EmacsGPT
- Starting loss ≈ 9.0 (random); goal is ~3-4 after training

---

[← Chapter 8: Full Model Assembly](chapter-08-inference.md) | [Next → Chapter 10: Training Loop](chapter-10-quantize.md)
