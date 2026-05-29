# Chapter 7: Scaling

[prev: Text Generation](chapter-06-generation.md) | [next: Fine-tuning](chapter-08-finetuning.md)

Scaling transforms a toy model into a capable one. This chapter covers parameter counting, compute estimation, scaling laws, and distributed training techniques.

## Model Sizes (Parameter Calculation)

```python
def count_parameters(vocab_size, embed_dim, n_layers, n_heads, max_len):
    """Calculate total parameters for a GPT model."""
    head_dim = embed_dim // n_heads

    # Token embeddings
    token_emb = vocab_size * embed_dim

    # Position embeddings
    pos_emb = max_len * embed_dim

    # Per transformer block
    attn_qkv = embed_dim * (3 * embed_dim)  # W_qkv (no bias)
    attn_out = embed_dim * embed_dim          # W_out
    ffn_up = embed_dim * (4 * embed_dim)      # fc1
    ffn_down = (4 * embed_dim) * embed_dim    # fc2
    ln_params = 2 * embed_dim * 2             # 2 LayerNorms (gamma + beta each)

    per_block = attn_qkv + attn_out + ffn_up + ffn_down + ln_params
    all_blocks = per_block * n_layers

    # Final LayerNorm
    final_ln = 2 * embed_dim

    # LM head (tied with token_emb, so not counted separately)
    total = token_emb + pos_emb + all_blocks + final_ln
    return total

# Common model sizes
models = [
    ("GPT-2 Small",  50257, 768,  12, 12, 1024),
    ("GPT-2 Medium", 50257, 1024, 24, 16, 1024),
    ("GPT-2 Large",  50257, 1280, 36, 20, 1024),
    ("GPT-2 XL",     50257, 1600, 48, 25, 1024),
    ("LLaMA-7B",     32000, 4096, 32, 32, 2048),
]

for name, *args in models:
    params = count_parameters(*args)
    print(f"{name:15s}: {params / 1e6:>8.1f}M parameters")
```

## Compute Requirements (FLOPs)

Rule of thumb: `FLOPs per token ≈ 6 * N` (where N = number of parameters)

For training: `Total FLOPs ≈ 6 * N * D` (D = number of training tokens)

```python
def estimate_training_flops(n_params, n_tokens):
    """Estimate total FLOPs for training."""
    flops = 6 * n_params * n_tokens
    # Convert to GPU-hours (A100 = ~312 TFLOPS bf16)
    a100_tflops = 312e12
    gpu_seconds = flops / a100_tflops
    gpu_hours = gpu_seconds / 3600
    return flops, gpu_hours

# Example: train a 7B model on 1T tokens
flops, hours = estimate_training_flops(7e9, 1e12)
print(f"FLOPs: {flops:.2e}")
print(f"A100 GPU-hours: {hours:.0f}")
print(f"A100 GPU-days: {hours/24:.0f}")
```

## Scaling Laws (Chinchilla)

The Chinchilla paper found the optimal ratio: **train tokens ≈ 20x parameters**.

| Model Size | Optimal Tokens | Compute Budget |
| ---------- | -------------- | -------------- |
| 1B         | 20B tokens     | ~3.6e20 FLOPs  |
| 7B         | 140B tokens    | ~5.9e21 FLOPs  |
| 70B        | 1.4T tokens    | ~5.9e23 FLOPs  |

Key insight: Many models were undertrained. A smaller model trained on more data often beats a larger model trained on less data.

## Gradient Accumulation

Simulate larger batch sizes without more GPU memory:

```python
import torch

def train_with_gradient_accumulation(model, dataloader, optimizer,
                                     accumulation_steps=8, device="cuda"):
    """Effective batch size = micro_batch_size * accumulation_steps."""
    model.train()

    for step, (x, y) in enumerate(dataloader):
        x, y = x.to(device), y.to(device)

        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            logits = model(x)
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), y.view(-1)
            )
            # Scale loss by accumulation steps
            loss = loss / accumulation_steps

        loss.backward()

        if (step + 1) % accumulation_steps == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
```

## Distributed Training: DDP

