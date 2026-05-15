# Chapter 7 — Transformer Block

[← Chapter 6: Self-Attention](chapter-06-training.md) | [Next → Chapter 8: Full Model Assembly](chapter-08-inference.md)

---

## Goal

Learn nn.Module, nn.Linear, and LayerNorm, then build a complete transformer block.

---

## PyTorch Concept: nn.Module + nn.Linear + LayerNorm

### nn.Module

Every neural network component inherits from `nn.Module`. Define layers in `__init__`, computation in `forward`.

```python
import torch
import torch.nn as nn

class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.Linear(4, 2)  # 4 inputs → 2 outputs

    def forward(self, x):
        return self.layer(x)

net = TinyNet()
print(sum(p.numel() for p in net.parameters()))  # 10 params (4*2 + 2 bias)
```

### nn.Linear

A fully-connected layer: `output = input @ W.T + bias`. The workhorse of neural nets.

### LayerNorm

Normalizes each sample independently to have mean=0, std=1. Stabilizes training.

```python
norm = nn.LayerNorm(256)
x = torch.randn(2, 64, 256)
out = norm(x)  # each 256-dim vector normalized independently
print(out.mean(dim=-1)[0, 0])  # ≈ 0.0
```

---

## Applying It: The Transformer Block

A transformer block = attention + feed-forward network + residual connections + layer norm.

```python
# src/model/block.py
import torch.nn as nn
from .attention import MultiHeadAttention

class FeedForward(nn.Module):
    def __init__(self, d_model=256, d_ff=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x):
        return self.net(x)

class TransformerBlock(nn.Module):
    def __init__(self, d_model=256, n_heads=4):
        super().__init__()
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ff = FeedForward(d_model)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x):
        # Pre-norm architecture with residual connections
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x
```

---

## Why Residuals?

Without `x + ...`, gradients vanish in deep networks. Residual connections let gradients flow straight through, making 6+ layer models trainable.

---

## Test It

```python
block = TransformerBlock(d_model=256, n_heads=4)
x = torch.randn(2, 64, 256)
out = block(x)
print(out.shape)  # torch.Size([2, 64, 256])
print(f"Block params: {sum(p.numel() for p in block.parameters()):,}")
# Block params: ~530,000
```

---

## What You Learned

- **PyTorch concept**: `nn.Module` for composable layers, `nn.Linear` for dense transforms, `LayerNorm` for stability
- **Build step**: TransformerBlock with pre-norm, residuals, GELU activation
- One block ≈ 530K params. We'll stack several in the next chapter.

---

[← Chapter 6: Self-Attention](chapter-06-training.md) | [Next → Chapter 8: Full Model Assembly](chapter-08-inference.md)
