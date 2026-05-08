# Chapter 10: Scaling Up — GPU Training and Mixed Precision

[← Chapter 9: Generation](chapter-09-generation.md) | [Chapter 11: Fine-tuning →](chapter-11-finetuning.md)

---

## The Problem

Our 10M parameter model generates decent Shakespeare, but it's still small. Real language understanding requires more parameters, more data, and more compute. Training bigger models on CPU takes days. We need GPUs.

The Cluster: "Finally. You've been wasting my time with toy models. Give me a real workload — 100M+ parameters, mixed precision, gradient accumulation. Let me show you what 8 A100s can do."

## Scaling Laws

Kaplan et al. (2020) discovered that LLM performance follows predictable power laws:

```
Loss ∝ 1/N^0.076    (N = parameters)
Loss ∝ 1/D^0.095    (D = dataset size in tokens)
Loss ∝ 1/C^0.050    (C = compute in FLOPs)
```

Translation: **10× more parameters → loss drops by ~17%**. This is why labs keep making models bigger.

| Model Size | Approximate Loss | Quality |
|---|---|---|
| 10M params | ~1.45 | Coherent phrases, broken grammar |
| 100M params | ~1.20 | Good sentences, weak paragraphs |
| 1B params | ~1.00 | Coherent paragraphs |
| 10B params | ~0.85 | Fluent text, some reasoning |
| 100B+ params | ~0.70 | Strong reasoning, instruction following |

## GPU Training Basics

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import time

# ─── Device Setup ─────────────────────────────────────────────────────────────

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device: {device}")

if device == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

# Moving model to GPU — that's it
# model = GPT(config).to(device)

# Moving data to GPU
# x = x.to(device)
# y = y.to(device)

# Everything else (forward, backward, optimizer) works the same
```

## Mixed Precision Training (AMP)

Modern GPUs have specialized hardware for float16/bfloat16 operations that's 2-8× faster than float32. Mixed precision uses lower precision where safe and full precision where needed.

```python
from torch.amp import autocast, GradScaler

# ─── Mixed Precision Training ─────────────────────────────────────────────────

# GradScaler prevents underflow in float16 gradients
scaler = GradScaler('cuda')

def train_step_amp(model, x, y, optimizer, scaler):
    """Single training step with automatic mixed precision."""
    optimizer.zero_grad(set_to_none=True)

    # Forward pass in mixed precision
    with autocast('cuda', dtype=torch.bfloat16):
        logits, loss = model(x, y)

    # Backward pass with gradient scaling
    scaler.scale(loss).backward()

    # Unscale gradients for clipping
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

    # Optimizer step
    scaler.step(optimizer)
    scaler.update()

    return loss.item()


# ─── Simpler: bfloat16 (if GPU supports it) ──────────────────────────────────

# bfloat16 doesn't need GradScaler (same exponent range as float32)
def train_step_bf16(model, x, y, optimizer):
    """Training step with bfloat16 (simpler, no scaler needed)."""
    optimizer.zero_grad(set_to_none=True)

    with autocast('cuda', dtype=torch.bfloat16):
        logits, loss = model(x, y)

    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    return loss.item()
```

**bfloat16 vs float16**:
- `float16`: more precision, but smaller range → needs GradScaler
- `bfloat16`: less precision, but same range as float32 → no scaler needed
- Use bfloat16 if your GPU supports it (A100, H100, RTX 3090+)

## Gradient Accumulation

When your model is too large for big batches, simulate larger batches by accumulating gradients:

```python
def train_with_accumulation(
    model, get_batch_fn, optimizer, steps,
    accumulation_steps=4, device='cuda'
):
    """
    Gradient accumulation: simulate batch_size * accumulation_steps
    with only batch_size memory usage.
    """
    model.train()

    for step in range(steps):
        optimizer.zero_grad(set_to_none=True)
        accumulated_loss = 0.0

        for micro_step in range(accumulation_steps):
            x, y = get_batch_fn()
            x, y = x.to(device), y.to(device)

            with autocast('cuda', dtype=torch.bfloat16):
                logits, loss = model(x, y)
                # Scale loss by accumulation steps
                loss = loss / accumulation_steps

            loss.backward()
            accumulated_loss += loss.item()

        # Clip and step after accumulating all micro-batches
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if step % 100 == 0:
            print(f"Step {step} | Loss: {accumulated_loss:.4f}")
```

With `batch_size=16` and `accumulation_steps=4`, the effective batch size is 64, but you only need memory for 16 samples at a time.

## Scaled-Up Configuration

```python
# ─── Larger Model Configs ─────────────────────────────────────────────────────

configs = {
    'small': dict(    # ~10M params (what we've been using)
        n_embd=384, n_head=6, n_layer=6, block_size=256,
    ),
    'medium': dict(   # ~50M params
        n_embd=512, n_head=8, n_layer=8, block_size=512,
    ),
    'large': dict(    # ~150M params
        n_embd=768, n_head=12, n_layer=12, block_size=1024,
    ),
    'xl': dict(       # ~350M params (GPT-2 Medium scale)
        n_embd=1024, n_head=16, n_layer=24, block_size=1024,
    ),
}

def estimate_params(config):
    """Rough parameter count estimate."""
    d = config['n_embd']
    L = config['n_layer']
    # ~12 * d^2 per layer (attention + FFN) + embeddings
    return 12 * L * d * d + config.get('vocab_size', 50257) * d

for name, cfg in configs.items():
    params = estimate_params(cfg)
    print(f"{name:8s}: ~{params/1e6:.0f}M parameters")