Distributed Data Parallel — each GPU has a full model copy, data is split across GPUs:

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup_ddp(rank, world_size):
    """Initialize distributed process group."""
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def train_ddp(rank, world_size, model, dataset):
    setup_ddp(rank, world_size)

    model = model.to(rank)
    model = DDP(model, device_ids=[rank])

    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=32, sampler=sampler
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)

    for epoch in range(10):
        sampler.set_epoch(epoch)  # Shuffle differently each epoch
        for x, y in dataloader:
            x, y = x.to(rank), y.to(rank)
            logits = model(x)
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), y.view(-1)
            )
            optimizer.zero_grad()
            loss.backward()  # Gradients are all-reduced automatically
            optimizer.step()

    dist.destroy_process_group()

# Launch: torchrun --nproc_per_node=4 train.py
```

## Distributed Training: FSDP

Fully Sharded Data Parallel — shards model parameters, gradients, and optimizer states across GPUs:

```python
import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import MixedPrecision

# FSDP wraps the model and shards parameters
bfloat16_policy = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.bfloat16,
    buffer_dtype=torch.bfloat16,
)

model = FSDP(
    model,
    mixed_precision=bfloat16_policy,
    use_orig_params=True,
)
# Memory per GPU: ~model_size / num_gpus (vs full copy in DDP)
```

**DDP vs FSDP**:

- DDP: each GPU holds full model. Limited by single-GPU memory.
- FSDP: shards everything. Can train models larger than single-GPU memory.

## Flash Attention

Flash Attention computes exact attention without materializing the full `(seq_len, seq_len)` attention matrix. Reduces memory from `O(N^2)` to `O(N)`:

```python
import torch
import torch.nn.functional as F

# PyTorch 2.0+ has built-in flash attention
def attention_with_flash(Q, K, V, is_causal=True):
    """
    Q, K, V shape: (batch, n_heads, seq_len, head_dim)
    Uses flash attention kernel automatically when available.
    """
    output = F.scaled_dot_product_attention(
        Q, K, V,
        is_causal=is_causal,
        dropout_p=0.0,
    )
    # output shape: (batch, n_heads, seq_len, head_dim)
    return output

# Drop-in replacement in CausalSelfAttention:
# Instead of manual score computation, just call:
# out = F.scaled_dot_product_attention(Q, K, V, is_causal=True)
```

**Benefits**: 2-4x faster, uses O(N) memory instead of O(N^2). Essential for long sequences.

## Memory Optimization

```python
import torch

# 1. Activation checkpointing: recompute activations during backward
#    instead of storing them (trades compute for memory)
from torch.utils.checkpoint import checkpoint

class TransformerBlockCheckpointed(torch.nn.Module):
    def __init__(self, block):
        super().__init__()
        self.block = block

    def forward(self, x):
        return checkpoint(self.block, x, use_reentrant=False)

# 2. torch.compile: fuses operations, reduces memory overhead
model = torch.compile(model)
```

## Model Parallelism

When a single model does not fit on one GPU even with FSDP:

**Tensor Parallelism**: Split individual layers across GPUs (e.g., split the FFN weight matrix column-wise across 2 GPUs).

**Pipeline Parallelism**: Put different layers on different GPUs. Forward pass flows through GPUs sequentially.

```
Tensor Parallel (within a layer):
  GPU 0: first half of FFN columns
  GPU 1: second half of FFN columns
  -> All-reduce to combine

Pipeline Parallel (across layers):
  GPU 0: layers 0-5
  GPU 1: layers 6-11
  -> Micro-batches overlap computation
```

## Summary of Scaling Techniques

| Technique                | What it does              | When to use               |
| ------------------------ | ------------------------- | ------------------------- |
| Gradient Accumulation    | Larger effective batch    | Limited GPU memory        |
| DDP                      | Data parallel across GPUs | Model fits on 1 GPU       |
| FSDP                     | Shard model across GPUs   | Model too large for 1 GPU |
| Flash Attention          | O(N) memory attention     | Always (free speedup)     |
| Activation Checkpointing | Recompute vs store        | Memory constrained        |
| torch.compile            | Kernel fusion             | Always (PyTorch 2.0+)     |
| Tensor Parallelism       | Split layers across GPUs  | Very large models         |
| Pipeline Parallelism     | Split model stages        | Very large models         |

## Key Takeaways

- Parameter count is dominated by attention and FFN weights (not embeddings)
- Chinchilla scaling: use 20 tokens per parameter for optimal compute efficiency
- Gradient accumulation is the simplest way to increase effective batch size
- DDP for multi-GPU when model fits on one GPU; FSDP when it does not
- Flash Attention is a free lunch — always use it
- torch.compile gives 10-30% speedup with one line of code
