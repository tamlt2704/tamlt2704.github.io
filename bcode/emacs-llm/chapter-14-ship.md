# Chapter 14 — Quantize & Ship

[← Chapter 13: RAG Pipeline](chapter-13-rag.md)

---

## Goal

Learn INT8 quantization for speed, then package everything as a CLI tool.

---

## PyTorch Concept: torch.quantization (INT8)

### Dynamic Quantization

Converts float32 weights to int8 at inference time — ~2× faster, ~4× smaller, minimal quality loss.

```python
import torch
import torch.nn as nn

model = nn.Linear(256, 256)

# One line: quantize Linear layers to INT8
quantized = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)

# Compare sizes
import sys
orig_size = sys.getsizeof(torch.save(model.state_dict(), "/dev/null"))
print(f"Original params dtype: {next(model.parameters()).dtype}")
print("Quantized model runs ~2x faster on CPU")
```

---

## Applying It: Quantize EmacsGPT

```python
# src/quantize.py
import torch
import torch.nn as nn
from model.gpt import EmacsGPT

# Load trained model
model = EmacsGPT()
model.load_state_dict(torch.load("data/emacs-gpt-qa.pt"))
model.eval()

# Quantize all Linear layers to INT8
quantized_model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)

# Save quantized model
torch.save(quantized_model.state_dict(), "data/emacs-gpt-q8.pt")

# Compare file sizes
import os
orig = os.path.getsize("data/emacs-gpt-qa.pt") / 1e6
quant = os.path.getsize("data/emacs-gpt-q8.pt") / 1e6
print(f"Original: {orig:.1f} MB → Quantized: {quant:.1f} MB")
# Original: 21.0 MB → Quantized: 6.2 MB
```

---

## Package as CLI Tool

```python
# src/cli.py
"""emacs-llm: Ask questions about Emacs from the command line."""
import argparse
from rag import rag_answer

def main():
    parser = argparse.ArgumentParser(description="Ask Emacs questions")
    parser.add_argument("question", help="Your question about Emacs")
    parser.add_argument("--top-k", type=int, default=3, help="Chunks to retrieve")
    parser.add_argument("--max-tokens", type=int, default=150)
    args = parser.parse_args()

    answer = rag_answer(args.question, top_k=args.top_k, max_tokens=args.max_tokens)
    print(answer)

if __name__ == "__main__":
    main()
```

---

## Make It Installable

```toml
# pyproject.toml
[project]
name = "emacs-llm"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "torch",
    "tokenizers",
    "sentence-transformers",
    "rank-bm25",
    "beautifulsoup4",
    "requests",
]

[project.scripts]
emacs-llm = "src.cli:main"
```

```bash
pip install -e .
emacs-llm "how do I swap two windows?"
# Use window-swap-states or C-x 4 0 to swap the buffers in two windows.
```

---

## Final Architecture

```
User question
    │
    ├─→ BM25 + Semantic Retriever → top-3 chunks
    │
    ├─→ Format prompt with context
    │
    └─→ Quantized EmacsGPT → generated answer
```

---

## What You Learned

- **PyTorch concept**: `quantize_dynamic` converts to INT8 for ~2× speedup and ~3× size reduction
- **Build step**: Packaged the full pipeline as an installable CLI tool
- You built an LLM from scratch: tokenizer → transformer → training → RAG → shipping

---

## 🎉 Course Complete!

You've built a working LLM from raw text to CLI tool. Here's what you created:

1. Custom BPE tokenizer trained on Emacs text
2. 5.2M parameter transformer (from scratch, no libraries)
3. Training loop that runs on CPU
4. Fine-tuned Q&A model
5. Hybrid RAG retriever
6. Quantized INT8 model
7. Installable CLI tool

Every PyTorch concept was taught inline, exactly when you needed it. No prerequisites, no separate tutorials.

---

[← Chapter 13: RAG Pipeline](chapter-13-rag.md)
