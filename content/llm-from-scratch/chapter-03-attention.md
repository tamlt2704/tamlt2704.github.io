# Chapter 3: Attention Mechanism

[prev: Embeddings](chapter-02-embeddings.md) | [next: Transformer Block](chapter-04-transformer.md)

Attention allows each token to look at every other token and decide what information to gather. It is the core mechanism that gives transformers their power.

## Intuition: Query, Key, Value

Think of attention like a search engine:

- **Query (Q)**: "What am I looking for?"
- **Key (K)**: "What do I contain?" (for each token)
- **Value (V)**: "What information do I provide?" (for each token)

The attention score between two tokens = how well the query matches the key. High score = "pay more attention to this token's value."

## Scaled Dot-Product Attention

`Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V`

```python
import torch
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q shape: (batch, seq_len, d_k)
    K shape: (batch, seq_len, d_k)
    V shape: (batch, seq_len, d_v)
    """
    d_k = Q.shape[-1]
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    # scores shape: (batch, seq_len, seq_len)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attention_weights = F.softmax(scores, dim=-1)
    # attention_weights shape: (batch, seq_len, seq_len)

    output = attention_weights @ V
    # output shape: (batch, seq_len, d_v)
    return output, attention_weights
```

**Why scale by `sqrt(d_k)`?** Without scaling, dot products grow large with dimension, pushing softmax into regions with tiny gradients.

## Single-Head Attention from Scratch

```python
import torch
import torch.nn as nn
import math

class SingleHeadAttention(nn.Module):
    def __init__(self, embed_dim, head_dim):
        super().__init__()
        self.W_q = nn.Linear(embed_dim, head_dim, bias=False)
        self.W_k = nn.Linear(embed_dim, head_dim, bias=False)
        self.W_v = nn.Linear(embed_dim, head_dim, bias=False)
        self.head_dim = head_dim

    def forward(self, x, mask=None):
        # x shape: (batch, seq_len, embed_dim)
        Q = self.W_q(x)  # (batch, seq_len, head_dim)
        K = self.W_k(x)  # (batch, seq_len, head_dim)
        V = self.W_v(x)  # (batch, seq_len, head_dim)

        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.head_dim)
        # scores shape: (batch, seq_len, seq_len)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        weights = torch.softmax(scores, dim=-1)
        output = weights @ V
        # output shape: (batch, seq_len, head_dim)
        return output

# Test
attn = SingleHeadAttention(embed_dim=768, head_dim=64)
x = torch.randn(2, 10, 768)  # batch=2, seq_len=10
out = attn(x)
print(f"Output shape: {out.shape}")  # (2, 10, 64)
```

## Multi-Head Attention

Multiple heads let the model attend to different types of relationships simultaneously:

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, embed_dim, n_heads, dropout=0.1):
        super().__init__()
        assert embed_dim % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = embed_dim // n_heads

        self.W_qkv = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.W_out = nn.Linear(embed_dim, embed_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # x shape: (batch, seq_len, embed_dim)
        batch, seq_len, embed_dim = x.shape

        qkv = self.W_qkv(x)  # (batch, seq_len, 3 * embed_dim)
        qkv = qkv.reshape(batch, seq_len, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]
        # Each: (batch, n_heads, seq_len, head_dim)

        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.head_dim)
        # scores: (batch, n_heads, seq_len, seq_len)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        weights = torch.softmax(scores, dim=-1)
        weights = self.dropout(weights)

        attn_output = weights @ V
        # attn_output: (batch, n_heads, seq_len, head_dim)

        attn_output = attn_output.transpose(1, 2).reshape(batch, seq_len, embed_dim)
        output = self.W_out(attn_output)
        # output: (batch, seq_len, embed_dim)
        return output
```

## Causal Masking (for Autoregressive Generation)

In a language model, token at position `i` should only attend to positions `0..i`. We enforce this with a causal mask:

```python
import torch

def create_causal_mask(seq_len):
    """Position i can attend to positions 0..i only."""
    mask = torch.tril(torch.ones(seq_len, seq_len))
    # Example for seq_len=4:
    # [[1, 0, 0, 0],
    #  [1, 1, 0, 0],
    #  [1, 1, 1, 0],
    #  [1, 1, 1, 1]]
    return mask.unsqueeze(0).unsqueeze(0)
    # output shape: (1, 1, seq_len, seq_len)
