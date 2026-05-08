# Chapter 2: The Bigram Model — Your First Neural Language Model

[← Chapter 1: Tokenization](chapter-01-tokenization.md) | [Chapter 3: Embeddings →](chapter-03-embeddings.md)

---

## The Problem

We have tokens — integers representing characters. But we have no model. No predictions. No generation. Nothing.

Dr. Lin: "Build the dumbest possible language model. I want to see loss go down by end of day. I don't care if the output is garbage — I want a training loop that works."

## The Bigram Model

The simplest language model: predict the next token using **only** the current token. No context. No memory. Just: "Given that the current character is 'h', what's the most likely next character?"

This is a lookup table. For each token in our vocabulary, we store a distribution over what comes next.

```
Current token: 'h'  → Next: 'e' (0.35), 'a' (0.20), 'i' (0.15), ...
Current token: 't'  → Next: 'h' (0.40), 'o' (0.15), 'e' (0.12), ...
Current token: '\n' → Next: ' ' (0.10), 'T' (0.08), 'A' (0.06), ...
```

In neural network terms: a single embedding layer that maps each token to logits over the vocabulary.

## The Code

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import urllib.request
import os

# ─── Data Setup ───────────────────────────────────────────────────────────────

if not os.path.exists('input.txt'):
    url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
    urllib.request.urlretrieve(url, 'input.txt')

with open('input.txt', 'r') as f:
    text = f.read()

# Character-level tokenizer
chars = sorted(set(text))
vocab_size = len(chars)
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}

encode = lambda s: [char_to_idx[c] for c in s]
decode = lambda l: ''.join(idx_to_char[i] for i in l)

data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]

print(f"Vocab size: {vocab_size}")
print(f"Train tokens: {len(train_data):,}")
print(f"Val tokens: {len(val_data):,}")

# ─── Batching ─────────────────────────────────────────────────────────────────

block_size = 8   # context length (doesn't matter much for bigram)
batch_size = 32

def get_batch(split):
    """Get a random batch of input-target pairs."""
    data_split = train_data if split == 'train' else val_data
    # Random starting positions
    ix = torch.randint(len(data_split) - block_size, (batch_size,))
    x = torch.stack([data_split[i:i+block_size] for i in ix])
    y = torch.stack([data_split[i+1:i+block_size+1] for i in ix])
    return x, y

# Example batch
xb, yb = get_batch('train')
print(f"\nBatch shapes: x={xb.shape}, y={yb.shape}")
# x: (32, 8) — 32 sequences of 8 tokens
# y: (32, 8) — the next token for each position

# ─── The Bigram Model ─────────────────────────────────────────────────────────

class BigramLanguageModel(nn.Module):
    """The simplest neural language model: predict next token from current token only."""

    def __init__(self, vocab_size):
        super().__init__()
        # Each token directly looks up logits for the next token
        # This is just a (vocab_size × vocab_size) lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx, targets=None):
        # idx shape: (batch, seq_len)
        logits = self.token_embedding_table(idx)  # (batch, seq_len, vocab_size)

        if targets is None:
            loss = None
        else:
            # Reshape for cross-entropy: (B*T, C) and (B*T,)
            B, T, C = logits.shape
            logits_flat = logits.view(B * T, C)
            targets_flat = targets.view(B * T)
            loss = F.cross_entropy(logits_flat, targets_flat)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        """Generate new tokens autoregressively."""
        for _ in range(max_new_tokens):
            # Get predictions (only use last token for bigram)
            logits, _ = self(idx)
            # Focus on last time step
            logits = logits[:, -1, :]  # (batch, vocab_size)
            # Convert to probabilities
            probs = F.softmax(logits, dim=-1)
            # Sample from distribution
            idx_next = torch.multinomial(probs, num_samples=1)  # (batch, 1)
            # Append to sequence
            idx = torch.cat([idx, idx_next], dim=1)
        return idx

model = BigramLanguageModel(vocab_size)
print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")
# vocab_size × vocab_size = 65 × 65 = 4,225 parameters

# ─── Before Training: Random Output ──────────────────────────────────────────

print("\n--- Generation BEFORE training ---")
start = torch.zeros((1, 1), dtype=torch.long)  # Start with token 0 (newline)
generated = model.generate(start, max_new_tokens=100)
print(decode(generated[0].tolist()))
```

Output before training (complete garbage):
```
eFwZKjPx&qMbS!yTfhrl:VOwU
NiJdvXgCzAp;RtYkDm,HBu'Ls
```

Random characters. The model hasn't learned anything yet.

## Training Loop

```python
# ─── Training ─────────────────────────────────────────────────────────────────

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

for step in range(10000):
    # Get batch
    xb, yb = get_batch('train')

    # Forward pass
    logits, loss = model(xb, yb)

    # Backward pass
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    # Print progress
    if step % 2000 == 0:
        print(f"Step {step:5d} | Loss: {loss.item():.4f}")

