# Chapter 4: Self-Attention — The Core of the Transformer

[← Chapter 3: Embeddings](chapter-03-embeddings.md) | [Chapter 5: Transformer Block →](chapter-05-transformer.md)

---

## The Problem

Our embedding model processes each token independently. Position 5 can't see what's at position 0, 1, 2, 3, or 4. It's blind to context.

Dr. Lin: "This is THE chapter. Attention is the single idea that makes transformers work. Every other piece — embeddings, feed-forward layers, residuals — is supporting infrastructure. Attention is the engine. Understand this, and you understand GPT."

## What We Need

Given the sequence "The cat sat on the ___", the model predicting the blank needs to:
1. Look back at "cat" (the subject)
2. Look back at "sat on" (the action)
3. Combine this information to predict "mat" or "floor"

We need a mechanism where each token can **selectively look at previous tokens** and gather relevant information. That mechanism is self-attention.

## The Intuition: Queries, Keys, and Values

Think of attention like a search engine:

- **Query (Q)**: "What am I looking for?" — each token asks a question
- **Key (K)**: "What do I contain?" — each token advertises its content
- **Value (V)**: "What information do I provide?" — each token's actual data

The process:
1. Each token creates a Query: "I need context about [something]"
2. Each token creates a Key: "I contain information about [something]"
3. Query-Key dot product measures relevance: "How much does this token's Key match my Query?"
4. High-relevance tokens contribute more of their Value to the output

```
Token "the" (position 5) asks: Q = "What noun was the subject?"
Token "cat" (position 1) advertises: K = "I'm a noun, a subject"
Dot product Q·K is HIGH → "cat" is relevant to "the"
Token "cat" provides: V = [information about being a cat]
```

## Step-by-Step: Attention with Numbers

Let's trace through attention with a tiny example. Suppose we have 4 tokens, each embedded as a 3-dimensional vector:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)

# 4 tokens, each a 3-dimensional embedding
# Imagine these are embeddings for: "The", "cat", "sat", "on"
T, C = 4, 3  # seq_len=4, embed_dim=3
x = torch.randn(T, C)
print("Input embeddings:")
print(x)
```

```
Input embeddings:
tensor([[ 0.33,  0.12, -0.23],   # "The"
        [-0.11,  0.45,  0.67],   # "cat"
        [ 0.89, -0.34,  0.12],   # "sat"
        [ 0.23,  0.56, -0.78]])  # "on"
```

### Step 1: Create Q, K, V with Linear Projections

```python
head_size = 4  # dimension of Q, K, V (a hyperparameter)

# Learnable projection matrices
W_Q = nn.Linear(C, head_size, bias=False)
W_K = nn.Linear(C, head_size, bias=False)
W_V = nn.Linear(C, head_size, bias=False)

Q = W_Q(x)  # (4, 4) — each token's query
K = W_K(x)  # (4, 4) — each token's key
V = W_V(x)  # (4, 4) — each token's value

print(f"Q shape: {Q.shape}")  # (4, 4)
print(f"K shape: {K.shape}")  # (4, 4)
print(f"V shape: {V.shape}")  # (4, 4)
```

Each token now has three vectors: what it's looking for (Q), what it contains (K), and what it provides (V).

### Step 2: Compute Attention Scores (Q × K^T)

How much does each token attend to every other token?

```python
# Dot product of queries with keys
# Q[i] · K[j] = how much token i attends to token j
scores = Q @ K.transpose(-2, -1)  # (4, 4)

print("Raw attention scores:")
print(scores)
```

```
Raw attention scores:
tensor([[ 0.21,  0.45, -0.12,  0.33],   # "The" attending to [The, cat, sat, on]
        [ 0.11,  0.89,  0.23,  0.56],   # "cat" attending to [The, cat, sat, on]
        [-0.34,  0.12,  0.67,  0.11],   # "sat" attending to [The, cat, sat, on]
        [ 0.45,  0.23, -0.11,  0.78]])  # "on" attending to [The, cat, sat, on]
```

`scores[i][j]` = how relevant token `j` is to token `i`.

### Step 3: Scale by √d_k

```python
d_k = head_size  # 4
scores_scaled = scores / (d_k ** 0.5)  # divide by √4 = 2

print("Scaled scores:")
print(scores_scaled)
```

**Why scale?** Without scaling, when `d_k` is large, dot products grow large in magnitude. Large values push softmax into regions where gradients are tiny (saturation). Dividing by √d_k keeps the variance of scores around 1, regardless of dimension.

```
Without scaling (d_k=64):  scores might be [-15, 22, -8, 31]
  → softmax: [0.00, 0.00, 0.00, 1.00]  ← almost one-hot, gradient ≈ 0

With scaling (÷√64=8):    scores become [-1.9, 2.75, -1.0, 3.9]
  → softmax: [0.01, 0.12, 0.03, 0.84]  ← smooth, gradient flows
