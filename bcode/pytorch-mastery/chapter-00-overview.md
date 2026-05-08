# Chapter 0: Before You Start

[Chapter 1: Tensors →](chapter-01-tensors.md)

---

## The Story

You're a research engineer at **DeepForge**, a startup that builds custom ML models for clients. Your first week, the CTO **Mara** drops by:

"We use PyTorch for everything here. Not because it's trendy — because it's Python all the way down. You can debug it, print it, step through it. No magic. If something breaks, you read the code and fix it. That's the deal."

Over 12 chapters, you'll build real models for real projects — image classifiers, text models, GANs, production APIs — each one teaching a new PyTorch skill.

## What Is PyTorch?

PyTorch is three things:

1. **A tensor library** — like NumPy but with GPU support
2. **An automatic differentiation engine** — computes gradients for you
3. **A neural network toolkit** — layers, optimizers, data loaders

```python
import torch

# 1. Tensors (like NumPy arrays, but on GPU)
x = torch.tensor([1.0, 2.0, 3.0])
y = x ** 2  # [1, 4, 9]

# 2. Autograd (automatic gradients)
x = torch.tensor([2.0], requires_grad=True)
y = x ** 3  # y = x³
y.backward()  # dy/dx = 3x² = 12
print(x.grad)  # tensor([12.])

# 3. Neural networks
import torch.nn as nn
model = nn.Linear(10, 1)  # 10 inputs → 1 output
output = model(torch.randn(1, 10))
```

## The Mental Model

```
┌─────────────────────────────────────────────┐
│  Your Code (Python)                          │
│  model = MyNet()                             │
│  loss = criterion(output, target)            │
│  loss.backward()                             │
│  optimizer.step()                            │
└─────────────────────────────────────────────┘
         ↕ (Python objects, debuggable)
┌─────────────────────────────────────────────┐
│  PyTorch (C++/CUDA under the hood)           │
│  Tensor operations, autograd engine,         │
│  GPU kernels, memory management              │
└─────────────────────────────────────────────┘
         ↕
┌─────────────────────────────────────────────┐
│  Hardware (CPU / GPU)                        │
│  Matrix multiplications at 100 TFLOPS        │
└─────────────────────────────────────────────┘
```

You write Python. PyTorch handles the math on the GPU. You can inspect everything at every step — that's what makes it great for research.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Research Engineer | Learns by building |
| **Mara** | CTO | "Print the tensor shapes. Always." |
| **Client** | Various | Has a problem, needs a model |
| **The GPU** | NVIDIA A100 | Fast but unforgiving about memory |

## Prerequisites

### Install PyTorch

```bash
# CPU only (works everywhere)
pip install torch torchvision torchaudio

# With CUDA (NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verify

```python
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Quick tensor test
a = torch.randn(3, 4)
b = torch.randn(4, 5)
c = a @ b  # Matrix multiply
print(f"(3,4) @ (4,5) = {c.shape}")  # torch.Size([3, 5])

# Autograd test
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1  # y = x² + 2x + 1
y.backward()
print(f"dy/dx at x=3: {x.grad.item()}")  # 2*3 + 2 = 8
```

### What You Need to Know

- **Python basics**: functions, classes, list comprehensions, f-strings
- **NumPy familiarity** (helpful but not required — PyTorch is similar)
- **Math**: what a derivative is (slope of a curve), what matrix multiplication does

You do NOT need:
- Deep learning theory (we'll learn it as we build)
- GPU programming experience
- A PhD

## PyTorch vs TensorFlow

| | PyTorch | TensorFlow |
|---|---|---|
| Execution | Eager (like Python) | Graph-based (compiled) |
| Debugging | print(), pdb, normal Python | Harder to inspect |
| Research | Dominant (90%+ of papers) | Declining in research |
| Production | Growing (TorchServe, ONNX) | Mature (TF Serving) |
| Learning curve | Gentle (it's just Python) | Steeper (sessions, graphs) |

We use PyTorch because it's Python. If you can write a for loop, you can write a training loop.

## The Roadmap

| Ch | The Project | The PyTorch Skill |
|---|---|---|
| 1 | Image brightness tool | Tensor creation, indexing, reshaping |
| 2 | Curve fitting | Autograd, gradients, optimization |
| 3 | Digit classifier | nn.Module, layers, forward pass |
| 4 | Sentiment model | Training loop, loss, optimizer |
| 5 | Image pipeline | Dataset, DataLoader, transforms |
| 6 | Object detector | CNNs, transfer learning |
| 7 | Stock predictor | RNNs, LSTM, sequences |
| 8 | Text classifier | Transformers, attention |
| 9 | GAN for faces | Custom training, multiple models |
| 10 | Model registry | Saving, loading, exporting |
| 11 | Real-time inference | GPU optimization, profiling |
| 12 | Production API | Deployment, quantization |

## Mara's Rules

1. **Print shapes** — `print(x.shape)` after every operation until it's second nature
2. **Start small** — get it working on 10 samples before scaling to 10 million
3. **Read errors carefully** — PyTorch errors tell you exactly what's wrong (usually shape mismatch)
4. **Use `.detach()`** — when you want a value without the computational graph

Let's create some tensors.

---

[Chapter 1: Tensors →](chapter-01-tensors.md)
