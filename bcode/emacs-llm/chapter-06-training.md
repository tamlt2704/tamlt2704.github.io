# Chapter 6 — Self-Attention

[← Chapter 5: Embeddings](chapter-05-transformer.md) | [Next → Chapter 7: Transformer Block](chapter-07-finetune.md)

---

## Goal

Learn matrix multiplication and softmax, then build single-head and multi-head attention.

---

## PyTorch Concept: Matrix Multiplication + Softmax

### The @ Operator

`@` does matrix multiplication. It's how queries "ask" keys for relevance scores.

```python
import torch

A = torch.randn(3, 4)  # 3 queries, each 4-dim
B = torch.randn(4, 5)  # 4-dim keys, 5 of them
C = A @ B               # (3, 5) — each query scores against each key
print(C.shape)          # torch.Size([3, 5])
```

### F.softmax

Converts raw scores into a probability distribution (sums to 1, all positive).

```python
import torch.nn.functional as F

scores = torch.tensor([2.0, 1.0, 0.1])
weights = F.softmax(scores, dim=-1)
print(weights)  # tensor([0.659, 0.242, 0.099]) — sums to 1.0
```

---

## Applying It: Single-Head Attention

The core idea: each token creates a Query, Key, and Value. Queries ask "what should I attend to?", Keys answer "here's what I contain", Values provide "here's my content."

```python
# src/model/attention.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SingleHeadAttention(nn.Module):
    def __init__(self, d_model=256, head_dim=64):
        super().__init__()
        self.q = nn.Linear(d_model, head_dim, bias=False)
        self.k = nn.Linear(d_model, head_dim, bias=False)
        self.v = nn.Linear(d_model, head_dim, bias=False)
        self.scale = math.sqrt(head_dim)

    def forward(self, x):
        Q, K, V = self.q(x), self.k(x), self.v(x)

        # Attention scores: how much each token attends to others
        scores = (Q @ K.transpose(-2, -1)) / self.scale

        # Causal mask: can't look at future tokens
        mask = torch.triu(torch.ones_like(scores), diagonal=1).bool()
        scores = scores.masked_fill(mask, float("-inf"))

        weights = F.softmax(scores, dim=-1)
        return weights @ V  # weighted sum of values
```

---

## Multi-Head Attention

Multiple heads let the model attend to different things simultaneously (syntax, semantics, position).

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=256, n_heads=4):
        super().__init__()
        assert d_model % n_heads == 0
        head_dim = d_model // n_heads
        self.heads = nn.ModuleList(
            [SingleHeadAttention(d_model, head_dim) for _ in range(n_heads)]
        )
        self.proj = nn.Linear(d_model, d_model)

    def forward(self, x):
        # Run all heads, concatenate, project back
        head_outputs = [h(x) for h in self.heads]
        concat = torch.cat(head_outputs, dim=-1)
        return self.proj(concat)
```

---

## Test It

```python
mha = MultiHeadAttention(d_model=256, n_heads=4)
x = torch.randn(2, 64, 256)  # batch=2, seq=64, d_model=256
out = mha(x)
print(out.shape)  # torch.Size([2, 64, 256])
```

---

## What You Learned

- **PyTorch concept**: `@` for matmul, `F.softmax` for probability distributions
- **Build step**: Single-head attention (Q·K/√d → softmax → ·V) and multi-head wrapper
- Causal masking prevents the model from cheating by looking at future tokens

---

[← Chapter 5: Embeddings](chapter-05-transformer.md) | [Next → Chapter 7: Transformer Block](chapter-07-finetune.md)
