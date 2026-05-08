# LLM From Scratch — Building a Language Model With Your Own Hands

A narrative-driven course on building a large language model from the ground up. You're a machine learning engineer at **TinyMind**, a research lab that believes you can't truly understand LLMs until you've built one yourself — from raw text to a model that generates coherent sentences.

## Episodes

| # | Title | The Milestone | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, the big picture, what an LLM actually is |
| 01 | [Text to Numbers](chapter-01-tokenization.md) | Tokenizer works | Tokenization, BPE, vocabulary building |
| 02 | [Predicting the Next Token](chapter-02-bigrams.md) | Bigram model generates text | Language modeling basics, probability, loss |
| 03 | [Embeddings](chapter-03-embeddings.md) | Words become vectors | Word embeddings, lookup tables, similarity |
| 04 | [Attention Is All You Need](chapter-04-attention.md) | Self-attention works | Attention mechanism, Q/K/V, scaled dot-product |
| 05 | [The Transformer Block](chapter-05-transformer.md) | One transformer block runs | Multi-head attention, feed-forward, LayerNorm, residuals |
| 06 | [Stacking Blocks](chapter-06-gpt.md) | Full GPT architecture | Positional encoding, stacking layers, the full model |
| 07 | [Training Loop](chapter-07-training.md) | Model trains and loss decreases | Backprop, AdamW, learning rate schedule, gradient clipping |
| 08 | [Data Pipeline](chapter-08-data.md) | Training on real text | Dataset preparation, batching, context windows |
| 09 | [Generation](chapter-09-generation.md) | Model generates text | Sampling, temperature, top-k, top-p, beam search |
| 10 | [Scaling Up](chapter-10-scaling.md) | Bigger model, better results | Scaling laws, GPU training, mixed precision, distributed |
| 11 | [Fine-Tuning](chapter-11-finetuning.md) | Model follows instructions | SFT, LoRA, instruction tuning, RLHF overview |
| 12 | [Evaluation & Ship](chapter-12-eval.md) | Model is evaluated and deployed | Perplexity, benchmarks, inference optimization, deployment |

## Prerequisites

- Python 3.10+
- PyTorch 2.0+
- Basic calculus (derivatives) and linear algebra (matrix multiplication)
- A GPU is helpful but not required for the small models we build

## Philosophy

Every concept is introduced because the current model is too dumb. You'll see the failure first — garbage output, exploding loss, incoherent text — then learn the technique that fixes it. The broken model comes first. The better model follows.
