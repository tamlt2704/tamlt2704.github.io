# Build a Large Language Model from Scratch

[next: Tokenization](chapter-01-tokenization.md)

## What This Series Covers

This series walks through building a GPT-style language model from scratch using Python and PyTorch. Every component is implemented and explained — no black boxes.

## Chapters

1. [Tokenization](chapter-01-tokenization.md) — BPE, vocabulary building, encoding/decoding
2. [Embeddings](chapter-02-embeddings.md) — Token embeddings, positional encodings, RoPE
3. [Attention](chapter-03-attention.md) — Scaled dot-product, multi-head, causal masking
4. [Transformer Block](chapter-04-transformer.md) — LayerNorm, FFN, residual connections
5. [Training](chapter-05-training.md) — Data prep, loss, optimizer, training loop
6. [Text Generation](chapter-06-generation.md) — Sampling strategies, KV-cache
7. [Scaling](chapter-07-scaling.md) — Distributed training, flash attention, parallelism
8. [Fine-tuning](chapter-08-finetuning.md) — SFT, LoRA, RLHF, DPO
9. [Inference and Deployment](chapter-09-inference.md) — Quantization, serving, local running

## What You Will Build

A GPT-style autoregressive language model that can:

- Tokenize raw text using Byte Pair Encoding
- Learn contextual representations via self-attention
- Generate coherent text with various sampling strategies
- Be fine-tuned on instruction-following data

The final model architecture:

```
Input Text
    → Tokenizer (BPE)
    → Token Embeddings + Positional Embeddings
    → N x Transformer Blocks
        → Multi-Head Self-Attention (causal)
        → Feed-Forward Network
        → Layer Normalization + Residual Connections
    → Linear Head → Softmax
    → Next Token Prediction
```

## Prerequisites

**Python**: Comfortable with classes, list comprehensions, generators, decorators.

**Linear Algebra Basics**:

- Matrix multiplication: `C = A @ B` where shapes are `(m, k) @ (k, n) → (m, n)`
- Dot product: `sum(a_i * b_i)` measures similarity between vectors
- Softmax: converts logits to probabilities that sum to 1

**PyTorch Basics**:

```python
import torch
import torch.nn as nn

# Tensors and shapes
x = torch.randn(2, 3)  # shape: (2, 3)
y = torch.randn(3, 4)  # shape: (3, 4)
z = x @ y               # shape: (2, 4)

# nn.Module pattern
class MyLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x):
        return self.linear(x)

# Autograd
x = torch.randn(3, requires_grad=True)
y = (x ** 2).sum()
y.backward()
print(x.grad)  # dy/dx = 2x
```

## Setup

```python
# requirements
# torch >= 2.0
# tiktoken
# datasets
# wandb (optional, for logging)

import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## Model Configuration

We will build toward this configuration (a small GPT-2 scale model):

```python
config = {
    "vocab_size": 50257,
    "context_length": 1024,
    "embed_dim": 768,
    "n_heads": 12,
    "n_layers": 12,
    "dropout": 0.1,
    "bias": False,
}
# Total parameters: ~124M
```
