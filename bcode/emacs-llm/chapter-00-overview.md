# Chapter 0 — Overview & Setup

[Next → Chapter 1: Get the Data](chapter-01-data.md)

---

## What We're Building

A local LLM trained on the Emacs manual that answers questions like:

```
$ emacs-llm "how do I swap two windows?"
> Use C-x 4 0 or the command `window-swap-states` to swap...
```

We build **everything** from scratch: tokenizer, transformer, training loop, RAG pipeline, and CLI tool.

---

## Episode Guide

| # | Chapter | Key Concept |
|---|---------|-------------|
| 0 | Overview & Setup | This file |
| 1 | Get the Data | Download + parse Emacs manual |
| 2 | Chunk the Text | Overlapping passages |
| 3 | Build the Retriever | BM25 + embeddings |
| 4 | Train a Tokenizer | BPE from scratch |
| 5 | Embeddings | Tensors + nn.Embedding |
| 6 | Self-Attention | Matmul + Softmax |
| 7 | Transformer Block | nn.Module + Linear + LayerNorm |
| 8 | Full Model Assembly | nn.ModuleList composition |
| 9 | Loss & Optimizer | CrossEntropy + Adam + autograd |
| 10 | Training Loop | Dataset + DataLoader |
| 11 | Text Generation | inference_mode + sampling |
| 12 | Fine-Tune for Q&A | save/load state_dict |
| 13 | RAG Pipeline | Retriever + Model combined |
| 14 | Quantize & Ship | INT8 + CLI packaging |

---

## Prerequisites

- Python 3.10+
- Basic Python knowledge (loops, functions, classes)
- **No PyTorch knowledge needed** — we teach every concept inline
- An internet connection (to download the Emacs manual)
- ~4 GB disk space

---

## Setup

```bash
mkdir emacs-llm && cd emacs-llm
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install tokenizers sentence-transformers rank-bm25
pip install requests beautifulsoup4
```

Create the project structure:

```bash
mkdir -p data src
touch src/__init__.py
```

---

## How Each Chapter Works

Every chapter from 5 onward follows the same pattern:

1. **PyTorch Concept** — a minimal ~10-line example teaching ONE idea
2. **Applying It** — use that concept to build the next piece of our LLM
3. **What You Learned** — summary of both the concept and the build step

Code blocks stay under ~20 lines. No magic, no hand-waving.

---

## What You Learned

- The full roadmap: 14 chapters from raw text to working CLI
- Project structure and dependencies
- PyTorch concepts are taught inline — no separate tutorials needed

---

[Next → Chapter 1: Get the Data](chapter-01-data.md)
