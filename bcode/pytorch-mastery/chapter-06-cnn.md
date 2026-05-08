# Chapter 6: CNNs — Seeing Patterns

[← Chapter 5: Data Loading](chapter-05-data.md) | [Chapter 7: RNNs →](chapter-07-rnn.md)

---

## The Project

Client: a warehouse automation company needs an object detector for their conveyor belt. Cameras capture items at 30fps. A feedforward net won't work — it ignores spatial relationships. You need convolutions.

Mara: "A Conv2d layer slides a small filter across the image. It learns *what* to look for. Pooling learns *where* to look."

## Conv2d: The Core Operation

```python
import torch
import torch.nn as nn

# Conv2d(in_channels, out_channels, kernel_size)
conv = nn.Conv2d(3, 16, kernel_size=3, padding=1)

# Input: (batch, channels, height, width)
x = torch.randn(1, 3, 32, 32)  # 1 RGB image, 32×32
out = conv(x)
print(out.shape)  # (1, 16, 32, 32) — 16 feature maps

# Without padding: output shrinks
conv_no_pad = nn.Conv2d(3, 16, kernel_size=3)
out = conv_no_pad(x)
print(out.shape)  # (1, 16, 30, 30) — lost 2 pixels per side

# Stride: skip pixels (downsamples)
conv_stride = nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1)
out = conv_stride(x)
print(out.shape)  # (1, 16, 16, 16) — halved spatial dims
```

## MaxPool2d: Downsample

```python
pool = nn.MaxPool2d(kernel_size=2, stride=2)
x = torch.randn(1, 16, 32, 32)
out = pool(x)
print(out.shape)  # (1, 16, 16, 16) — halved H and W
```

## A CNN Architecture

```python
class ConvNet(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),   # (B, 32, 32, 32)
            nn.ReLU(),
            nn.MaxPool2d(2),                   # (B, 32, 16, 16)
            nn.Conv2d(32, 64, 3, padding=1),  # (B, 64, 16, 16)
            nn.ReLU(),
            nn.MaxPool2d(2),                   # (B, 64, 8, 8)
            nn.Conv2d(64, 128, 3, padding=1), # (B, 128, 8, 8)
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),           # (B, 128, 1, 1)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                      # (B, 128)
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)

model = ConvNet()
x = torch.randn(4, 3, 32, 32)
print(model(x).shape)  # (4, 10)
```

## Transfer Learning with Pretrained Models

Why train from scratch when ImageNet models already know edges, textures, and shapes?

```python
from torchvision import models

# Load pretrained ResNet-18
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace the final classification head
num_classes = 5  # Our warehouse items
model.fc = nn.Linear(model.fc.in_features, num_classes)

# Only the new head trains
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Training {trainable:,} / {total:,} parameters")
# Training 2,565 / 11,179,077 parameters
```

## The Client Project: Conveyor Belt Classifier

```python
import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader, TensorDataset

# Simulate conveyor belt images (5 item types)
NUM_CLASSES = 5
train_images = torch.randn(500, 3, 224, 224)
train_labels = torch.randint(0, NUM_CLASSES, (500,))
val_images = torch.randn(100, 3, 224, 224)
val_labels = torch.randint(0, NUM_CLASSES, (100,))

train_loader = DataLoader(TensorDataset(train_images, train_labels),
                          batch_size=32, shuffle=True)
val_loader = DataLoader(TensorDataset(val_images, val_labels), batch_size=32)

# Transfer learning: pretrained ResNet-18
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for param in model.parameters():
    param.requires_grad = False
model.fc = nn.Linear(512, NUM_CLASSES)

optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

# Train only the head
for epoch in range(5):
    model.train()
    for images, labels in train_loader:
        logits = model(images)
        loss = loss_fn(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Validate
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            preds = model(images).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    print(f"Epoch {epoch+1}: val_acc={correct/total:.4f}")
```

## What You Learned

- **Conv2d** — slides learned filters across spatial dimensions
- **MaxPool2d** — downsamples by taking max in each window
- **Feature maps** — each conv filter detects a different pattern
- **AdaptiveAvgPool2d** — pools to fixed size regardless of input
- **Transfer learning** — use pretrained weights, replace the head
- **Freezing** — `requires_grad = False` to lock pretrained layers

The CNN handles spatial data. But what about sequences — text, time series, audio? Those need memory of what came before. Next: recurrent networks.

---

[← Chapter 5: Data Loading](chapter-05-data.md) | [Chapter 7: RNNs →](chapter-07-rnn.md)