```

```
small   : ~10M parameters
medium  : ~50M parameters
large   : ~150M parameters
xl      : ~350M parameters
```

## Complete Scaled Training Script

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.amp import autocast, GradScaler
import math
import time
import os
import urllib.request

# ─── GPT Model (same as Chapter 6, abbreviated) ──────────────────────────────

class GPTConfig:
    def __init__(self, **kwargs):
        self.vocab_size = kwargs.get('vocab_size', 65)
        self.block_size = kwargs.get('block_size', 512)
        self.n_embd = kwargs.get('n_embd', 512)
        self.n_head = kwargs.get('n_head', 8)
        self.n_layer = kwargs.get('n_layer', 8)
        self.dropout = kwargs.get('dropout', 0.1)

# (Full GPT class from Chapter 6 goes here)
# For brevity, assume it's imported or defined above

# ─── Training Configuration ──────────────────────────────────────────────────

device = 'cuda' if torch.cuda.is_available() else 'cpu'
use_amp = device == 'cuda'

# Hyperparameters for scaled training
batch_size = 32                # per-device batch size
accumulation_steps = 4         # effective batch = 32 * 4 = 128
max_iters = 10000
max_lr = 6e-4
min_lr = 6e-5
warmup_iters = 500
weight_decay = 0.1
grad_clip = 1.0

# ─── Learning Rate Schedule ───────────────────────────────────────────────────

def get_lr(step):
    if step < warmup_iters:
        return max_lr * (step + 1) / warmup_iters
    if step > max_iters:
        return min_lr
    decay_ratio = (step - warmup_iters) / (max_iters - warmup_iters)
    return min_lr + 0.5 * (1 + math.cos(math.pi * decay_ratio)) * (max_lr - min_lr)

# ─── Training Loop with All Optimizations ─────────────────────────────────────

"""
config = GPTConfig(vocab_size=vocab_size)
model = GPT(config).to(device)

# Compile model for faster execution (PyTorch 2.0+)
if hasattr(torch, 'compile'):
    model = torch.compile(model)

optimizer = torch.optim.AdamW(
    model.parameters(), lr=max_lr, betas=(0.9, 0.95), weight_decay=weight_decay
)
scaler = GradScaler('cuda', enabled=use_amp)

for step in range(max_iters):
    t0 = time.time()

    # Update learning rate
    lr = get_lr(step)
    for pg in optimizer.param_groups:
        pg['lr'] = lr

    # Gradient accumulation
    optimizer.zero_grad(set_to_none=True)
    loss_accum = 0.0

    for micro_step in range(accumulation_steps):
        x, y = get_batch('train')

        with autocast('cuda', dtype=torch.bfloat16, enabled=use_amp):
            logits, loss = model(x, y)
            loss = loss / accumulation_steps

        scaler.scale(loss).backward()
        loss_accum += loss.item()

    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
    scaler.step(optimizer)
    scaler.update()

    # Timing
    dt = time.time() - t0
    tokens_per_sec = batch_size * accumulation_steps * config.block_size / dt

    if step % 100 == 0:
        print(f"Step {step:5d} | Loss: {loss_accum:.4f} | "
              f"LR: {lr:.6f} | {tokens_per_sec:.0f} tok/s | {dt*1000:.0f}ms")
"""
```

## torch.compile (PyTorch 2.0+)

One line for 20-40% speedup:

```python
# Before training:
model = torch.compile(model)

# That's it. PyTorch traces and optimizes the computation graph.
# First iteration is slow (compilation), subsequent ones are faster.
```

## Multi-GPU: Distributed Data Parallel (DDP)

For multiple GPUs, DDP replicates the model and splits batches:

```python
# ─── DDP Overview (conceptual) ────────────────────────────────────────────────

"""
# Launch with: torchrun --nproc_per_node=4 train.py

import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

# Initialize process group
dist.init_process_group(backend='nccl')
local_rank = int(os.environ['LOCAL_RANK'])
torch.cuda.set_device(local_rank)

# Create model on this GPU
model = GPT(config).to(local_rank)
model = DDP(model, device_ids=[local_rank])

# Training loop is the same — DDP handles gradient synchronization
# Each GPU processes batch_size samples → effective batch = batch_size * num_gpus

# Cleanup
dist.destroy_process_group()
"""
```

DDP scales nearly linearly: 4 GPUs ≈ 4× throughput. The communication overhead (gradient all-reduce) is small compared to computation.

## Performance Comparison

| Optimization | Speedup | Memory Savings |
|---|---|---|
| GPU (vs CPU) | 10-50× | — |
| Mixed precision (bf16) | 1.5-2× | 50% |
| torch.compile | 1.2-1.4× | — |
| Gradient accumulation | — | Proportional to steps |
| DDP (4 GPUs) | ~3.8× | — |
| **All combined** | **50-200×** | **50%** |

## What You Learned

- **GPU training** — `.to(device)` for model and data, everything else is the same
- **Mixed precision** — `autocast` + `GradScaler` for 2× speedup with half the memory
- **bfloat16** — preferred over float16 when available (no scaler needed)
- **Gradient accumulation** — simulate large batches with limited memory
- **torch.compile** — one-line 20-40% speedup (PyTorch 2.0+)
- **DDP** — multi-GPU training with near-linear scaling
- **Scaling laws** — predictable relationship between compute and performance

Our model is now training efficiently at scale. But it just completes text — it doesn't follow instructions or answer questions. That requires fine-tuning.

---

[← Chapter 9: Generation](chapter-09-generation.md) | [Chapter 11: Fine-tuning →](chapter-11-finetuning.md)