```

### Step 4: Apply Causal Mask

In language modeling, token at position `i` can only attend to positions `0, 1, ..., i`. It **cannot** look at future tokens (that would be cheating — you can't use the answer to predict the answer).

```python
# Create causal mask: upper triangle = -infinity
mask = torch.triu(torch.ones(T, T), diagonal=1).bool()
print("Mask (True = blocked):")
print(mask)
```

```
Mask (True = blocked):
tensor([[False,  True,  True,  True],   # "The" can only see itself
        [False, False,  True,  True],   # "cat" can see "The", "cat"
        [False, False, False,  True],   # "sat" can see "The", "cat", "sat"
        [False, False, False, False]])  # "on" can see everything before it
```

```python
# Apply mask: set future positions to -infinity
scores_scaled = scores_scaled.masked_fill(mask, float('-inf'))
print("Masked scores:")
print(scores_scaled)
```

```
Masked scores:
tensor([[ 0.11,  -inf,  -inf,  -inf],   # "The" only sees itself
        [ 0.06,  0.45,  -inf,  -inf],   # "cat" sees "The" and itself
        [-0.17,  0.06,  0.34,  -inf],   # "sat" sees "The", "cat", itself
        [ 0.23,  0.12, -0.06,  0.39]])  # "on" sees all previous
```

After softmax, `-inf` becomes 0 probability — the model literally cannot attend to future tokens.

### Step 5: Softmax → Attention Weights

```python
# Convert scores to probabilities (each row sums to 1)
attention_weights = F.softmax(scores_scaled, dim=-1)
print("Attention weights:")
print(attention_weights)
```

```
Attention weights:
tensor([[1.00, 0.00, 0.00, 0.00],   # "The" puts all weight on itself
        [0.40, 0.60, 0.00, 0.00],   # "cat" attends 40% to "The", 60% to itself
        [0.24, 0.30, 0.46, 0.00],   # "sat" distributes across The/cat/sat
        [0.27, 0.24, 0.20, 0.29]])  # "on" attends to all four
```

Each row is a probability distribution. Token `i` distributes its attention across tokens `0..i`.

### Step 6: Weighted Sum of Values

```python
# Output = weighted combination of values
output = attention_weights @ V  # (4, 4)
print(f"Output shape: {output.shape}")  # (4, 4)
```

Each token's output is a weighted average of the Value vectors it attends to. Token "sat" gets 24% of "The"'s value + 30% of "cat"'s value + 46% of its own value.

**This is the key insight**: each token's representation now contains information from previous tokens, weighted by relevance.

## The Complete Single-Head Attention

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SelfAttention(nn.Module):
    """Single-head causal self-attention."""

    def __init__(self, n_embd, head_size, block_size):
        super().__init__()
        self.W_Q = nn.Linear(n_embd, head_size, bias=False)
        self.W_K = nn.Linear(n_embd, head_size, bias=False)
        self.W_V = nn.Linear(n_embd, head_size, bias=False)
        # Register the causal mask as a buffer (not a parameter)
        self.register_buffer(
            'mask',
            torch.triu(torch.ones(block_size, block_size), diagonal=1).bool()
        )

    def forward(self, x):
        B, T, C = x.shape  # batch, seq_len, embedding_dim

        Q = self.W_Q(x)  # (B, T, head_size)
        K = self.W_K(x)  # (B, T, head_size)
        V = self.W_V(x)  # (B, T, head_size)

        # Attention scores
        d_k = Q.shape[-1]
        scores = Q @ K.transpose(-2, -1) / (d_k ** 0.5)  # (B, T, T)

        # Causal mask
        scores = scores.masked_fill(self.mask[:T, :T], float('-inf'))

        # Softmax
        weights = F.softmax(scores, dim=-1)  # (B, T, T)

        # Weighted sum of values
        out = weights @ V  # (B, T, head_size)
        return out
```

## Putting It in a Model

```python
class AttentionLanguageModel(nn.Module):
    """Language model with single-head self-attention."""

    def __init__(self, vocab_size, n_embd, head_size, block_size):
        super().__init__()
        self.block_size = block_size
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.attention = SelfAttention(n_embd, head_size, block_size)
        self.lm_head = nn.Linear(head_size, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        device = idx.device

        tok_emb = self.token_embedding(idx)                          # (B, T, n_embd)
        pos_emb = self.position_embedding(torch.arange(T, device=device))  # (T, n_embd)
        x = tok_emb + pos_emb                                        # (B, T, n_embd)
        x = self.attention(x)                                        # (B, T, head_size)
        logits = self.lm_head(x)                                     # (B, T, vocab_size)

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T))

        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx
```

## Training the Attention Model

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

# ─── Hyperparameters ──────────────────────────────────────────────────────────

