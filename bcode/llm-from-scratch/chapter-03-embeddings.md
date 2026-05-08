# Chapter 3: Embeddings — Giving Tokens Meaning

[← Chapter 2: Bigrams](chapter-02-bigrams.md) | [Chapter 4: Attention →](chapter-04-attention.md)

---

## The Problem

The bigram model maps each token directly to logits — a flat lookup table. Token 23 has no relationship to token 24. The letter 'a' has no connection to 'A'. There's no concept of similarity, no shared structure.

Kai: "Your bigram model treats every character as equally different from every other character. 'a' is as far from 'b' as it is from 'Z'. That's insane. We need tokens to live in a space where similar things are close together."

## What Are Embeddings?

An embedding maps discrete tokens into continuous vector space. Instead of token 23 being just the number 23, it becomes a vector like `[0.12, -0.34, 0.78, ...]`.

Why this helps:
- **Similar tokens get similar vectors** — 'a' and 'e' (both vowels) end up nearby
- **Relationships become directions** — the vector from 'a' to 'A' is similar to 'b' to 'B'
- **The model can generalize** — learning something about 'cat' helps with 'bat'

```
Token space (discrete):     Embedding space (continuous):
  0: '\n'                     [0.1, -0.2, 0.5, ...]
  1: ' '                      [0.3,  0.1, 0.4, ...]
  2: '!'                      [-0.1, 0.8, 0.2, ...]
  ...                         ...
  64: 'z'                     [0.7, -0.3, 0.1, ...]
```

## Token Embeddings

```python
import torch
import torch.nn as nn

vocab_size = 65    # number of unique tokens
n_embd = 32       # embedding dimension (a hyperparameter)

# The embedding layer: a learnable lookup table
token_embedding = nn.Embedding(vocab_size, n_embd)

# Look up embeddings for a sequence
tokens = torch.tensor([20, 43, 50, 50, 53])  # "hello" in our encoding
embedded = token_embedding(tokens)

print(f"Input shape:  {tokens.shape}")       # (5,)
print(f"Output shape: {embedded.shape}")     # (5, 32)
print(f"Each token is now a {n_embd}-dimensional vector")
```

Under the hood, `nn.Embedding` is just a matrix of shape `(vocab_size, n_embd)`. Looking up token `i` returns row `i` of the matrix. These rows are learned during training.

## Position Embeddings

Here's a problem: if we just embed tokens, the model doesn't know **where** they are in the sequence.

```
"cat sat" → embeddings of [c, a, t, ' ', s, a, t]
```

The two 'a' tokens get the **same** embedding, even though one is in "cat" and the other in "sat". The model can't tell position 2 from position 5.

Solution: **add** a position embedding to each token embedding.

```python
block_size = 8  # maximum sequence length

# Position embedding: one vector per position
position_embedding = nn.Embedding(block_size, n_embd)

# For a sequence of length T:
T = 5
positions = torch.arange(T)  # [0, 1, 2, 3, 4]
pos_emb = position_embedding(positions)  # (T, n_embd)

# Combined embedding = token embedding + position embedding
tok_emb = token_embedding(tokens)  # (T, n_embd)
x = tok_emb + pos_emb              # (T, n_embd) — element-wise addition

print(f"Token embedding shape:    {tok_emb.shape}")   # (5, 32)
print(f"Position embedding shape: {pos_emb.shape}")   # (5, 32)
print(f"Combined shape:           {x.shape}")         # (5, 32)
```

Now the same token 'a' at position 2 and position 5 gets different combined embeddings. The model knows where each token sits.

## Why Addition Works

Adding embeddings seems weird — why not concatenate? Two reasons:

1. **Efficiency** — addition keeps the dimension at `n_embd`, concatenation doubles it
2. **It works** — the model learns to use different dimensions for token identity vs. position

Think of it like coordinates: token embedding says "what am I?" and position embedding says "where am I?" The model learns to read both signals from the combined vector.

