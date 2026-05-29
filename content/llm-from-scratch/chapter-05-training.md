# Chapter 5: Training

[prev: Transformer Block](chapter-04-transformer.md) | [next: Text Generation](chapter-06-generation.md)

Training a language model means teaching it to predict the next token. This chapter covers dataset preparation, the loss function, optimizer, and the full training loop.

## Dataset Preparation

We need to convert raw text into (input, target) pairs where the target is the input shifted by one position:

```python
import torch
from torch.utils.data import Dataset, DataLoader
import tiktoken

class TextDataset(Dataset):
    def __init__(self, text, seq_len=128, tokenizer_name="gpt2"):
        self.seq_len = seq_len
        enc = tiktoken.get_encoding(tokenizer_name)
        self.tokens = torch.tensor(enc.encode(text), dtype=torch.long)

    def __len__(self):
        return (len(self.tokens) - 1) // self.seq_len

    def __getitem__(self, idx):
        start = idx * self.seq_len
        chunk = self.tokens[start : start + self.seq_len + 1]
        x = chunk[:-1]   # input:  tokens[0..seq_len-1]
        y = chunk[1:]    # target: tokens[1..seq_len]
        return x, y
        # x shape: (seq_len,)
        # y shape: (seq_len,)

# Usage
text = open("corpus.txt").read()  # your training text
dataset = TextDataset(text, seq_len=128)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Each batch: x shape (32, 128), y shape (32, 128)
```

## Cross-Entropy Loss (Next Token Prediction)

The model outputs logits for every position. We compare against the actual next token:

```python
import torch
import torch.nn as nn

def compute_loss(logits, targets):
    """
    logits shape: (batch, seq_len, vocab_size)
    targets shape: (batch, seq_len)
    """
    # Reshape for cross_entropy: (batch * seq_len, vocab_size) vs (batch * seq_len,)
    batch, seq_len, vocab_size = logits.shape
    loss = nn.functional.cross_entropy(
        logits.view(batch * seq_len, vocab_size),
        targets.view(batch * seq_len)
    )
    return loss

# Perplexity = exp(loss)
# Lower perplexity = better model
```

## AdamW Optimizer

AdamW decouples weight decay from the gradient update. Standard for training LLMs:

```python
import torch

def configure_optimizer(model, lr=3e-4, weight_decay=0.1):
    """Separate parameters that should/shouldn't have weight decay."""
    decay_params = []
    no_decay_params = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        # Don't decay biases and LayerNorm parameters
        if param.ndim == 1 or "bias" in name:
            no_decay_params.append(param)
        else:
            decay_params.append(param)

    param_groups = [
        {"params": decay_params, "weight_decay": weight_decay},
        {"params": no_decay_params, "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(param_groups, lr=lr, betas=(0.9, 0.95))
    return optimizer
```

## Learning Rate Scheduling (Warmup + Cosine Decay)

```python
import math

def get_lr(step, warmup_steps=1000, max_steps=100000, max_lr=3e-4, min_lr=3e-5):
    """Cosine decay with linear warmup."""
    if step < warmup_steps:
        # Linear warmup
        return max_lr * step / warmup_steps
    if step >= max_steps:
        return min_lr
    # Cosine decay
    progress = (step - warmup_steps) / (max_steps - warmup_steps)
    return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))
```

## Gradient Clipping

Prevents exploding gradients by capping the global norm:

```python
import torch

# After loss.backward(), before optimizer.step():
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

## Mixed Precision Training (fp16/bf16)

Use lower precision for forward/backward pass to save memory and speed up training:

```python
import torch
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for x, y in dataloader:
    x, y = x.cuda(), y.cuda()
    optimizer.zero_grad()

    # Forward pass in mixed precision
    with autocast(dtype=torch.bfloat16):
        logits = model(x)
        loss = compute_loss(logits, y)

    # Backward pass with gradient scaling (for fp16; bf16 doesn't need it)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    scaler.step(optimizer)
    scaler.update()
```

**bf16 vs fp16**: bf16 has the same exponent range as fp32 (no overflow issues), so it does not need loss scaling. Preferred on modern GPUs (A100+).

## Complete Training Loop

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import time

def train(model, dataloader, max_steps=10000, device="cuda"):
    model = model.to(device)
    model.train()

    optimizer = configure_optimizer(model, lr=3e-4)
    warmup_steps = min(1000, max_steps // 10)

    step = 0
    total_loss = 0.0
    log_interval = 100

    start_time = time.time()

    while step < max_steps:
        for x, y in dataloader:
            if step >= max_steps:
                break

            x, y = x.to(device), y.to(device)
            # x shape: (batch, seq_len)
            # y shape: (batch, seq_len)

            # Update learning rate
            lr = get_lr(step, warmup_steps, max_steps)
            for param_group in optimizer.param_groups:
                param_group["lr"] = lr

            # Forward
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(x)  # (batch, seq_len, vocab_size)
                loss = compute_loss(logits, y)

            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            step += 1

            if step % log_interval == 0:
                avg_loss = total_loss / log_interval
                elapsed = time.time() - start_time
                tokens_per_sec = (log_interval * x.shape[0] * x.shape[1]) / elapsed
                print(
                    f"Step {step:>6d} | Loss {avg_loss:.4f} | "
                    f"Perplexity {math.exp(avg_loss):.2f} | "
                    f"LR {lr:.2e} | "
                    f"Tokens/s {tokens_per_sec:.0f}"
                )
                total_loss = 0.0
                start_time = time.time()

    return model

# Run training
# model = GPT(vocab_size=50257, embed_dim=768, n_heads=12, n_layers=12)
# trained_model = train(model, dataloader, max_steps=10000)
```

## Putting It All Together

```python
import torch
import tiktoken
from torch.utils.data import DataLoader

# 1. Load and tokenize data
text = open("corpus.txt").read()
dataset = TextDataset(text, seq_len=128)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# 2. Create model (from Chapter 4)
model = GPT(
    vocab_size=50257,
    embed_dim=768,
    n_heads=12,
    n_layers=12,
    max_len=1024,
    dropout=0.1,
)

# 3. Train
trained_model = train(model, dataloader, max_steps=10000)

# 4. Save checkpoint
torch.save({
    "model_state_dict": trained_model.state_dict(),
    "step": 10000,
}, "checkpoint.pt")
```

## Key Takeaways

- Language modeling objective: predict the next token at every position
- AdamW with weight decay on 2D+ parameters, no decay on biases/norms
- Cosine LR schedule with warmup prevents early training instability
- Gradient clipping at norm 1.0 prevents exploding gradients
- bf16 mixed precision halves memory usage with minimal accuracy loss
- Monitor perplexity (`exp(loss)`) — lower is better
