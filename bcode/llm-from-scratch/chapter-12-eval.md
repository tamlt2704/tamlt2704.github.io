# Chapter 12: Evaluation and Deployment — Is It Any Good?

[← Chapter 11: Fine-tuning](chapter-11-finetuning.md) | [Overview →](chapter-00-overview.md)

---

## The Problem

We've built, trained, and fine-tuned a GPT. But how do we measure quality? "The output looks okay" isn't a metric. And even if the model is good, inference is slow — generating one token requires a full forward pass through the entire model.

Dr. Lin: "Two questions remain. First: how good is your model, quantitatively? Second: can you serve it fast enough to be useful? Perplexity for the first. KV-cache for the second. Then we ship it."

## Perplexity: The Standard LM Metric

Perplexity measures how "surprised" the model is by held-out text. Lower = better.

```
Perplexity = exp(average cross-entropy loss)
```

Intuition: a perplexity of 20 means the model is, on average, as uncertain as if it were choosing uniformly among 20 tokens at each step.

```python
import torch
import torch.nn.functional as F
import math

@torch.no_grad()
def compute_perplexity(model, data_loader, device='cuda'):
    """Compute perplexity on a dataset."""
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    for x, y in data_loader:
        x, y = x.to(device), y.to(device)
        logits, loss = model(x, y)

        # Count non-padding tokens
        num_tokens = (y != 0).sum().item()  # assuming 0 is padding
        if num_tokens == 0:
            num_tokens = y.numel()

        total_loss += loss.item() * num_tokens
        total_tokens += num_tokens

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)
    return perplexity, avg_loss


# Usage:
# ppl, loss = compute_perplexity(model, val_loader)
# print(f"Perplexity: {ppl:.2f} | Loss: {loss:.4f}")
```

### Perplexity Benchmarks

| Model | Perplexity (WikiText-103) |
|---|---|
| Random (vocab=50K) | 50,000 |
| Bigram model | ~200 |
| LSTM (small) | ~80 |
| Our GPT (10M) | ~40-60 |
| GPT-2 (117M) | ~30 |
| GPT-2 (1.5B) | ~18 |
| GPT-3 (175B) | ~10 |

## KV-Cache: Fast Inference

During generation, we recompute attention for ALL previous tokens at every step. This is wasteful — previous tokens' keys and values don't change.

**KV-Cache**: store computed K and V tensors, only compute the new token's Q/K/V.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class CachedHead(nn.Module):
    """Single attention head with KV-cache for fast inference."""

    def __init__(self, n_embd, head_size, block_size, dropout=0.0):
        super().__init__()
        self.W_Q = nn.Linear(n_embd, head_size, bias=False)
        self.W_K = nn.Linear(n_embd, head_size, bias=False)
        self.W_V = nn.Linear(n_embd, head_size, bias=False)
        self.head_size = head_size

    def forward(self, x, kv_cache=None):
        """
        x: (B, T, C) during training, (B, 1, C) during cached inference
        kv_cache: tuple of (cached_K, cached_V) or None
        """
        B, T, C = x.shape

        Q = self.W_Q(x)  # (B, T, head_size)
        K = self.W_K(x)  # (B, T, head_size)
        V = self.W_V(x)  # (B, T, head_size)

        if kv_cache is not None:
            # Append new K, V to cache
            cached_K, cached_V = kv_cache
            K = torch.cat([cached_K, K], dim=1)  # (B, T_cached + T, head_size)
            V = torch.cat([cached_V, V], dim=1)

        # Store updated cache
        new_cache = (K, V)

        # Attention (Q attends to all K)
        scores = Q @ K.transpose(-2, -1) / (self.head_size ** 0.5)

        # Causal mask (only needed during training with T > 1)
        if T > 1:
            mask = torch.triu(torch.ones(T, K.size(1), device=x.device), diagonal=K.size(1)-T+1).bool()
            scores = scores.masked_fill(mask.unsqueeze(0), float('-inf'))

        weights = F.softmax(scores, dim=-1)
        out = weights @ V

        return out, new_cache