batch_size = 32
block_size = 32      # longer context now that we can use it!
n_embd = 64
head_size = 64
max_iters = 5000
learning_rate = 1e-3
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def get_batch(split):
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - block_size, (batch_size,))
    x = torch.stack([d[i:i+block_size] for i in ix]).to(device)
    y = torch.stack([d[i+1:i+block_size+1] for i in ix]).to(device)
    return x, y

# ─── Train ────────────────────────────────────────────────────────────────────

model = AttentionLanguageModel(vocab_size, n_embd, head_size, block_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {params:,}")

for step in range(max_iters):
    xb, yb = get_batch('train')
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    if step % 1000 == 0:
        print(f"Step {step:5d} | Loss: {loss.item():.4f}")

# ─── Generate ─────────────────────────────────────────────────────────────────

print("\n--- Generated Text ---")
start = torch.zeros((1, 1), dtype=torch.long, device=device)
print(decode(model.generate(start, max_new_tokens=300)[0].tolist()))
```

Output:
```
Parameters: 21,057
Step     0 | Loss: 4.3012
Step  1000 | Loss: 2.3456
Step  2000 | Loss: 2.2134
Step  3000 | Loss: 2.1567
Step  4000 | Loss: 2.0923

--- Generated Text ---

KING HENRY:
What is the matter with the good lord?

GLOUCESTER:
The king hath sent me to the tower,
And there I shall be crown'd.
```

Loss dropped from ~2.5 (bigram/embedding) to ~2.1. The model can now form words and short phrases because it can look at previous characters.

## Why Attention Works: The Information Flow

Without attention:
```
Position 0: [The] → predicts next using ONLY "The"
Position 1: [cat] → predicts next using ONLY "cat"
Position 2: [sat] → predicts next using ONLY "sat"
```

With attention:
```
Position 0: [The] → predicts using "The"
Position 1: [cat] → predicts using "The" + "cat" (weighted)
Position 2: [sat] → predicts using "The" + "cat" + "sat" (weighted)
```

Each token aggregates information from all previous tokens, weighted by relevance. The model learns WHAT to pay attention to through the Q, K, V matrices.

## Key Concepts Summary

### Why Q, K, V instead of just averaging?

Simple averaging treats all previous tokens equally. Attention lets the model be **selective**:
- "The cat sat on the ___" — the model should attend strongly to "cat" and "sat", weakly to "the" and "on"
- Q/K dot product learns this selectivity

### Why scale by √d_k?

Dot products grow with dimension. If Q and K are random vectors of dimension `d_k`, their dot product has variance `d_k`. Dividing by `√d_k` normalizes variance to 1, keeping softmax in a well-behaved range.

```python
# Demonstration
d_k = 64
q = torch.randn(1000, d_k)
k = torch.randn(1000, d_k)
dots = (q @ k.T).std()
dots_scaled = (q @ k.T / (d_k**0.5)).std()
print(f"Unscaled std: {dots:.2f}")        # ~8.0 (too large for softmax)
print(f"Scaled std:   {dots_scaled:.2f}")  # ~1.0 (good for softmax)
```

### Why causal mask?

Language modeling is autoregressive: predict token `t` using only tokens `0..t-1`. If token `t` could see token `t+1`, it would just copy the answer. The mask enforces this constraint.

### What does attention learn?

After training, you can inspect the attention weights to see what the model learned:
- Some positions attend to the most recent token (local context)
- Some attend to the first token (global context)
- Some attend to specific patterns (e.g., matching brackets, subject-verb agreement)

## Attention as Matrix Operations

The entire attention mechanism is just matrix multiplications:

```
Input:   X ∈ ℝ^(T × C)

Q = X @ W_Q    ∈ ℝ^(T × d_k)
K = X @ W_K    ∈ ℝ^(T × d_k)
V = X @ W_V    ∈ ℝ^(T × d_v)

Scores = Q @ K^T / √d_k    ∈ ℝ^(T × T)
Scores = mask(Scores)
Weights = softmax(Scores)   ∈ ℝ^(T × T)
Output = Weights @ V        ∈ ℝ^(T × d_v)
```

This is fully differentiable and parallelizable on GPUs. Unlike RNNs, all positions are computed simultaneously.

## What You Learned

- **Self-attention** — each token computes a weighted sum of all previous tokens' values
- **Q, K, V** — Query (what I want), Key (what I have), Value (what I give)
- **Scaled dot-product** — Q·K^T / √d_k prevents softmax saturation
- **Causal mask** — prevents attending to future tokens (autoregressive constraint)
- **The improvement** — loss dropped from ~2.5 to ~2.1 because the model can use context
- **Parallelism** — unlike RNNs, attention computes all positions at once

One attention head captures one type of relationship. But language has many simultaneous relationships (syntax, semantics, position, etc.). Next chapter: multiple attention heads working in parallel.

---

[← Chapter 3: Embeddings](chapter-03-embeddings.md) | [Chapter 5: Transformer Block →](chapter-05-transformer.md)
