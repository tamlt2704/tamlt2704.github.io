---
title: "Chapter 6: Training Tips"
description: "Learning rate scheduling, mixed precision, and best practices"
---

# Chapter 6: Training Tips

## Learning Rate Scheduling

```python
import torch
import torch.nn as nn

model = nn.Linear(10, 2)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Step decay
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# Cosine annealing
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)

# ReduceLROnPlateau
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

# In training loop:
# scheduler.step()  # or scheduler.step(val_loss) for ReduceLROnPlateau
```

## Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

# for images, labels in train_loader:
#     optimizer.zero_grad()
#     with autocast():
#         output = model(images)
#         loss = criterion(output, labels)
#     scaler.scale(loss).backward()
#     scaler.step(optimizer)
#     scaler.update()
```

## Gradient Clipping

```python
# Prevent exploding gradients
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

## Checkpointing

```python
# Save
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss,
}, "checkpoint.pt")

# Load
checkpoint = torch.load("checkpoint.pt")
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
```

## Weight Initialization

```python
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        nn.init.zeros_(m.bias)
    elif isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode="fan_out")

model.apply(init_weights)
```

## Exercises

1. Train a model with cosine annealing and plot the learning rate over epochs.
2. Compare training speed with and without mixed precision on a GPU.
3. Implement a training loop with checkpointing that resumes from the last saved state.

---

[← prev](./chapter-05-transfer.md) | [next →](./chapter-06-deployment.md)