class CachedGPT(nn.Module):
    """GPT with KV-cache for efficient generation."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        # ... (full model definition)
        # Each layer stores its own KV cache

    @torch.no_grad()
    def generate_with_cache(self, idx, max_new_tokens, temperature=1.0):
        """Generate with KV-cache — O(1) per new token instead of O(n)."""
        caches = [None] * self.config.n_layer  # one cache per layer

        for i in range(max_new_tokens):
            if i == 0:
                # First token: process entire prompt
                idx_input = idx
                pos = torch.arange(idx.size(1), device=idx.device)
            else:
                # Subsequent tokens: only process the new token
                idx_input = idx[:, -1:]
                pos = torch.tensor([idx.size(1) - 1], device=idx.device)

            # Forward pass (with cache)
            tok_emb = self.token_embedding(idx_input)
            pos_emb = self.position_embedding(pos)
            x = tok_emb + pos_emb

            # Pass through each layer, updating caches
            for layer_idx, block in enumerate(self.blocks):
                x, caches[layer_idx] = block(x, kv_cache=caches[layer_idx])

            x = self.ln_f(x)
            logits = self.lm_head(x[:, -1, :]) / temperature
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)

        return idx
```

### Speed Comparison

```python
import time

def benchmark_generation(model, prompt_tokens, num_tokens=100, device='cuda'):
    """Compare generation speed with and without KV-cache."""

    # Without cache (naive)
    start = time.time()
    _ = model.generate(prompt_tokens.clone(), max_new_tokens=num_tokens)
    naive_time = time.time() - start

    # With cache
    start = time.time()
    _ = model.generate_with_cache(prompt_tokens.clone(), max_new_tokens=num_tokens)
    cached_time = time.time() - start

    print(f"Without KV-cache: {naive_time:.2f}s ({num_tokens/naive_time:.0f} tok/s)")
    print(f"With KV-cache:    {cached_time:.2f}s ({num_tokens/cached_time:.0f} tok/s)")
    print(f"Speedup:          {naive_time/cached_time:.1f}×")

# Expected output:
# Without KV-cache: 4.23s (24 tok/s)
# With KV-cache:    0.87s (115 tok/s)
# Speedup:          4.9×
```

The speedup grows with sequence length. For 2048-token contexts, KV-cache gives 10-50× speedup.

## Quantization: Smaller and Faster

Reduce model size by using fewer bits per weight:

```python
# ─── Simple Weight Quantization ───────────────────────────────────────────────

def quantize_model_int8(model):
    """Naive int8 quantization (for illustration)."""
    for name, param in model.named_parameters():
        if param.dim() >= 2:  # only quantize weight matrices
            # Find scale
            max_val = param.data.abs().max()
            scale = max_val / 127.0

            # Quantize to int8
            quantized = (param.data / scale).round().clamp(-128, 127).to(torch.int8)

            # Store quantized weight and scale
            # (In practice, you'd use a custom module)
            param.data = (quantized.float() * scale)

    return model


# In practice, use PyTorch's built-in quantization:
"""
import torch.quantization

# Dynamic quantization (easiest)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {nn.Linear},  # which layers to quantize
    dtype=torch.qint8
)

# Check size reduction
original_size = sum(p.numel() * p.element_size() for p in model.parameters())
quantized_size = sum(p.numel() * p.element_size() for p in quantized_model.parameters())
print(f"Original:  {original_size / 1e6:.1f} MB")
print(f"Quantized: {quantized_size / 1e6:.1f} MB")
print(f"Reduction: {original_size / quantized_size:.1f}×")
"""
```

| Precision | Bits/param | Model Size (7B) | Quality |
|---|---|---|---|
| float32 | 32 | 28 GB | Baseline |
| float16 | 16 | 14 GB | ~Same |
| int8 | 8 | 7 GB | Slight degradation |
| int4 (GPTQ/AWQ) | 4 | 3.5 GB | Small degradation |

## Evaluation Benchmarks

Beyond perplexity, evaluate on tasks:

```python
# ─── Simple Benchmark: Text Completion Accuracy ───────────────────────────────

@torch.no_grad()
def evaluate_completion(model, tokenizer, examples, device='cuda'):
    """
    Evaluate: given a prompt, does the model's top prediction match the expected next token?
    """
    model.eval()
    correct = 0
    total = 0

    for prompt, expected in examples:
        tokens = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long, device=device)
        logits, _ = model(tokens)
        predicted_token = logits[0, -1, :].argmax().item()
        expected_token = tokenizer.encode(expected)[0]

        if predicted_token == expected_token:
            correct += 1
        total += 1

    accuracy = correct / total
    print(f"Completion accuracy: {correct}/{total} = {accuracy:.1%}")
    return accuracy


# Example evaluation set
eval_examples = [
    ("To be or not to b", "e"),
    ("The quick brown fo", "x"),
    ("Once upon a tim", "e"),
    # ...
]
```

### Common LLM Benchmarks

| Benchmark | What It Tests | Format |
|---|---|---|
| HellaSwag | Common sense | Multiple choice |
| MMLU | Knowledge (57 subjects) | Multiple choice |
| HumanEval | Code generation | Function completion |
| TruthfulQA | Factual accuracy | Open-ended |
| GSM8K | Math reasoning | Word problems |
| ARC | Science reasoning | Multiple choice |

## Deployment Options

```python
# ─── Simple Inference Server ──────────────────────────────────────────────────

"""
# Using FastAPI for a simple inference endpoint:

from fastapi import FastAPI
from pydantic import BaseModel
import torch

app = FastAPI()

# Load model once at startup
model = load_model('best_model.pt')
model.eval()
tokenizer = load_tokenizer()

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.8
    top_p: float = 0.9

@app.post("/generate")
async def generate(req: GenerateRequest):
    tokens = torch.tensor([tokenizer.encode(req.prompt)], device='cuda')
    output = model.generate_with_cache(
        tokens,
        max_new_tokens=req.max_tokens,
        temperature=req.temperature,
    )
    text = tokenizer.decode(output[0].tolist())
    return {"text": text}