## The Embedding Model

Let's upgrade our bigram model to use proper embeddings:

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
block_size = 8
n_embd = 32
max_iters = 5000
learning_rate = 1e-3
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def get_batch(split):
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - block_size, (batch_size,))
    x = torch.stack([d[i:i+block_size] for i in ix]).to(device)
    y = torch.stack([d[i+1:i+block_size+1] for i in ix]).to(device)
    return x, y

# ─── Model with Embeddings ───────────────────────────────────────────────────

class EmbeddingLanguageModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)  # project back to vocab

    def forward(self, idx, targets=None):
        B, T = idx.shape

        tok_emb = self.token_embedding(idx)          # (B, T, n_embd)
        pos_emb = self.position_embedding(torch.arange(T, device=device))  # (T, n_embd)
        x = tok_emb + pos_emb                        # (B, T, n_embd)
        logits = self.lm_head(x)                     # (B, T, vocab_size)

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T))

        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            # Crop to block_size (position embedding only goes up to block_size)
            idx_cond = idx[:, -block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx

model = EmbeddingLanguageModel().to(device)
params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {params:,}")
# token_emb: 65×32=2080, pos_emb: 8×32=256, lm_head: 32×65+65=2145
# Total: ~4,481

# ─── Training ─────────────────────────────────────────────────────────────────

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

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
Step     0 | Loss: 4.4321
Step  1000 | Loss: 2.5678
Step  2000 | Loss: 2.4912
Step  3000 | Loss: 2.4756
Step  4000 | Loss: 2.4601

--- Generated Text ---

Whe fath my bour
Thend, ise t hou wis
And mee the lat
```

## Wait — It's Not Much Better?

The loss is similar to the bigram model (~2.47 vs ~2.47). Why?

Because **embeddings alone don't help if the model can't use context**. Our `lm_head` linear layer processes each position independently. Token at position 3 can't see tokens at positions 0, 1, 2.

The embeddings give us a richer representation, but we need a mechanism to **mix information between positions**. That mechanism is attention.

Think of it this way:
- **Bigram**: each token predicts the next in isolation
- **Embedding model**: each token has a richer representation, but still predicts in isolation
- **Attention** (next chapter): tokens can look at each other and share information

The embeddings are the foundation. Attention is the mechanism that makes them useful.

## Visualizing Embeddings

After training, similar characters end up with similar embeddings:

```python
# After training, check embedding similarity
emb_weights = model.token_embedding.weight.detach()

# Cosine similarity between 'a' and 'e' (both vowels)
a_emb = emb_weights[char_to_idx['a']]
e_emb = emb_weights[char_to_idx['e']]
sim_vowels = F.cosine_similarity(a_emb.unsqueeze(0), e_emb.unsqueeze(0))

# Cosine similarity between 'a' and 'Z' (very different)
z_emb = emb_weights[char_to_idx['Z']]
sim_diff = F.cosine_similarity(a_emb.unsqueeze(0), z_emb.unsqueeze(0))

print(f"Similarity('a', 'e'): {sim_vowels.item():.3f}")  # Higher
print(f"Similarity('a', 'Z'): {sim_diff.item():.3f}")    # Lower
```

The model discovers structure in the data without being told. Vowels cluster together. Consonants cluster together. Uppercase letters form their own group.

## What You Learned

- **Token embeddings** — map discrete tokens to continuous vectors via `nn.Embedding`
- **Position embeddings** — encode where each token sits in the sequence
- **Addition** — token + position embeddings combine identity and location
- **The gap** — embeddings alone don't help without a way to mix information across positions
- **The setup** — we now have rich token representations ready for attention

We have meaningful vectors for each token. But each token is still isolated — it can't see its neighbors. The next chapter introduces the mechanism that changes everything: self-attention.

---

[← Chapter 2: Bigrams](chapter-02-bigrams.md) | [Chapter 4: Attention →](chapter-04-attention.md)