```

## Causal Self-Attention (Complete Module for GPT)

```python
import torch
import torch.nn as nn
import math

class CausalSelfAttention(nn.Module):
    def __init__(self, embed_dim, n_heads, max_len=1024, dropout=0.1):
        super().__init__()
        assert embed_dim % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = embed_dim // n_heads

        self.W_qkv = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.W_out = nn.Linear(embed_dim, embed_dim, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

        # Pre-compute causal mask (buffer, not parameter)
        mask = torch.tril(torch.ones(max_len, max_len))
        self.register_buffer("mask", mask.view(1, 1, max_len, max_len))

    def forward(self, x):
        # x shape: (batch, seq_len, embed_dim)
        batch, seq_len, embed_dim = x.shape

        qkv = self.W_qkv(x).reshape(batch, seq_len, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]
        # Each: (batch, n_heads, seq_len, head_dim)

        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.head_dim)
        scores = scores.masked_fill(
            self.mask[:, :, :seq_len, :seq_len] == 0, float('-inf')
        )

        weights = torch.softmax(scores, dim=-1)
        weights = self.attn_dropout(weights)

        out = weights @ V  # (batch, n_heads, seq_len, head_dim)
        out = out.transpose(1, 2).reshape(batch, seq_len, embed_dim)
        out = self.W_out(out)
        out = self.resid_dropout(out)
        return out  # (batch, seq_len, embed_dim)
```

## KV-Cache for Inference

During generation, we produce one token at a time. Without caching, we recompute attention over the entire sequence for each new token. KV-cache stores past keys and values:

```python
import torch
import torch.nn as nn
import math

class CausalSelfAttentionWithCache(nn.Module):
    def __init__(self, embed_dim, n_heads, dropout=0.1):
        super().__init__()
        assert embed_dim % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = embed_dim // n_heads

        self.W_qkv = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.W_out = nn.Linear(embed_dim, embed_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, kv_cache=None):
        """
        x: (batch, seq_len, embed_dim) - full seq or new token(s)
        kv_cache: tuple (cached_K, cached_V) or None
        Returns: output, new_kv_cache
        """
        batch, seq_len, embed_dim = x.shape

        qkv = self.W_qkv(x).reshape(batch, seq_len, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]

        if kv_cache is not None:
            K = torch.cat([kv_cache[0], K], dim=2)
            V = torch.cat([kv_cache[1], V], dim=2)

        new_cache = (K, V)

        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.head_dim)
        # For prefill (seq_len > 1), apply causal mask
        if seq_len > 1:
            mask = torch.tril(torch.ones(seq_len, K.shape[2], device=x.device))
            scores = scores.masked_fill(mask.unsqueeze(0).unsqueeze(0) == 0, float('-inf'))

        weights = torch.softmax(scores, dim=-1)
        out = weights @ V
        out = out.transpose(1, 2).reshape(batch, seq_len, embed_dim)
        out = self.W_out(out)
        return out, new_cache

# Demo
attn = CausalSelfAttentionWithCache(embed_dim=768, n_heads=12)
prompt = torch.randn(1, 5, 768)  # 5 prompt tokens
out, cache = attn(prompt, kv_cache=None)
print(f"Prefill: {out.shape}")        # (1, 5, 768)
print(f"Cache K: {cache[0].shape}")   # (1, 12, 5, 64)

new_token = torch.randn(1, 1, 768)
out, cache = attn(new_token, kv_cache=cache)
print(f"Generate: {out.shape}")       # (1, 1, 768)
print(f"Cache K: {cache[0].shape}")   # (1, 12, 6, 64)
```

**Without KV-cache**: Generating N tokens costs `O(N^2)` attention computations.
**With KV-cache**: Each new token costs `O(N)` per step.

## Key Takeaways

- Attention computes weighted sums of values based on query-key similarity
- Scaling by `sqrt(d_k)` prevents gradient vanishing in softmax
- Multi-head attention runs multiple attention patterns in parallel
- Causal masking prevents attending to future tokens
- KV-cache eliminates redundant computation during generation
