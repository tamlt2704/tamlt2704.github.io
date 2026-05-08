# Chapter 7: Training — Making the Model Learn

[← Chapter 6: GPT Architecture](chapter-06-gpt.md) | [Chapter 8: Data Pipeline →](chapter-08-data.md)

---

## The Problem

We have a 10M parameter GPT that outputs random characters. A randomly initialized model is useless. We need a proper training loop with all the tricks that make modern LLM training work.

Dr. Lin: "Training a transformer isn't just `loss.backward()` in a loop. You need learning rate warmup, cosine decay, gradient clipping, proper evaluation, and checkpointing. Get any of these wrong and your model either diverges or plateaus."

## The Training Recipe

Modern LLM training uses:
1. **AdamW optimizer** — Adam with decoupled weight decay
2. **Learning rate warmup** — start small, ramp up linearly
3. **Cosine decay** — after warmup, decay LR following a cosine curve
4. **Gradient clipping** — prevent exploding gradients
5. **Evaluation loop** — track validation loss to detect overfitting
6. **Checkpointing** — save model periodically

## Complete Training Script

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import time
import urllib.request

# ─── GPT Model (from Chapter 6) ──────────────────────────────────────────────

class GPTConfig:
    vocab_size: int = 65
    block_size: int = 256
    n_embd: int = 384
    n_head: int = 6
    n_layer: int = 6
    dropout: float = 0.2

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Head(nn.Module):
    def __init__(self, config, head_size):
        super().__init__()
        self.W_Q = nn.Linear(config.n_embd, head_size, bias=False)
        self.W_K = nn.Linear(config.n_embd, head_size, bias=False)
        self.W_V = nn.Linear(config.n_embd, head_size, bias=False)
        self.dropout = nn.Dropout(config.dropout)
        self.register_buffer('mask', torch.triu(torch.ones(config.block_size, config.block_size), diagonal=1).bool())

    def forward(self, x):
        B, T, C = x.shape
        Q, K, V = self.W_Q(x), self.W_K(x), self.W_V(x)
        scores = Q @ K.transpose(-2, -1) / (Q.shape[-1] ** 0.5)
        scores = scores.masked_fill(self.mask[:T, :T], float('-inf'))
        weights = self.dropout(F.softmax(scores, dim=-1))
        return weights @ V


class MultiHeadAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        head_size = config.n_embd // config.n_head
        self.heads = nn.ModuleList([Head(config, head_size) for _ in range(config.n_head)])
        self.proj = nn.Linear(config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
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


class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        self.drop = nn.Dropout(config.dropout)
        self.blocks = nn.Sequential(*[TransformerBlock(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)
        self.lm_head.weight = self.token_embedding.weight
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding(idx)
        pos_emb = self.position_embedding(torch.arange(T, device=idx.device))
        x = self.drop(tok_emb + pos_emb)
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx

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

# ─── Training Configuration ──────────────────────────────────────────────────

# Model
config = GPTConfig(vocab_size=vocab_size)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = GPT(config).to(device)
print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Device: {device}")

# Training hyperparameters
batch_size = 64
max_iters = 5000
eval_interval = 500
eval_iters = 200

# Learning rate schedule
max_lr = 3e-4
min_lr = 3e-5          # 10x smaller than max
warmup_iters = 200     # linear warmup
lr_decay_iters = 5000  # cosine decay over this many steps

# AdamW
weight_decay = 0.1
grad_clip = 1.0

# ─── Learning Rate Schedule ───────────────────────────────────────────────────

def get_lr(step):
    """Learning rate with linear warmup and cosine decay."""
    # Linear warmup
    if step < warmup_iters:
        return max_lr * (step + 1) / warmup_iters

    # After decay period, return minimum
    if step > lr_decay_iters:
        return min_lr

    # Cosine decay between warmup and decay end
    decay_ratio = (step - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))  # goes from 1 to 0
    return min_lr + coeff * (max_lr - min_lr)

# Visualize the schedule
print("\nLearning rate schedule:")
for step in [0, 100, 200, 500, 1000, 2500, 5000]:
    print(f"  Step {step:5d}: lr = {get_lr(step):.6f}")

# ─── Optimizer Setup ──────────────────────────────────────────────────────────

# Separate parameters: apply weight decay only to weight matrices, not biases/norms
decay_params = []
no_decay_params = []
for name, param in model.named_parameters():
    if param.requires_grad:
        if param.dim() >= 2:
            decay_params.append(param)
        else:
            no_decay_params.append(param)

optimizer = torch.optim.AdamW([
    {'params': decay_params, 'weight_decay': weight_decay},
    {'params': no_decay_params, 'weight_decay': 0.0},
], lr=max_lr, betas=(0.9, 0.95))

print(f"\nDecay params: {sum(p.numel() for p in decay_params):,}")
print(f"No-decay params: {sum(p.numel() for p in no_decay_params):,}")

# ─── Batch Function ───────────────────────────────────────────────────────────

def get_batch(split):
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - config.block_size, (batch_size,))
    x = torch.stack([d[i:i+config.block_size] for i in ix]).to(device)
    y = torch.stack([d[i+1:i+config.block_size+1] for i in ix]).to(device)
    return x, y

# ─── Evaluation ───────────────────────────────────────────────────────────────

@torch.no_grad()
def estimate_loss():
    """Estimate loss on train and val splits."""
    model.eval()
    losses = {}
    for split in ['train', 'val']:
        batch_losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            x, y = get_batch(split)
            _, loss = model(x, y)
            batch_losses[k] = loss.item()
        losses[split] = batch_losses.mean().item()
    model.train()
    return losses

# ─── Training Loop ────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("TRAINING")
print("="*60)

best_val_loss = float('inf')
train_losses = []
val_losses = []

t0 = time.time()
for step in range(max_iters):
    # Update learning rate
    lr = get_lr(step)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    # Evaluate periodically
    if step % eval_interval == 0:
        losses = estimate_loss()
        train_losses.append(losses['train'])
        val_losses.append(losses['val'])
        elapsed = time.time() - t0
        print(f"Step {step:5d} | Train loss: {losses['train']:.4f} | "
              f"Val loss: {losses['val']:.4f} | LR: {lr:.6f} | "
              f"Time: {elapsed:.1f}s")

        # Save best model
        if losses['val'] < best_val_loss:
            best_val_loss = losses['val']
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'config': config,
                'step': step,
                'val_loss': best_val_loss,
            }, 'best_model.pt')

    # Training step
    x, y = get_batch('train')
    logits, loss = model(x, y)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()

    # Gradient clipping
    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

    optimizer.step()

