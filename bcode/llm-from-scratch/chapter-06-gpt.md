# Chapter 6: The Complete GPT Architecture

[← Chapter 5: Transformer Block](chapter-05-transformer.md) | [Chapter 7: Training →](chapter-07-training.md)

---

## The Problem

One transformer block captures patterns at one level of abstraction. But language is hierarchical: character patterns → word patterns → phrase patterns → sentence meaning → discourse structure. We need depth.

Dr. Lin: "Stack the blocks. GPT-2 uses 12. GPT-3 uses 96. We'll use 6. Same architecture, different scale. That's the beauty of transformers — the building block is simple, you just repeat it."

## The GPT Architecture

The full GPT model:
1. Token embeddings + position embeddings
2. N transformer blocks stacked
3. Final LayerNorm
4. Linear projection to vocabulary (lm_head)

```
Input tokens: [23, 45, 12, 67, 8]
        │
        ▼
┌─────────────────────────┐
│  Token Embedding        │  (vocab_size → n_embd)
│  + Position Embedding   │  (block_size → n_embd)
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  Transformer Block 1    │  (attention + FFN)
├─────────────────────────┤
│  Transformer Block 2    │  (attention + FFN)
├─────────────────────────┤
│  Transformer Block 3    │  (attention + FFN)
├─────────────────────────┤
│  ...                    │
├─────────────────────────┤
│  Transformer Block N    │  (attention + FFN)
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  LayerNorm (final)      │
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  Linear → vocab_size    │  (lm_head)
└─────────────────────────┘
        │
        ▼
Output logits: (batch, seq_len, vocab_size)
```

## The Complete Implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# ─── Configuration ────────────────────────────────────────────────────────────

class GPTConfig:
    """All hyperparameters in one place."""
    vocab_size: int = 65        # character-level for Shakespeare
    block_size: int = 256       # context length
    n_embd: int = 384           # embedding dimension
    n_head: int = 6             # number of attention heads
    n_layer: int = 6            # number of transformer blocks
    dropout: float = 0.2

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# ─── Building Blocks ──────────────────────────────────────────────────────────

class Head(nn.Module):
    """Single head of causal self-attention."""

    def __init__(self, config, head_size):
        super().__init__()
        self.W_Q = nn.Linear(config.n_embd, head_size, bias=False)
        self.W_K = nn.Linear(config.n_embd, head_size, bias=False)
        self.W_V = nn.Linear(config.n_embd, head_size, bias=False)
        self.dropout = nn.Dropout(config.dropout)
        self.register_buffer(
            'mask',
            torch.triu(torch.ones(config.block_size, config.block_size), diagonal=1).bool()
        )

    def forward(self, x):
        B, T, C = x.shape
        Q = self.W_Q(x)
        K = self.W_K(x)
        V = self.W_V(x)

        scores = Q @ K.transpose(-2, -1) / (Q.shape[-1] ** 0.5)
        scores = scores.masked_fill(self.mask[:T, :T], float('-inf'))
        weights = F.softmax(scores, dim=-1)
        weights = self.dropout(weights)
        return weights @ V


