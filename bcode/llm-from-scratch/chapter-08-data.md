# Chapter 8: Data Pipeline — Feeding the Model

[← Chapter 7: Training](chapter-07-training.md) | [Chapter 9: Generation →](chapter-09-generation.md)

---

## The Problem

We've been training on tiny Shakespeare — 1.1M characters, one writing style, one era. The model memorizes patterns instead of learning general language. It can only generate pseudo-Shakespeare.

Kai: "Your model is overfitting to one author from 400 years ago. You need diverse text: books, articles, code, conversations. And you need a proper data pipeline — random sampling, efficient batching, no data leakage. Let me show you how real training data works."

## The Dataset Class

PyTorch's `Dataset` and `DataLoader` give us efficient, shuffled batching:

```python
import torch
from torch.utils.data import Dataset, DataLoader
import os
import urllib.request

# ─── Text Dataset ─────────────────────────────────────────────────────────────

class TextDataset(Dataset):
    """Dataset that serves random context windows from a text corpus."""

    def __init__(self, text: str, block_size: int, tokenizer):
        self.block_size = block_size
        self.data = torch.tensor(tokenizer.encode(text), dtype=torch.long)

    def __len__(self):
        # Number of possible starting positions
        return len(self.data) - self.block_size

    def __getitem__(self, idx):
        # Return a (input, target) pair — target is shifted by 1
        x = self.data[idx : idx + self.block_size]
        y = self.data[idx + 1 : idx + self.block_size + 1]
        return x, y


class CharTokenizer:
    """Character-level tokenizer."""

    def __init__(self, text: str):
        chars = sorted(set(text))
        self.vocab_size = len(chars)
        self.char_to_idx = {ch: i for i, ch in enumerate(chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(chars)}

    def encode(self, text: str) -> list[int]:
        return [self.char_to_idx[ch] for ch in text]

    def decode(self, indices: list[int]) -> str:
        return ''.join(self.idx_to_char[i] for i in indices)


# ─── Setup ────────────────────────────────────────────────────────────────────

if not os.path.exists('input.txt'):
    url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
    urllib.request.urlretrieve(url, 'input.txt')

with open('input.txt', 'r') as f:
    text = f.read()

tokenizer = CharTokenizer(text)
print(f"Corpus size: {len(text):,} characters")
print(f"Vocab size: {tokenizer.vocab_size}")

# Train/val split
split_idx = int(0.9 * len(text))
train_text = text[:split_idx]
val_text = text[split_idx:]

# Create datasets
block_size = 256
train_dataset = TextDataset(train_text, block_size, tokenizer)
val_dataset = TextDataset(val_text, block_size, tokenizer)

print(f"Train samples: {len(train_dataset):,}")
print(f"Val samples:   {len(val_dataset):,}")

# ─── DataLoader ───────────────────────────────────────────────────────────────

batch_size = 64

train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True,        # random order each epoch
    num_workers=2,       # parallel data loading
    pin_memory=True,     # faster GPU transfer
    drop_last=True,      # drop incomplete final batch
)

val_loader = DataLoader(
    val_dataset,
    batch_size=batch_size,
    shuffle=False,
    num_workers=2,
    pin_memory=True,
    drop_last=True,
)

# Test it
batch_x, batch_y = next(iter(train_loader))
print(f"\nBatch x shape: {batch_x.shape}")  # (64, 256)
print(f"Batch y shape: {batch_y.shape}")    # (64, 256)
print(f"Sample input:  {tokenizer.decode(batch_x[0][:50].tolist())}")
```

## Multi-File Dataset

For larger training, load from multiple text files:

```python
class MultiFileDataset(Dataset):
    """Load and concatenate multiple text files into one dataset."""

    def __init__(self, file_paths: list[str], block_size: int, tokenizer):
        self.block_size = block_size

        # Concatenate all files
        all_tokens = []
        for path in file_paths:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            tokens = tokenizer.encode(text)
            all_tokens.extend(tokens)
            print(f"  Loaded {path}: {len(tokens):,} tokens")

        self.data = torch.tensor(all_tokens, dtype=torch.long)
        print(f"  Total: {len(self.data):,} tokens")

    def __len__(self):
        return len(self.data) - self.block_size

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.block_size]
        y = self.data[idx + 1 : idx + self.block_size + 1]
        return x, y
```

## Memory-Mapped Dataset for Large Corpora

When your corpus doesn't fit in RAM, use memory-mapped files:

