# Chapter 10 — Training Loop

[← Chapter 9: Loss & Optimizer](chapter-09-rag.md) | [Next → Chapter 11: Text Generation](chapter-11-eval.md)

---

## Goal

Learn Dataset and DataLoader, then train EmacsGPT on the full Emacs manual.

---

## PyTorch Concept: Dataset + DataLoader

### Custom Dataset

Inherit from `Dataset`, implement `__len__` and `__getitem__`.

```python
import torch
from torch.utils.data import Dataset, DataLoader

class NumberDataset(Dataset):
    def __init__(self, size=100):
        self.data = torch.arange(size)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

ds = NumberDataset(100)
print(len(ds), ds[42])  # 100, tensor(42)
```

### DataLoader

Handles batching, shuffling, and parallel loading automatically.

```python
loader = DataLoader(ds, batch_size=16, shuffle=True)
batch = next(iter(loader))
print(batch.shape)  # torch.Size([16])
```

---

## Applying It: Emacs Text Dataset

```python
# src/dataset.py
import torch
from torch.utils.data import Dataset
from tokenizers import Tokenizer

class EmacsDataset(Dataset):
    def __init__(self, text_path="data/emacs-manual.txt", seq_len=128):
        tokenizer = Tokenizer.from_file("data/tokenizer.json")
        text = open(text_path, encoding="utf-8").read()
        self.ids = tokenizer.encode(text).ids
        self.seq_len = seq_len

    def __len__(self):
        return len(self.ids) - self.seq_len - 1

    def __getitem__(self, idx):
        chunk = self.ids[idx : idx + self.seq_len + 1]
        x = torch.tensor(chunk[:-1])   # input
        y = torch.tensor(chunk[1:])    # target (shifted by 1)
        return x, y
```

---

## The Training Loop

```python
# src/train.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from model.gpt import EmacsGPT
from dataset import EmacsDataset

model = EmacsGPT()
dataset = EmacsDataset(seq_len=128)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(3):
    total_loss = 0
    for step, (x, y) in enumerate(loader):
        logits = model(x)
        loss = loss_fn(logits.view(-1, 8192), y.view(-1))

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()

        if step % 100 == 0:
            print(f"Epoch {epoch} Step {step} Loss: {loss.item():.4f}")

    avg = total_loss / len(loader)
    print(f"Epoch {epoch} avg loss: {avg:.4f}")

torch.save(model.state_dict(), "data/emacs-gpt.pt")
print("Model saved to data/emacs-gpt.pt")
```

---

## Expected Timeline

| Hardware | Time per Epoch | Total (3 epochs) |
|----------|---------------|-------------------|
| CPU (laptop) | ~40 min | ~2 hours |
| GPU (RTX 3060) | ~5 min | ~15 min |

Loss should drop: epoch 0 ≈ 7.0 → epoch 1 ≈ 4.5 → epoch 2 ≈ 3.8

---

## What You Learned

- **PyTorch concept**: `Dataset` wraps data with `__getitem__`; `DataLoader` handles batching/shuffling
- **Build step**: Full training loop — 3 epochs over the Emacs manual, checkpoint saved
- Next-token prediction: input is tokens[0:n], target is tokens[1:n+1]

---

[← Chapter 9: Loss & Optimizer](chapter-09-rag.md) | [Next → Chapter 11: Text Generation](chapter-11-eval.md)