print(f"\nFinal loss: {loss.item():.4f}")
print(f"Random baseline: {-torch.log(torch.tensor(1.0/vocab_size)).item():.4f}")
```

Output:
```
Step     0 | Loss: 4.6911
Step  2000 | Loss: 2.5843
Step  4000 | Loss: 2.5012
Step  6000 | Loss: 2.4876
Step  8000 | Loss: 2.4734

Final loss: 2.4680
Random baseline: 4.1744
```

Loss dropped from ~4.7 (random) to ~2.5. The model learned something! But 2.5 is still high — a perfect bigram model on English text gets around 2.4.

## After Training: Still Garbage (But Better Garbage)

```python
# ─── Generation AFTER Training ────────────────────────────────────────────────

print("\n--- Generation AFTER training ---")
start = torch.zeros((1, 1), dtype=torch.long)
generated = model.generate(start, max_new_tokens=300)
print(decode(generated[0].tolist()))
```

Output after training:
```

CEThik bere my:
Yof isth t d hereroube lat igmin
Whar vet, wande
Thas m t y oroup
INGoat hed
Byo ath, ange; t tes
```

It's still garbage! But look closer:
- It learned that spaces follow words
- It learned common letter pairs ("th", "he", "er")
- It learned that newlines happen after punctuation
- It learned that capital letters start lines

The bigram model captures **local character statistics** but nothing more. It can't spell words because it has no memory — each prediction only sees one character.

## Why It's Limited

The bigram model's fundamental problem: **no context**.

```
"The cat sat on the ___"

Bigram sees: 'e' → predicts next character
It doesn't know it's in the word "the"
It doesn't know "cat" came before
It doesn't know this is English
```

Every prediction is based on a single character. To generate real words and sentences, we need the model to look at multiple previous tokens. That requires:
1. **Embeddings** — give tokens richer representations (Chapter 3)
2. **Attention** — let tokens look at each other (Chapter 4)

## Understanding the Loss

Cross-entropy loss measures how surprised the model is by the correct answer:

```python
# If vocab_size = 65 and model predicts uniformly:
# P(correct) = 1/65
# Loss = -log(1/65) = 4.17 (very surprised)

# After training, model learns 'h' often follows 't':
# P('h' | 't') = 0.25
# Loss = -log(0.25) = 1.39 (less surprised)

# Perfect prediction:
# P(correct) = 1.0
# Loss = -log(1.0) = 0.0 (not surprised at all)
```

Our model went from 4.7 → 2.5. It's less surprised, but still quite uncertain about what comes next. That's because with only one character of context, there IS genuine uncertainty.

## The Complete Script

Here's everything in one runnable file:

```python
"""
Bigram Language Model — the simplest neural LM.
Run: python bigram.py
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import urllib.request
import os

# Hyperparameters
batch_size = 32
block_size = 8
max_iters = 10000
learning_rate = 1e-3
eval_interval = 2000
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Data
if not os.path.exists('input.txt'):
    url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
    urllib.request.urlretrieve(url, 'input.txt')

with open('input.txt', 'r') as f:
    text = f.read()

chars = sorted(set(text))
vocab_size = len(chars)
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}
encode = lambda s: [char_to_idx[c] for c in s]
decode = lambda l: ''.join(idx_to_char[i] for i in l)

data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]

def get_batch(split):
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - block_size, (batch_size,))
    x = torch.stack([d[i:i+block_size] for i in ix]).to(device)
    y = torch.stack([d[i+1:i+block_size+1] for i in ix]).to(device)
    return x, y

# Model
class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx, targets=None):
        logits = self.token_embedding_table(idx)
        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T))
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            logits, _ = self(idx)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx

model = BigramLanguageModel(vocab_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

# Training
for step in range(max_iters):
    xb, yb = get_batch('train')
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    if step % eval_interval == 0:
        print(f"Step {step:5d} | Loss: {loss.item():.4f}")

# Generate
print("\n--- Generated Text ---")
start = torch.zeros((1, 1), dtype=torch.long, device=device)
print(decode(model.generate(start, max_new_tokens=500)[0].tolist()))
```

## What You Learned

- **Bigram model** — predicts next token from current token only (a lookup table)
- **nn.Embedding** — maps token indices to vectors (here, directly to logits)
- **Cross-entropy loss** — measures prediction quality (-log of correct token's probability)
- **Training loop** — forward pass → loss → backward pass → optimizer step
- **Autoregressive generation** — predict one token, append it, repeat
- **The limitation** — no context means no real language understanding

The model works but generates nonsense because it only sees one token at a time. To improve, we need richer token representations. That's embeddings.

---

[← Chapter 1: Tokenization](chapter-01-tokenization.md) | [Chapter 3: Embeddings →](chapter-03-embeddings.md)
