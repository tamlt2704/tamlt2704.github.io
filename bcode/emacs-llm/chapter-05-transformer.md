# Chapter 5 — Embeddings

[← Chapter 4: Train a Tokenizer](chapter-04-tokenizer.md) | [Next → Chapter 6: Self-Attention](chapter-06-training.md)

---

## Goal

Learn tensors and nn.Embedding, then build the embedding layer for our LLM.

---

## PyTorch Concept: Tensors + nn.Embedding

### What's a Tensor?

A tensor is just a multi-dimensional array with GPU support and automatic differentiation.

```python
import torch

# Scalars, vectors, matrices — all tensors
scalar = torch.tensor(3.14)           # 0-D
vector = torch.tensor([1, 2, 3])      # 1-D
matrix = torch.tensor([[1, 2], [3, 4]])  # 2-D

print(vector.shape)   # torch.Size([3])
print(matrix.dtype)   # torch.int64
```

### What's nn.Embedding?

A lookup table that maps integer IDs to dense vectors. Each row is a learnable vector.

```python
import torch.nn as nn

# 10 words in vocab, each represented as a 4-dim vector
embed = nn.Embedding(num_embeddings=10, embedding_dim=4)

ids = torch.tensor([2, 5, 7])  # look up words 2, 5, 7
vectors = embed(ids)           # shape: (3, 4)
print(vectors.shape)           # torch.Size([3, 4])
# Each ID gets its own learnable 4-dimensional vector
```

---

## Applying It: Token + Position Embeddings

Every transformer needs two embeddings:
- **Token embedding**: what word is this?
- **Position embedding**: where in the sequence is it?

```python
# src/model/embedding.py
import torch
import torch.nn as nn

class EmacsEmbedding(nn.Module):
    def __init__(self, vocab_size=8192, d_model=256, max_len=512):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)

    def forward(self, token_ids):
        # token_ids shape: (batch, seq_len)
        seq_len = token_ids.size(1)
        positions = torch.arange(seq_len, device=token_ids.device)

        tok = self.token_emb(token_ids)   # (batch, seq_len, d_model)
        pos = self.pos_emb(positions)     # (seq_len, d_model)

        return tok + pos  # broadcast addition
```

---

## Test It

```python
emb = EmacsEmbedding()
fake_input = torch.randint(0, 8192, (2, 64))  # batch=2, seq_len=64
output = emb(fake_input)
print(output.shape)  # torch.Size([2, 64, 256])
```

Two sequences of 64 tokens, each token now a 256-dim vector. Ready for attention.

---

## What You Learned

- **PyTorch concept**: Tensors are N-dimensional arrays; `nn.Embedding` is a learnable lookup table
- **Build step**: Token + positional embeddings that convert token IDs into rich vectors
- Our model config: vocab=8192, d_model=256, max_len=512

---

[← Chapter 4: Train a Tokenizer](chapter-04-tokenizer.md) | [Next → Chapter 6: Self-Attention](chapter-06-training.md)
