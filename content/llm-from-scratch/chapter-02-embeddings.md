# Chapter 2: Embeddings

[prev: Tokenization](chapter-01-tokenization.md) | [next: Attention](chapter-03-attention.md)

Embeddings convert discrete token IDs into continuous vectors that the model can learn from. Position embeddings tell the model where each token sits in the sequence.

## Word Embeddings Intuition (Word2Vec)

The core idea: words appearing in similar contexts should have similar vector representations.

`"king" - "man" + "woman" ≈ "queen"`

This works because the embedding space captures semantic relationships as directions.

```python
import torch
import torch.nn as nn

# Simple demonstration: learn embeddings via context prediction
# Skip-gram: given a word, predict surrounding words
class SkipGram(nn.Module):
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        self.embeddings = nn.Embedding(vocab_size, embed_dim)
        self.output = nn.Linear(embed_dim, vocab_size)

    def forward(self, center_word):
        # center_word shape: (batch_size,)
        embed = self.embeddings(center_word)  # (batch_size, embed_dim)
        logits = self.output(embed)           # (batch_size, vocab_size)
        return logits
```

In modern LLMs, we don't pre-train Word2Vec separately — the token embeddings are learned end-to-end during language model training.

## Token Embeddings

A lookup table that maps each token ID to a dense vector:

```python
import torch
import torch.nn as nn

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        # Embedding matrix: (vocab_size, embed_dim)
        self.embedding = nn.Embedding(vocab_size, embed_dim)

    def forward(self, token_ids):
        # token_ids shape: (batch_size, seq_len)
        return self.embedding(token_ids)
        # output shape: (batch_size, seq_len, embed_dim)

# Example
vocab_size = 50257
embed_dim = 768
tok_emb = TokenEmbedding(vocab_size, embed_dim)

ids = torch.tensor([[101, 2003, 1037]])  # (1, 3)
vectors = tok_emb(ids)                    # (1, 3, 768)
print(f"Input shape: {ids.shape}")
print(f"Output shape: {vectors.shape}")
```

Each row of the embedding matrix is a learnable vector. Token 101 always maps to the same vector (before attention mixes context in).

## Why Position Matters

Self-attention is permutation-invariant — without positional information, `"dog bites man"` and `"man bites dog"` produce identical representations. We must inject position information.

## Positional Embeddings

### Sinusoidal (Fixed) — Original Transformer

Uses sine and cosine functions at different frequencies:

`PE(pos, 2i) = sin(pos / 10000^(2i/d_model))`
`PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))`

```python
import torch
import math

def sinusoidal_positional_encoding(max_len, embed_dim):
    """Generate fixed sinusoidal positional encodings."""
    pe = torch.zeros(max_len, embed_dim)  # (max_len, embed_dim)
    position = torch.arange(0, max_len).unsqueeze(1).float()  # (max_len, 1)
    div_term = torch.exp(
        torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim)
    )  # (embed_dim/2,)

    pe[:, 0::2] = torch.sin(position * div_term)  # even indices
    pe[:, 1::2] = torch.cos(position * div_term)  # odd indices
    return pe  # (max_len, embed_dim)

pe = sinusoidal_positional_encoding(1024, 768)
print(f"Positional encoding shape: {pe.shape}")  # (1024, 768)
```

**Properties**: No learnable parameters, can extrapolate to longer sequences than seen during training.

### Learned Positional Embeddings — GPT-2

Simply learn a vector for each position:

```python
class LearnedPositionalEmbedding(nn.Module):
    def __init__(self, max_len, embed_dim):
        super().__init__()
        self.pos_embedding = nn.Embedding(max_len, embed_dim)

    def forward(self, seq_len):
        positions = torch.arange(seq_len, device=self.pos_embedding.weight.device)
        # positions shape: (seq_len,)
        return self.pos_embedding(positions)
        # output shape: (seq_len, embed_dim)
```

**Properties**: More expressive, but cannot generalize beyond `max_len`.

### Rotary Position Embeddings (RoPE) — LLaMA, Modern Models

RoPE encodes position by rotating the query and key vectors. It provides relative position information and extrapolates better.

The idea: rotate pairs of dimensions by an angle proportional to position.

