# Emacs LLM — Build a Local Q&A Model From Scratch

Build a CPU-friendly Q&A system trained on the Emacs manual. No prior PyTorch knowledge needed — each chapter teaches exactly the PyTorch concept it uses, right before using it.

## The Goal

```
You: How do I swap two windows?
Bot: Use C-x o to switch to the other window. To swap buffer 
     positions, use window-swap-states (Emacs 28+).
```

Local. CPU only. Sub-second. Trained on the Emacs manual.

## Architecture: RAG + Small Transformer

```
Question → Retrieve relevant passages → Small model answers from context
```

## Episodes

Each chapter introduces ONE new PyTorch concept alongside the LLM building step.

| # | Build Step | PyTorch Concept Introduced |
|---|---|---|
| 00 | Overview & Setup | — |
| 01 | Download & parse Emacs manual | — (pure Python) |
| 02 | Chunk text into passages | — (pure Python) |
| 03 | Build retriever (BM25 + embeddings) | — (using libraries) |
| 04 | Train a BPE tokenizer | — (using `tokenizers` lib) |
| 05 | Tensors & the embedding layer | **Tensors, Embedding** |
| 06 | Self-attention mechanism | **Matrix ops, Softmax** |
| 07 | Transformer block (FFN + LayerNorm) | **nn.Module, Linear, ReLU** |
| 08 | Full model assembly | **Composing modules** |
| 09 | Loss & optimizer | **CrossEntropyLoss, Adam, autograd** |
| 10 | Training loop | **DataLoader, training loop pattern** |
| 11 | Text generation | **inference_mode, sampling** |
| 12 | Fine-tune for Q&A | **Save/Load, fine-tuning** |
| 13 | RAG pipeline | **Combining retriever + model** |
| 14 | Quantize & ship | **Quantization, CLI packaging** |

## Prerequisites

- Python 3.11+, 8GB+ RAM, no GPU needed
- No PyTorch experience required — taught inline

## Install

```bash
uv python install 3.12
uv init emacs-llm --python 3.12
cd emacs-llm
uv add torch --index-url https://download.pytorch.org/whl/cpu
uv add numpy tokenizers sentence-transformers rank-bm25
```