```python
import numpy as np

class MemmapDataset(Dataset):
    """Memory-mapped dataset for corpora too large for RAM."""

    def __init__(self, bin_path: str, block_size: int):
        self.block_size = block_size
        # Memory-map the file — doesn't load into RAM
        self.data = np.memmap(bin_path, dtype=np.uint16, mode='r')
        print(f"Loaded memmap: {len(self.data):,} tokens ({len(self.data)*2/1e9:.2f} GB)")

    def __len__(self):
        return len(self.data) - self.block_size

    def __getitem__(self, idx):
        x = torch.from_numpy(self.data[idx : idx + self.block_size].astype(np.int64))
        y = torch.from_numpy(self.data[idx + 1 : idx + self.block_size + 1].astype(np.int64))
        return x, y


def prepare_memmap(text_path: str, output_path: str, tokenizer):
    """Pre-tokenize a text file and save as binary for fast loading."""
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    tokens = tokenizer.encode(text)
    tokens = np.array(tokens, dtype=np.uint16)
    tokens.tofile(output_path)
    print(f"Saved {len(tokens):,} tokens to {output_path}")
    return output_path
```

## Training Loop with DataLoader

```python
import torch.nn as nn
import torch.nn.functional as F

# Assuming GPT model from Chapter 6 is defined...
# (See chapter-06-gpt.md for full model code)

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# ─── Training with DataLoader ─────────────────────────────────────────────────

def train_epoch(model, loader, optimizer, device, grad_clip=1.0):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    num_batches = 0

    for batch_x, batch_y in loader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        logits, loss = model(batch_x, batch_y)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


@torch.no_grad()
def evaluate(model, loader, device):
    """Evaluate on validation set."""
    model.eval()
    total_loss = 0
    num_batches = 0

    for batch_x, batch_y in loader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        _, loss = model(batch_x, batch_y)
        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


# ─── Full Training Run ────────────────────────────────────────────────────────

# Example training loop (assumes model is already created)
"""
num_epochs = 10

for epoch in range(num_epochs):
    train_loss = train_epoch(model, train_loader, optimizer, device)
    val_loss = evaluate(model, val_loader, device)
    print(f"Epoch {epoch+1}/{num_epochs} | Train: {train_loss:.4f} | Val: {val_loss:.4f}")
"""
```

## Larger Corpus Options

Tiny Shakespeare is great for debugging, but for a real model you want more data:

| Corpus | Size | Description |
|---|---|---|
| Tiny Shakespeare | 1.1M chars | One author, good for testing |
| OpenWebText | 38GB | Web pages (GPT-2's training data, open recreation) |
| The Pile | 800GB | Diverse: books, code, web, academic papers |
| Wikipedia | 20GB | Encyclopedic text |
| Project Gutenberg | 60GB | Public domain books |
| C4 | 750GB | Cleaned Common Crawl |

For this course, Shakespeare is sufficient to demonstrate all concepts. The architecture scales to any corpus size.

```python
# ─── Downloading a Slightly Larger Corpus ─────────────────────────────────────

def download_corpus(name='shakespeare'):
    """Download a training corpus."""
    urls = {
        'shakespeare': 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt',
    }

    if name not in urls:
        print(f"Available: {list(urls.keys())}")
        return None

    path = f'{name}.txt'
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(urls[name], path)

    with open(path, 'r') as f:
        text = f.read()

    print(f"Loaded {name}: {len(text):,} characters")
    return text
```

## Data Quality Matters

Kai's rules for training data:

1. **Deduplicate** — repeated text biases the model toward memorization
2. **Filter quality** — garbage in, garbage out
3. **Diverse sources** — books, web, code, dialogue for a general model
4. **No test leakage** — validation data must never appear in training
5. **Shuffle** — don't train on documents in order (the model would learn document boundaries, not language)

```python
# Simple deduplication at the line level
def deduplicate(text: str) -> str:
    """Remove duplicate lines (simple dedup)."""
    lines = text.split('\n')
    seen = set()
    unique = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique.append(line)
    deduped = '\n'.join(unique)
    print(f"Dedup: {len(lines):,} lines → {len(unique):,} lines "
          f"({100*len(unique)/len(lines):.1f}% kept)")
    return deduped
```

## What You Learned

- **Dataset class** — wraps tokenized text, serves random context windows
- **DataLoader** — handles batching, shuffling, parallel loading, GPU pinning
- **Memory mapping** — `np.memmap` for corpora that don't fit in RAM
- **Pre-tokenization** — tokenize once, save as binary, load fast
- **Multi-file loading** — concatenate multiple text sources
- **Data quality** — deduplication, filtering, diversity, no leakage
- **Epoch-based training** — iterate through entire dataset, then repeat

We have data flowing efficiently into the model. But the model only computes loss — it doesn't generate text in a controllable way. Next: sampling strategies for text generation.

---

[← Chapter 7: Training](chapter-07-training.md) | [Chapter 9: Generation →](chapter-09-generation.md)