```python
import torch

def precompute_rope_frequencies(embed_dim, max_len, base=10000.0):
    """Precompute the rotation frequencies for RoPE."""
    # Each pair of dimensions gets a different frequency
    freqs = 1.0 / (base ** (torch.arange(0, embed_dim, 2).float() / embed_dim))
    # freqs shape: (embed_dim/2,)

    positions = torch.arange(max_len).float()  # (max_len,)
    # Outer product: angle for each (position, frequency_pair)
    angles = torch.outer(positions, freqs)  # (max_len, embed_dim/2)

    # Complex representation for rotation
    cos = torch.cos(angles)  # (max_len, embed_dim/2)
    sin = torch.sin(angles)  # (max_len, embed_dim/2)
    return cos, sin

def apply_rope(x, cos, sin):
    """Apply rotary embeddings to input tensor.

    x shape: (batch_size, seq_len, n_heads, head_dim)
    """
    head_dim = x.shape[-1]
    # Split into pairs
    x1 = x[..., :head_dim // 2]  # (batch, seq, heads, head_dim/2)
    x2 = x[..., head_dim // 2:]  # (batch, seq, heads, head_dim/2)

    # Get cos/sin for current sequence length
    seq_len = x.shape[1]
    cos = cos[:seq_len].unsqueeze(0).unsqueeze(2)  # (1, seq_len, 1, head_dim/2)
    sin = sin[:seq_len].unsqueeze(0).unsqueeze(2)  # (1, seq_len, 1, head_dim/2)

    # Apply rotation: [x1, x2] -> [x1*cos - x2*sin, x1*sin + x2*cos]
    rotated = torch.cat([
        x1 * cos - x2 * sin,
        x1 * sin + x2 * cos,
    ], dim=-1)
    return rotated  # same shape as x

# Example
batch, seq_len, n_heads, head_dim = 2, 128, 12, 64
cos, sin = precompute_rope_frequencies(head_dim, max_len=2048)
x = torch.randn(batch, seq_len, n_heads, head_dim)
rotated = apply_rope(x, cos, sin)
print(f"Input: {x.shape}, Output: {rotated.shape}")
# Both: (2, 128, 12, 64)
```

**Why RoPE works**: The dot product between rotated queries and keys depends only on relative position, not absolute position. This gives the model translation-invariant attention patterns.

## Complete Embedding Layer

Combining token and positional embeddings (GPT-2 style with learned positions):

```python
import torch
import torch.nn as nn

class Embeddings(nn.Module):
    def __init__(self, vocab_size, embed_dim, max_len, dropout=0.1):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_len, embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.embed_dim = embed_dim

    def forward(self, token_ids):
        # token_ids shape: (batch_size, seq_len)
        batch_size, seq_len = token_ids.shape

        # Token embeddings
        tok_emb = self.token_embedding(token_ids)  # (batch_size, seq_len, embed_dim)

        # Position embeddings
        positions = torch.arange(seq_len, device=token_ids.device)  # (seq_len,)
        pos_emb = self.position_embedding(positions)  # (seq_len, embed_dim)

        # Combine: add token + position embeddings
        x = tok_emb + pos_emb  # (batch_size, seq_len, embed_dim)
        x = self.dropout(x)
        return x  # (batch_size, seq_len, embed_dim)

# Usage
embed_layer = Embeddings(vocab_size=50257, embed_dim=768, max_len=1024)
ids = torch.randint(0, 50257, (4, 128))  # batch of 4, seq_len 128
output = embed_layer(ids)
print(f"Embedding output: {output.shape}")  # (4, 128, 768)
```

## Embedding Dimension Choices

| Model        | Params | embed_dim | n_heads | head_dim |
| ------------ | ------ | --------- | ------- | -------- |
| GPT-2 Small  | 124M   | 768       | 12      | 64       |
| GPT-2 Medium | 355M   | 1024      | 16      | 64       |
| GPT-2 Large  | 774M   | 1280      | 20      | 64       |
| LLaMA-7B     | 7B     | 4096      | 32      | 128      |
| LLaMA-70B    | 70B    | 8192      | 64      | 128      |

The head dimension (`embed_dim / n_heads`) is typically 64 or 128. Larger models increase `embed_dim` and `n_heads` together.

## Key Takeaways

- Token embeddings are a learnable lookup table mapping IDs to vectors
- Position embeddings inject sequence order information
- Learned positions are simple but limited to max training length
- RoPE provides relative position via rotation — used in all modern LLMs
- Token + position embeddings are summed (not concatenated) to preserve dimensionality
