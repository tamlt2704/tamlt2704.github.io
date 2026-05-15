# Chapter 8 — Full Model Assembly

[← Chapter 7: Transformer Block](chapter-07-finetune.md) | [Next → Chapter 9: Loss & Optimizer](chapter-09-rag.md)

---

## Goal

Learn nn.ModuleList for stacking layers, then assemble the complete EmacsGPT model.

---

## PyTorch Concept: Composing nn.Modules (nn.ModuleList)

### Why ModuleList?

A plain Python list of layers won't register parameters. `nn.ModuleList` tells PyTorch "these are all part of the model."

```python
import torch.nn as nn

# Wrong — parameters won't be tracked:
# self.layers = [nn.Linear(4, 4) for _ in range(3)]

# Right — PyTorch sees all parameters:
class StackedLayers(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList([nn.Linear(4, 4) for _ in range(3)])

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

model = StackedLayers()
print(sum(p.numel() for p in model.parameters()))  # 60 (3 × (4*4 + 4))
```

---

## Applying It: The Full EmacsGPT Model

```python
# src/model/gpt.py
import torch
import torch.nn as nn
from .embedding import EmacsEmbedding
from .block import TransformerBlock

class EmacsGPT(nn.Module):
    def __init__(
        self,
        vocab_size=8192,
        d_model=256,
        n_heads=4,
        n_layers=6,
        max_len=512,
    ):
        super().__init__()
        self.embedding = EmacsEmbedding(vocab_size, d_model, max_len)
        self.blocks = nn.ModuleList(
            [TransformerBlock(d_model, n_heads) for _ in range(n_layers)]
        )
        self.ln_final = nn.LayerNorm(d_model)
        self.output_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, token_ids):
        x = self.embedding(token_ids)
        for block in self.blocks:
            x = block(x)
        x = self.ln_final(x)
        logits = self.output_head(x)  # (batch, seq_len, vocab_size)
        return logits
```

---

## Count Parameters

```python
model = EmacsGPT()
total = sum(p.numel() for p in model.parameters())
print(f"EmacsGPT: {total:,} parameters")
# EmacsGPT: ~5,200,000 parameters (5.2M)
```

For reference: GPT-2 small = 124M. Ours is 24× smaller — trainable on a laptop CPU.

---

## Smoke Test

```python
ids = torch.randint(0, 8192, (1, 128))  # 1 sequence, 128 tokens
logits = model(ids)
print(logits.shape)  # torch.Size([1, 128, 8192])
# Each position predicts a distribution over 8192 possible next tokens
```

---

## Model Config Summary

| Parameter | Value |
|-----------|-------|
| vocab_size | 8,192 |
| d_model | 256 |
| n_heads | 4 |
| n_layers | 6 |
| max_len | 512 |
| Total params | ~5.2M |

---

## What You Learned

- **PyTorch concept**: `nn.ModuleList` registers sub-modules so parameters are tracked
- **Build step**: Complete EmacsGPT — embeddings → 6 transformer blocks → output head
- 5.2M parameters: small enough to train on CPU, large enough to learn Emacs patterns

---

[← Chapter 7: Transformer Block](chapter-07-finetune.md) | [Next → Chapter 9: Loss & Optimizer](chapter-09-rag.md)
