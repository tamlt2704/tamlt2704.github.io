---
title: "Chapter 2: Neural Networks"
description: "Building neural networks with torch.nn"
---

# Chapter 2: Neural Networks

## nn.Module Basics

```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

model = SimpleNet(10, 32, 2)
print(model)
```

## Training Loop

```python
from torch.utils.data import DataLoader, TensorDataset

# Synthetic data
X = torch.randn(1000, 10)
y = (X[:, 0] + X[:, 1] > 0).long()

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = SimpleNet(10, 32, 2)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(20):
    total_loss = 0
    for batch_x, batch_y in loader:
        optimizer.zero_grad()
        output = model(batch_x)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    if epoch % 5 == 0:
        print(f"Epoch {epoch}, Loss: {total_loss/len(loader):.4f}")
```

## Evaluation

```python
model.eval()
with torch.no_grad():
    preds = model(X).argmax(dim=1)
    accuracy = (preds == y).float().mean()
    print(f"Accuracy: {accuracy:.2%}")
```

## Sequential API

```python
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, 2)
)
```

## Exercises

1. Build a 3-layer network for regression (predict a continuous value). Use MSELoss.
2. Add dropout and batch normalization to the SimpleNet and compare training curves.
3. Implement early stopping: stop training when validation loss hasn't improved for 5 epochs.

---

[← prev](./chapter-01-tensors.md) | [next →](./chapter-03-cnn.md)
