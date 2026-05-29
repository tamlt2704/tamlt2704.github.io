---
title: "Chapter 5: Transfer Learning"
description: "Leveraging pretrained models for new tasks"
---

# Chapter 5: Transfer Learning

## Using Pretrained ResNet

```python
import torch
import torch.nn as nn
import torchvision.models as models

# Load pretrained ResNet18
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace final layer for our task (e.g., 5 classes)
model.fc = nn.Linear(model.fc.in_features, 5)
print(model.fc)
```

## Data Preparation for Transfer Learning

```python
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Assumes folder structure: data/train/class1/, data/train/class2/, ...
# train_data = ImageFolder("data/train", transform=transform)
# train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
```

## Fine-tuning Strategy

```python
# Unfreeze last few layers for fine-tuning
for param in model.layer4.parameters():
    param.requires_grad = True

# Different learning rates
optimizer = torch.optim.Adam([
    {"params": model.layer4.parameters(), "lr": 1e-4},
    {"params": model.fc.parameters(), "lr": 1e-3},
])

criterion = nn.CrossEntropyLoss()
```

## Training Loop

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# for epoch in range(10):
#     model.train()
#     for images, labels in train_loader:
#         images, labels = images.to(device), labels.to(device)
#         optimizer.zero_grad()
#         loss = criterion(model(images), labels)
#         loss.backward()
#         optimizer.step()
```

## Exercises

1. Fine-tune a pretrained model on a custom dataset of 3 classes (e.g., cats, dogs, birds).
2. Compare accuracy between training from scratch vs. transfer learning on a small dataset.
3. Try different pretrained models (VGG16, EfficientNet) and compare results.

---

[← prev](./chapter-04-rnn.md) | [next →](./chapter-06-training.md)
