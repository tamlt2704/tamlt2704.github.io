# Chapter 0: Before You Start

[Chapter 1: Tokenization →](chapter-01-tokenization.md)

---

## The Story

You're a machine learning engineer at **TinyMind**, a research lab with one rule: "If you can't build it from scratch, you don't understand it."

Your manager, **Dr. Lin**, hands you a challenge:

"Everyone uses GPT. Nobody understands GPT. Build one. Not a wrapper around an API — an actual language model. From raw text to generated sentences. Every matrix multiplication, every attention head, every training step. By the end, you'll have a model that generates coherent English. It'll be small — maybe 10M parameters — but it'll be *yours*."

Over 12 chapters, you'll build a GPT-style language model from scratch using PyTorch. No HuggingFace. No pretrained weights. Just math, code, and text.

## What Is a Language Model?

A language model predicts the next token given the previous tokens:

```
Input:  "The cat sat on the"
Output: "mat" (with probability 0.12)
        "floor" (with probability 0.08)
        "roof" (with probability 0.05)
        ...
```

That's it. The entire magic of ChatGPT, Claude, and every LLM is: **predict the next word, really well, at scale.**

Generation is just repeated prediction:
1. Start with a prompt: "Once upon a"
2. Predict next token: "time"
3. New input: "Once upon a time"
4. Predict next token: "there"
5. Repeat until done

## The Architecture (Preview)

```
┌─────────────────────────────────────────────┐
│              TEXT GENERATION                  │
│  "The cat sat on the" → "mat"               │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│           TRANSFORMER BLOCKS (×N)            │
│  ┌─────────────────────────────────────┐    │
│  │  Multi-Head Self-Attention          │    │
│  │  + Residual Connection + LayerNorm  │    │
│  ├─────────────────────────────────────┤    │
│  │  Feed-Forward Network               │    │
│  │  + Residual Connection + LayerNorm  │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│  Token Embeddings + Positional Encoding      │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│  Tokenizer: "The cat sat" → [464, 3797, ...]│
└─────────────────────────────────────────────┘
```

We'll build every layer of this stack.

## The Roadmap

| Ch | What's Broken | What We Build |
|---|---|---|
| 1 | Can't feed text to a neural network | Tokenizer (text → numbers) |
| 2 | No model at all | Bigram model (simplest LM) |
| 3 | Tokens have no meaning | Embeddings (tokens → vectors) |
| 4 | Can't look at context | Self-attention mechanism |
| 5 | Single attention isn't enough | Full transformer block |
| 6 | One block isn't deep enough | Stacked GPT architecture |
| 7 | Model doesn't learn | Training loop with AdamW |
| 8 | Training on toy data | Real dataset pipeline |
| 9 | Model only computes loss | Text generation with sampling |
| 10 | Model is too small | Scaling, GPU, mixed precision |
| 11 | Model doesn't follow instructions | Fine-tuning and alignment |
| 12 | How good is it? | Evaluation and deployment |

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | ML Engineer | Builds everything from scratch |
| **Dr. Lin** | Lab Director | "Show me the loss curve." |
| **Kai** | Data Engineer | Handles the corpus and tokenizer |
| **The Cluster** | 8×A100 GPUs | Expensive. Impatient. Hot. |
| **Baseline** | The bigram model | Surprisingly hard to beat |

## Prerequisites

### Python 3.10+

```bash
python3 --version
```

### PyTorch 2.0+

```bash
pip install torch
python3 -c "import torch; print(torch.__version__)"
```

### Math You Need

You need three things from math:

**1. Matrix multiplication** — the core operation of neural networks
```python
# (batch, seq_len, d_model) × (d_model, vocab_size) → (batch, seq_len, vocab_size)
logits = hidden_states @ weight_matrix
```

**2. Softmax** — turns numbers into probabilities
```python
# [2.0, 1.0, 0.1] → [0.659, 0.242, 0.099] (sums to 1.0)
probs = torch.softmax(logits, dim=-1)
```

**3. Cross-entropy loss** — measures how wrong our predictions are
```python
# If true token is index 3 and we predicted P(3) = 0.02, loss is -log(0.02) = 3.9 (bad)
# If true token is index 3 and we predicted P(3) = 0.95, loss is -log(0.95) = 0.05 (good)
loss = -torch.log(predicted_probability_of_correct_token)
```

If you know these three, you can build a transformer. Everything else is introduced when you need it.

### Hardware

- **CPU only**: works for chapters 1-9 with small models (takes minutes instead of seconds)
- **Single GPU** (RTX 3060+): comfortable for all chapters
- **Multi-GPU**: only needed for Chapter 10's scaling experiments

### Quick Check

```python
import torch

# Check PyTorch
print(f"PyTorch {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Matrix multiply
a = torch.randn(2, 3)
b = torch.randn(3, 4)
c = a @ b
print(f"Matrix multiply: (2,3) @ (3,4) = {c.shape}")  # (2, 4)

# Softmax
logits = torch.tensor([2.0, 1.0, 0.1])
probs = torch.softmax(logits, dim=0)
print(f"Softmax: {logits.tolist()} → {probs.tolist()}")
print(f"Sum: {probs.sum().item():.4f}")  # 1.0
```

## The Model We'll Build

By Chapter 9, you'll have a working GPT that:
- Has ~10M parameters (tiny by modern standards, but real)
- Trains on a text corpus (Shakespeare, Wikipedia subset, or similar)
- Generates coherent English sentences
- Uses the same architecture as GPT-2/3 (just smaller)

It won't write poetry or answer questions well — that requires billions of parameters and instruction tuning. But it will demonstrate every concept that makes GPT-4 work. The architecture is identical. Only the scale differs.

## How to Read This

Each chapter:
1. Shows what the current model can't do (the failure)
2. Introduces the concept that fixes it (the theory)
3. Implements it in PyTorch (the code)
4. Demonstrates the improvement (the result)

All code is self-contained. Each chapter builds on the previous one. By Chapter 9, you'll have a single Python file (~300 lines) that defines, trains, and generates from a GPT.

Let's turn text into numbers.

---

[Chapter 1: Tokenization →](chapter-01-tokenization.md)
