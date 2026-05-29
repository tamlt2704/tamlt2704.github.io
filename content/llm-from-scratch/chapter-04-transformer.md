# Chapter 4: Transformer Block

[prev: Attention](chapter-03-attention.md) | [next: Training](chapter-05-training.md)

The transformer block combines attention with a feed-forward network, connected by residual connections and layer normalization. Stack N of these blocks to build a GPT.

## Layer Normalization

Normalizes across the feature dimension (not the batch dimension like BatchNorm):

`LayerNorm(x) = gamma * (x - mean) / sqrt(variance + eps) + beta`

```python
import torch
import torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self, embed_dim, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(embed_dim))
        self.beta = nn.Parameter(torch.zeros(embed_dim))

    def forward(self, x):
        # x shape: (batch, seq_len, embed_dim)
        mean = x.mean(dim=-1, keepdim=True)    # (batch, seq_len, 1)
        var = x.var(dim=-1, keepdim=True, unbiased=False)  # (batch, seq_len, 1)
        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta
        # output shape: (batch, seq_len, embed_dim)
```

### Pre-Norm vs Post-Norm

- **Post-Norm** (original transformer): `x + Sublayer(LayerNorm(x))` — no, actually: `LayerNorm(x + Sublayer(x))`
- **Pre-Norm** (GPT-2, modern): `x + Sublayer(LayerNorm(x))`

Pre-norm is more stable during training (gradients flow directly through residual path).

## Feed-Forward Network (MLP with GELU)

A two-layer MLP that expands then contracts the representation:

```python
import torch
import torch.nn as nn

class FeedForward(nn.Module):
    def __init__(self, embed_dim, expansion_factor=4, dropout=0.1):
        super().__init__()
        hidden_dim = embed_dim * expansion_factor
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)
        self.gelu = nn.GELU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # x shape: (batch, seq_len, embed_dim)
        x = self.fc1(x)      # (batch, seq_len, hidden_dim)
        x = self.gelu(x)     # (batch, seq_len, hidden_dim)
        x = self.fc2(x)      # (batch, seq_len, embed_dim)
        x = self.dropout(x)
        return x              # (batch, seq_len, embed_dim)
```

**Why GELU over ReLU?** GELU is smoother — it does not have a hard zero cutoff. It slightly outperforms ReLU in practice for language models.

## Residual Connections

Residual connections let gradients flow directly through the network:

`output = x + Sublayer(x)`

Without residuals, deep networks suffer from vanishing gradients. With residuals, even a 96-layer model trains stably.

## Full Transformer Block

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
        mask = torch.tril(torch.ones(max_len, max_len))
        self.register_buffer("mask", mask.view(1, 1, max_len, max_len))

    def forward(self, x):
        batch, seq_len, embed_dim = x.shape
        qkv = self.W_qkv(x).reshape(batch, seq_len, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]
        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.head_dim)
        scores = scores.masked_fill(self.mask[:,:,:seq_len,:seq_len] == 0, float('-inf'))
        weights = self.attn_dropout(torch.softmax(scores, dim=-1))
        out = (weights @ V).transpose(1, 2).reshape(batch, seq_len, embed_dim)
        return self.resid_dropout(self.W_out(out))


class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, n_heads, max_len=1024, dropout=0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(embed_dim)
        self.attn = CausalSelfAttention(embed_dim, n_heads, max_len, dropout)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.ffn = FeedForward(embed_dim, dropout=dropout)

    def forward(self, x):
        # x shape: (batch, seq_len, embed_dim)
        # Pre-norm + residual for attention
        x = x + self.attn(self.ln1(x))
        # Pre-norm + residual for FFN
        x = x + self.ffn(self.ln2(x))
        return x  # (batch, seq_len, embed_dim)

# Test
block = TransformerBlock(embed_dim=768, n_heads=12)
x = torch.randn(2, 128, 768)  # batch=2, seq_len=128
out = block(x)
print(f"Block output: {out.shape}")  # (2, 128, 768)
```

## Stacking N Blocks: The Full GPT Model

```python
import torch
import torch.nn as nn

class GPT(nn.Module):
    def __init__(self, vocab_size=50257, embed_dim=768, n_heads=12,
                 n_layers=12, max_len=1024, dropout=0.1):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, embed_dim)
        self.pos_emb = nn.Embedding(max_len, embed_dim)
        self.dropout = nn.Dropout(dropout)

        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, n_heads, max_len, dropout)
            for _ in range(n_layers)
        ])

        self.ln_final = nn.LayerNorm(embed_dim)
        self.lm_head = nn.Linear(embed_dim, vocab_size, bias=False)

        # Weight tying: share embedding and output weights
        self.lm_head.weight = self.token_emb.weight

    def forward(self, token_ids):
        # token_ids shape: (batch, seq_len)
        batch, seq_len = token_ids.shape

        tok_emb = self.token_emb(token_ids)  # (batch, seq_len, embed_dim)
        pos = torch.arange(seq_len, device=token_ids.device)
        pos_emb = self.pos_emb(pos)          # (seq_len, embed_dim)

        x = self.dropout(tok_emb + pos_emb)  # (batch, seq_len, embed_dim)

        for block in self.blocks:
            x = block(x)                     # (batch, seq_len, embed_dim)

        x = self.ln_final(x)                 # (batch, seq_len, embed_dim)
        logits = self.lm_head(x)             # (batch, seq_len, vocab_size)
        return logits

# Test
model = GPT(vocab_size=50257, embed_dim=768, n_heads=12, n_layers=12)
ids = torch.randint(0, 50257, (2, 128))
logits = model(ids)
print(f"Logits shape: {logits.shape}")  # (2, 128, 50257)

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params / 1e6:.1f}M")  # ~124M
```

## GPT Architecture Diagram

```
Input token IDs: (batch, seq_len)
         |
    Token Embedding + Position Embedding
         |
    Dropout
         |
    +--------------------------+
    |   Transformer Block x N  |
    |                          |
    |   LayerNorm              |
    |       |                  |
    |   Causal Self-Attention  |
    |       |                  |
    |   + Residual             |
    |       |                  |
    |   LayerNorm              |
    |       |                  |
    |   Feed-Forward (MLP)     |
    |       |                  |
    |   + Residual             |
    +--------------------------+
         |
    Final LayerNorm
         |
    Linear Head (embed_dim -> vocab_size)
         |
    Logits: (batch, seq_len, vocab_size)
```

## Dropout Placement

Dropout is applied at three points:

1. After embedding sum (before first block)
2. After attention output projection
3. After FFN output

During inference, dropout is disabled (`model.eval()`).

## Key Takeaways

- Pre-norm (LayerNorm before sublayer) is more stable than post-norm
- FFN expands to 4x embed_dim then contracts back — this is where "memory" is stored
- Residual connections are essential for training deep networks
- Weight tying between embedding and output head reduces parameters
- GPT-2 Small: 12 layers, 12 heads, 768 embed_dim = 124M parameters