"""
```

## The Complete Architecture (Final Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                    GPT LANGUAGE MODEL                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: "The cat sat on the"                                     │
│       ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  TOKENIZER (Ch.1)                                        │     │
│  │  "The cat sat on the" → [464, 3797, 3332, 319, 262]    │     │
│  └─────────────────────────────────────────────────────────┘     │
│       ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  TOKEN EMBEDDING (Ch.3)         POSITION EMBEDDING       │     │
│  │  [464,...] → (5, 384)     +     [0,1,2,3,4] → (5, 384) │     │
│  └─────────────────────────────────────────────────────────┘     │
│       ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  TRANSFORMER BLOCK ×6 (Ch.4-5)                           │     │
│  │  ┌───────────────────────────────────────────────────┐   │     │
│  │  │  LayerNorm → Multi-Head Attention (6 heads)       │   │     │
│  │  │    Q, K, V projections → scaled dot-product       │   │     │
│  │  │    causal mask → softmax → weighted sum           │   │     │
│  │  │  + Residual Connection                            │   │     │
│  │  ├───────────────────────────────────────────────────┤   │     │
│  │  │  LayerNorm → Feed-Forward (384 → 1536 → 384)     │   │     │
│  │  │    GELU activation                                │   │     │
│  │  │  + Residual Connection                            │   │     │
│  │  └───────────────────────────────────────────────────┘   │     │
│  └─────────────────────────────────────────────────────────┘     │
│       ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  FINAL LAYER NORM → LINEAR PROJECTION (Ch.6)            │     │
│  │  (5, 384) → (5, vocab_size)                             │     │
│  └─────────────────────────────────────────────────────────┘     │
│       ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  GENERATION (Ch.9)                                       │     │
│  │  logits → temperature → top-p → sample → "mat"          │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  TRAINING (Ch.7): AdamW + warmup + cosine decay + grad clip      │
│  DATA (Ch.8): Dataset → DataLoader → random context windows      │
│  SCALING (Ch.10): AMP + gradient accumulation + DDP              │
│  FINE-TUNING (Ch.11): SFT + LoRA + RLHF/DPO                    │
│  EVAL (Ch.12): Perplexity + benchmarks + KV-cache + quantize    │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Config: vocab=65, block=256, d=384, heads=6, layers=6          │
│  Parameters: ~10.8M | Training: ~5000 steps on Shakespeare      │
└─────────────────────────────────────────────────────────────────┘
```

## Course Wrap-Up

You built a GPT from scratch. Here's what you now understand:

| Chapter | Concept | Why It Matters |
|---|---|---|
| 1 | Tokenization | Text → numbers the model can process |
| 2 | Bigram model | Simplest LM baseline, training loop fundamentals |
| 3 | Embeddings | Tokens get meaning through learned vectors |
| 4 | Self-attention | Tokens communicate — the core transformer innovation |
| 5 | Transformer block | Multi-head attention + FFN + residuals = one unit |
| 6 | GPT architecture | Stack blocks, add embeddings, project to vocab |
| 7 | Training | AdamW, warmup, cosine decay, gradient clipping |
| 8 | Data pipeline | Efficient loading, batching, larger corpora |
| 9 | Generation | Temperature, top-k, top-p sampling strategies |
| 10 | Scaling | GPU, mixed precision, gradient accumulation, DDP |
| 11 | Fine-tuning | SFT, LoRA, RLHF — from completion to instruction |
| 12 | Evaluation | Perplexity, KV-cache, quantization, deployment |

## What's Next

From here, you could:
- **Scale up**: train a 100M+ model on OpenWebText
- **Add features**: rotary embeddings (RoPE), grouped-query attention, flash attention
- **Fine-tune**: collect instruction data and train a chatbot
- **Optimize**: implement flash attention, speculative decoding, continuous batching
- **Research**: experiment with architectures (Mamba, RWKV, mixture of experts)

The architecture you built is the same one powering GPT-4, Claude, LLaMA, and every other modern LLM. The difference is scale — more parameters, more data, more compute. But the ideas are identical.

Dr. Lin: "You built it from scratch. You understand it. Now go make it bigger."

## What You Learned

- **Perplexity** — exp(loss), the standard LM quality metric
- **KV-cache** — store past keys/values for O(1) generation per token
- **Quantization** — reduce precision (int8/int4) for smaller, faster models
- **Benchmarks** — HellaSwag, MMLU, HumanEval for standardized evaluation
- **Deployment** — serve the model via API with optimized inference
- **The full picture** — every component from tokenization to deployment

---

*You started with text and ended with a language model that generates coherent English. Every matrix multiplication, every attention head, every training step — built from scratch. The Cluster is satisfied. Dr. Lin nods. Baseline (the bigram model) is jealous.*

---

[← Chapter 11: Fine-tuning](chapter-11-finetuning.md) | [Overview →](chapter-00-overview.md)
