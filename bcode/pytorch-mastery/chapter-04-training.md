# Chapter 4: The Training Loop

[← Chapter 3: Neural Networks](chapter-03-nn-module.md) | [Chapter 5: Data Loading →](chapter-05-data.md)

---

## The Project

Client: a social media company needs a sentiment classifier. Given a movie review, predict positive or negative. They have 25,000 labeled reviews. The model must generalize — not just memorize.

Mara: "The training loop is always the same five lines. Loss, zero grad, backward, step, repeat. Burn it into muscle memory."

## Loss Functions

Loss measures how wrong your predictions are:

```python
import torch
import torch.nn as nn

# Classification: CrossEntropyLoss (combines LogSoftmax + NLLLoss)
loss_fn = nn.CrossEntropyLoss()
logits = torch.randn(32, 10)       # Raw model output (32 samples, 10 classes)
labels = torch.randint(0, 10, (32,))  # True class indices
loss = loss_fn(logits, labels)

# Binary classification: BCEWithLogitsLoss
loss_fn = nn.BCEWithLogitsLoss()
logits = torch.randn(32, 1)        # Raw scores
labels = torch.randint(0, 2, (32, 1)).float()
loss = loss_fn(logits, labels)

# Regression: MSELoss
loss_fn = nn.MSELoss()
predictions = torch.randn(32, 1)
targets = torch.randn(32, 1)
loss = loss_fn(predictions, targets)
```

## Optimizers

Optimizers update parameters using gradients:

```python
model = nn.Linear(100, 10)

# SGD: simple, needs tuning
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam: adaptive learning rate, good default
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# AdamW: Adam with proper weight decay
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

## The Five-Line Loop

```python
for epoch in range(num_epochs):
    for batch_x, batch_y in train_loader:
        predictions = model(batch_x)        # 1. Forward pass
        loss = loss_fn(predictions, batch_y) # 2. Compute loss
        optimizer.zero_grad()                # 3. Zero gradients
        loss.backward()                      # 4. Backward pass
        optimizer.step()                     # 5. Update weights
```

## Train vs Eval Mode

```python
# Training: dropout active, batch norm uses batch stats
model.train()

# Evaluation: dropout disabled, batch norm uses running stats
model.eval()
with torch.no_grad():  # Also disable gradient computation
    predictions = model(test_data)
```

## Overfitting: The Enemy

```python
# Signs of overfitting:
# - Training loss keeps dropping
# - Validation loss starts rising

# Defenses:
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.3),       # Randomly zero 30% of neurons during training
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(128, 10)
)

# Early stopping: stop when val loss stops improving
# Weight decay: penalize large weights (built into AdamW)
```

## The Client Project: Sentiment Classifier

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Simulated tokenized reviews (in practice, use a real tokenizer)
# Each review → fixed-length vector of token indices
VOCAB_SIZE = 10000
MAX_LEN = 200
EMBED_DIM = 64

class SentimentDataset(Dataset):
    def __init__(self, num_samples=5000):
        self.texts = torch.randint(0, VOCAB_SIZE, (num_samples, MAX_LEN))
        self.labels = torch.randint(0, 2, (num_samples,)).float()

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]

class SentimentModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(VOCAB_SIZE, EMBED_DIM)
        self.classifier = nn.Sequential(
            nn.Linear(EMBED_DIM, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        embedded = self.embedding(x)       # (batch, seq_len, embed_dim)
        pooled = embedded.mean(dim=1)      # (batch, embed_dim) — average pooling
        return self.classifier(pooled).squeeze(-1)  # (batch,)

# Setup
train_set = SentimentDataset(4000)
val_set = SentimentDataset(1000)
train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
val_loader = DataLoader(val_set, batch_size=64)

model = SentimentModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.BCEWithLogitsLoss()

# Training with validation tracking
for epoch in range(10):
    # Train
    model.train()
    train_loss = 0
    for texts, labels in train_loader:
        logits = model(texts)
        loss = loss_fn(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # Validate
    model.eval()
    val_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
        for texts, labels in val_loader:
            logits = model(texts)
            val_loss += loss_fn(logits, labels).item()
            preds = (logits > 0).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    print(f"Epoch {epoch+1}: train_loss={train_loss/len(train_loader):.4f} "
          f"val_loss={val_loss/len(val_loader):.4f} val_acc={correct/total:.4f}")
```

## What You Learned

- **Loss functions** — CrossEntropyLoss (classification), BCEWithLogitsLoss (binary), MSELoss (regression)
- **Optimizers** — SGD (simple), Adam (adaptive), AdamW (with weight decay)
- **The loop** — forward, loss, zero_grad, backward, step
- **train() / eval()** — toggle dropout and batch norm behavior
- **Overfitting** — dropout, weight decay, early stopping
- **Validation** — always track val loss to detect overfitting

The model trains, but we hardcoded the data loading. Real datasets need shuffling, batching, augmentation, and parallel loading. That's Chapter 5.

---

[← Chapter 3: Neural Networks](chapter-03-nn-module.md) | [Chapter 5: Data Loading →](chapter-05-data.md)