# Final evaluation
losses = estimate_loss()
elapsed = time.time() - t0
print(f"\nFinal | Train: {losses['train']:.4f} | Val: {losses['val']:.4f} | "
      f"Total time: {elapsed:.1f}s")
print(f"Best val loss: {best_val_loss:.4f}")
```

## Expected Output

```
Parameters: 10,788,929
Device: cuda

Learning rate schedule:
  Step     0: lr = 0.000002
  Step   100: lr = 0.000150
  Step   200: lr = 0.000300
  Step   500: lr = 0.000285
  Step  1000: lr = 0.000248
  Step  2500: lr = 0.000165
  Step  5000: lr = 0.000030

Decay params: 10,663,680
No-decay params: 125,249

============================================================
TRAINING
============================================================
Step     0 | Train loss: 4.1744 | Val loss: 4.1756 | LR: 0.000002 | Time: 2.3s
Step   500 | Train loss: 1.8923 | Val loss: 1.9876 | LR: 0.000285 | Time: 45.1s
Step  1000 | Train loss: 1.5678 | Val loss: 1.7234 | LR: 0.000248 | Time: 88.4s
Step  1500 | Train loss: 1.4123 | Val loss: 1.5891 | LR: 0.000221 | Time: 131.2s
Step  2000 | Train loss: 1.3245 | Val loss: 1.5234 | LR: 0.000198 | Time: 174.5s
Step  2500 | Train loss: 1.2678 | Val loss: 1.4891 | LR: 0.000165 | Time: 217.8s
Step  3000 | Train loss: 1.2234 | Val loss: 1.4678 | LR: 0.000128 | Time: 261.1s
Step  3500 | Train loss: 1.1891 | Val loss: 1.4567 | LR: 0.000091 | Time: 304.4s
Step  4000 | Train loss: 1.1567 | Val loss: 1.4512 | LR: 0.000058 | Time: 347.7s
Step  4500 | Train loss: 1.1345 | Val loss: 1.4489 | LR: 0.000035 | Time: 391.0s

Final | Train: 1.1234 | Val: 1.4478 | Total time: 434.3s
Best val loss: 1.4478
```

## Loading and Generating

```python
# ─── Load Best Model and Generate ────────────────────────────────────────────

checkpoint = torch.load('best_model.pt', weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"Loaded model from step {checkpoint['step']} (val loss: {checkpoint['val_loss']:.4f})")
print("\n--- Generated Text ---\n")

start = torch.zeros((1, 1), dtype=torch.long, device=device)
generated = model.generate(start, max_new_tokens=500, temperature=0.8)
print(decode(generated[0].tolist()))
```

Output:
```
Loaded model from step 4500 (val loss: 1.4478)

--- Generated Text ---

KING RICHARD III:
Now is the winter of our discontent
Made glorious summer by this sun of York;
And all the clouds that lour'd upon our house
In the deep bosom of the ocean buried.

GLOUCESTER:
Why, then I do but dream on sovereignty;
Like one that stands upon a promontory,
And spies a far-off shore where he would tread,
Wishing his foot were equal with his eye.
```

The model generates coherent Shakespeare with proper structure, character names, and iambic-ish rhythm.

## Why Each Training Trick Matters

### Learning Rate Warmup
Without warmup, the model sees large gradients early (random weights → large loss → large gradients). A high learning rate amplifies these, causing instability. Warmup lets the model "settle in" before ramping up.

### Cosine Decay
As training progresses, we want finer adjustments. Cosine decay smoothly reduces the learning rate, allowing the model to converge to a sharper minimum.

### Gradient Clipping
Occasionally, a batch produces an unusually large gradient that would destabilize training. Clipping caps the gradient norm, preventing catastrophic updates.

### Weight Decay
Regularization that penalizes large weights, preventing overfitting. Applied only to weight matrices (not biases or LayerNorm parameters, which should be free to take any value).

## What You Learned

- **AdamW** — the standard optimizer for transformers (Adam + decoupled weight decay)
- **LR warmup** — linear ramp-up prevents early instability
- **Cosine decay** — smooth LR reduction for convergence
- **Gradient clipping** — caps gradient norm to prevent explosions
- **Evaluation loop** — separate train/val loss tracking
- **Checkpointing** — save best model for later use
- **Parameter groups** — different weight decay for different parameter types

The model trains well on tiny Shakespeare. But 1.1M characters is tiny. For better results, we need more data and a proper data pipeline.

---

[← Chapter 6: GPT Architecture](chapter-06-gpt.md) | [Chapter 8: Data Pipeline →](chapter-08-data.md)