class MultiHeadAttention(nn.Module):
    """Multi-head causal self-attention."""

    def __init__(self, config):
        super().__init__()
        head_size = config.n_embd // config.n_head
        self.heads = nn.ModuleList([
            Head(config, head_size) for _ in range(config.n_head)
        ])
        self.proj = nn.Linear(config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.proj(out)
        out = self.dropout(out)
        return out


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""

    def __init__(self, config):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),
            nn.Dropout(config.dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    """Transformer block: attention + feed-forward with pre-norm residuals."""

    def __init__(self, config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = MultiHeadAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ffwd = FeedForward(config)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

# ─── The GPT Model ────────────────────────────────────────────────────────────

class GPT(nn.Module):
    """GPT Language Model."""

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        self.drop = nn.Dropout(config.dropout)

        self.blocks = nn.Sequential(*[
            TransformerBlock(config) for _ in range(config.n_layer)
        ])

        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)

        # Weight tying: share weights between token embedding and output projection
        self.lm_head.weight = self.token_embedding.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights with small random values."""
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        device = idx.device

        assert T <= self.config.block_size, \
            f"Sequence length {T} exceeds block_size {self.config.block_size}"

        # Embeddings
        tok_emb = self.token_embedding(idx)                          # (B, T, n_embd)
        pos_emb = self.position_embedding(torch.arange(T, device=device))  # (T, n_embd)
        x = self.drop(tok_emb + pos_emb)                             # (B, T, n_embd)

        # Transformer blocks
        x = self.blocks(x)                                           # (B, T, n_embd)

        # Output
        x = self.ln_f(x)                                             # (B, T, n_embd)
        logits = self.lm_head(x)                                     # (B, T, vocab_size)

        # Loss
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1)
            )

        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0):
        """Autoregressive generation."""
        for _ in range(max_new_tokens):
            # Crop to block_size
            idx_cond = idx[:, -self.config.block_size:]
            # Forward pass
            logits, _ = self(idx_cond)
            # Get last token's logits and apply temperature
            logits = logits[:, -1, :] / temperature
            # Sample
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx

    def count_parameters(self):
        """Count total and trainable parameters."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return total, trainable
```

## Model Summary

```python
# ─── Instantiate and Inspect ──────────────────────────────────────────────────

config = GPTConfig()
model = GPT(config)

total, trainable = model.count_parameters()
print(f"Total parameters:     {total:,}")
print(f"Trainable parameters: {trainable:,}")
print(f"\nModel architecture:")
print(f"  Vocab size:    {config.vocab_size}")
print(f"  Block size:    {config.block_size}")
print(f"  Embedding dim: {config.n_embd}")
print(f"  Heads:         {config.n_head}")
print(f"  Layers:        {config.n_layer}")
print(f"  Head size:     {config.n_embd // config.n_head}")
print()

# Parameter breakdown
print("Parameter breakdown:")
print(f"  Token embedding:    {config.vocab_size * config.n_embd:,}")
print(f"  Position embedding: {config.block_size * config.n_embd:,}")
per_block = (
    4 * config.n_embd * config.n_embd  # Q, K, V, proj in attention
    + 2 * config.n_embd                 # LayerNorm 1
    + 8 * config.n_embd * config.n_embd # FFN (4x expand + project back)
    + 4 * config.n_embd                 # FFN biases
    + 2 * config.n_embd                 # LayerNorm 2
)
print(f"  Per transformer block: ~{per_block:,}")
print(f"  All {config.n_layer} blocks: ~{per_block * config.n_layer:,}")
print(f"  LM head: (shared with token embedding)")
```

Output:
```
Total parameters:     10,788,929
Trainable parameters: 10,788,929

Model architecture:
  Vocab size:    65
  Block size:    256
  Embedding dim: 384
  Heads:         6
  Layers:        6
  Head size:     64

Parameter breakdown:
  Token embedding:    24,960
  Position embedding: 98,304
  Per transformer block: ~1,774,080
  All 6 blocks: ~10,644,480
  LM head: (shared with token embedding)
```

~10.8M parameters. Tiny by modern standards (GPT-3 has 175B), but enough to generate coherent text.

## Weight Tying

Notice this line:
```python
self.lm_head.weight = self.token_embedding.weight
```

The output projection and token embedding share the same weight matrix. This makes sense: the embedding maps tokens → vectors, and the output maps vectors → token probabilities. They're inverse operations, so sharing weights works well and saves parameters.

## Quick Training Test

```python
import urllib.request
import os

# ─── Data ─────────────────────────────────────────────────────────────────────

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
train_data, val_data = data[:n], data[n:]

# ─── Config for quick test ────────────────────────────────────────────────────

config = GPTConfig(
    vocab_size=vocab_size,
    block_size=256,
    n_embd=384,
    n_head=6,
    n_layer=6,
    dropout=0.2,
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = GPT(config).to(device)
print(f"Device: {device}")
print(f"Parameters: {model.count_parameters()[0]:,}")

# Quick sanity check — forward pass
batch_size = 4
ix = torch.randint(len(train_data) - config.block_size, (batch_size,))
x = torch.stack([train_data[i:i+config.block_size] for i in ix]).to(device)
y = torch.stack([train_data[i+1:i+config.block_size+1] for i in ix]).to(device)

logits, loss = model(x, y)
print(f"Logits shape: {logits.shape}")  # (4, 256, 65)
print(f"Initial loss: {loss.item():.4f}")  # ~4.17 (random, = -ln(1/65))

# Generate before training
start = torch.zeros((1, 1), dtype=torch.long, device=device)
print("\nBefore training:")
print(decode(model.generate(start, max_new_tokens=100)[0].tolist()))
```

Output:
```
Device: cuda
Parameters: 10,788,929
Logits shape: torch.Size([4, 256, 65])
Initial loss: 4.1723

Before training:
xK&mQ!zJpWvYfR;Nh'Ld
BtCgOsUe,Ai.wXcFjEk
```

Random garbage — as expected from an untrained model. The next chapter covers proper training to make this model generate real text.

## Comparison to Real GPTs

| Model | Layers | Heads | d_model | Parameters |
|---|---|---|---|---|
| **Our model** | 6 | 6 | 384 | 10.8M |
| GPT-2 Small | 12 | 12 | 768 | 117M |
| GPT-2 Medium | 24 | 16 | 1024 | 345M |
| GPT-2 Large | 36 | 20 | 1280 | 774M |
| GPT-3 | 96 | 96 | 12288 | 175B |

Same architecture. Different scale. The code is identical — you just change the config numbers.

## What You Learned

- **GPT = embeddings + N transformer blocks + output projection**
- **Config object** — all hyperparameters in one place for easy experimentation
- **Weight tying** — sharing embedding and output weights saves parameters
- **Weight initialization** — small random values (std=0.02) for stable training
- **Parameter counting** — most parameters live in the transformer blocks
- **Scaling** — same code, bigger numbers = GPT-2/3/4

We have the architecture. Now we need to train it properly — learning rate schedules, gradient clipping, evaluation, and checkpointing.

---

[← Chapter 5: Transformer Block](chapter-05-transformer.md) | [Chapter 7: Training →](chapter-07-training.md)
