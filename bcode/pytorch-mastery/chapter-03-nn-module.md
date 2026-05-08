# Chapter 3: Building Neural Networks

[← Chapter 2: Autograd](chapter-02-autograd.md) | [Chapter 4: Training Loop →](chapter-04-training.md)

---

## The Project

Client: a bank wants a digit classifier for check processing. They have the MNIST dataset — 70,000 handwritten digits (28×28 grayscale images). Build a feedforward neural network that classifies them.

Mara: "Print the tensor shapes. At every layer. Every time. Shape bugs are 90% of neural network bugs."

## nn.Module: The Building Block

Every neural network in PyTorch inherits from `nn.Module`:

```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(784, 128)  # 28*28 input → 128 hidden
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(128, 10)   # 128 → 10 classes (digits 0-9)

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        return x

model = SimpleNet()
print(model)
```

## nn.Linear

A fully connected layer: `output = input @ weight.T + bias`

```python
linear = nn.Linear(in_features=784, out_features=128)
print(linear.weight.shape)  # (128, 784)
print(linear.bias.shape)    # (128,)

# Pass data through
x = torch.randn(32, 784)    # Batch of 32, each 784 features
out = linear(x)
print(out.shape)             # (32, 128)
```

## Activation Functions

```python
relu = nn.ReLU()       # max(0, x) — most common
sigmoid = nn.Sigmoid() # squash to (0, 1)
tanh = nn.Tanh()       # squash to (-1, 1)

# Functional versions (no state, used inline)
import torch.nn.functional as F
x = torch.randn(5)
F.relu(x)
F.softmax(x, dim=0)  # Probabilities that sum to 1
```

## parameters() — What the Model Learns

```python
model = SimpleNet()

# All learnable parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params}")  # 101,770

for name, param in model.named_parameters():
    print(f"{name}: {param.shape}")
# layer1.weight: torch.Size([128, 784])
# layer1.bias: torch.Size([128])
# layer2.weight: torch.Size([10, 128])
# layer2.bias: torch.Size([10])
```

## nn.Sequential — Quick Stacking

```python
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

x = torch.randn(32, 784)
out = model(x)
print(out.shape)  # (32, 10)
```

## The Client Project: MNIST Digit Classifier

```python
import torch
import torch.nn as nn
from torchvision import datasets, transforms

# Load MNIST
transform = transforms.ToTensor()  # Converts to (1, 28, 28) float [0,1]
train_data = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_data = datasets.MNIST('./data', train=False, transform=transform)

train_loader = torch.utils.data.DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=64)

# The model
class DigitClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.network = nn.Sequential(
            nn.Linear(28 * 28, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        x = self.flatten(x)       # (batch, 1, 28, 28) → (batch, 784)
        return self.network(x)    # (batch, 784) → (batch, 10)

model = DigitClassifier()

# Quick shape check
sample_batch = torch.randn(64, 1, 28, 28)
output = model(sample_batch)
print(f"Input:  {sample_batch.shape}")  # (64, 1, 28, 28)
print(f"Output: {output.shape}")        # (64, 10)

# Training (simplified — full loop in Chapter 4)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(3):
    for images, labels in train_loader:
        output = model(images)
        loss = loss_fn(output, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Test accuracy
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            preds = model(images).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    print(f"Epoch {epoch+1}: accuracy = {correct/total:.4f}")
# Epoch 1: accuracy ≈ 0.9650
# Epoch 3: accuracy ≈ 0.9750
```

## What You Learned

- **nn.Module** — base class for all models; define `__init__` and `forward`
- **nn.Linear** — fully connected layer (matrix multiply + bias)
- **nn.ReLU** — activation function (introduces non-linearity)
- **forward()** — defines how data flows through the network
- **parameters()** — iterator over all learnable weights
- **nn.Sequential** — stack layers without writing a class
- **Shape discipline** — always verify shapes at each layer

The model works, but we glossed over the training loop. Next chapter: loss functions, optimizers, and the full training recipe.

---

[← Chapter 2: Autograd](chapter-02-autograd.md) | [Chapter 4: Training Loop →](chapter-04-training.md)
