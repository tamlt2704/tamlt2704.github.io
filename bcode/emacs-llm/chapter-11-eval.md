# Chapter 11 — Text Generation

[← Chapter 10: Training Loop](chapter-10-quantize.md) | [Next → Chapter 12: Fine-Tune for Q&A](chapter-12-ship.md)

---

## Goal

Learn inference_mode and sampling strategies, then build a generate() function.

---

## PyTorch Concept: torch.inference_mode + Sampling

### inference_mode

Disables gradient tracking — faster and uses less memory during generation.

```python
import torch

model = ...  # trained model

# Without inference_mode: PyTorch tracks ops for backprop (wasteful)
# With inference_mode: pure forward pass, no gradient overhead
with torch.inference_mode():
    output = model(input_ids)
    # Can't call .backward() here — and we don't want to
```

### Top-k Sampling

Instead of always picking the highest-probability token (greedy), sample from the top-k most likely tokens for variety.

```python
import torch.nn.functional as F

def top_k_sample(logits, k=40, temperature=0.8):
    """Sample from top-k tokens with temperature scaling."""
    logits = logits / temperature
    top_values, top_indices = logits.topk(k)
    probs = F.softmax(top_values, dim=-1)
    choice = torch.multinomial(probs, 1)
    return top_indices.gather(-1, choice)
```

---

## Applying It: The Generate Function

```python
# src/generate.py
import torch
import torch.nn.functional as F
from tokenizers import Tokenizer
from model.gpt import EmacsGPT

def generate(prompt, max_tokens=100, top_k=40, temperature=0.8):
    tokenizer = Tokenizer.from_file("data/tokenizer.json")
    model = EmacsGPT()
    model.load_state_dict(torch.load("data/emacs-gpt.pt"))
    model.eval()

    ids = tokenizer.encode(prompt).ids
    ids = torch.tensor([ids])  # add batch dim

    with torch.inference_mode():
        for _ in range(max_tokens):
            logits = model(ids[:, -512:])  # keep within max_len
            next_logits = logits[0, -1]    # last position

            # Top-k sampling
            top_vals, top_idx = next_logits.topk(top_k)
            probs = F.softmax(top_vals / temperature, dim=-1)
            choice = torch.multinomial(probs, 1)
            next_id = top_idx[choice]

            ids = torch.cat([ids, next_id.unsqueeze(0)], dim=1)

    return tokenizer.decode(ids[0].tolist())
```

---

## Try It

```python
if __name__ == "__main__":
    text = generate("To switch buffers in Emacs,")
    print(text)
    # To switch buffers in Emacs, use C-x b. This prompts for
    # the buffer name in the minibuffer. You can use completion...
```

---

## Temperature Effects

| Temperature | Behavior |
|-------------|----------|
| 0.2 | Very focused, repetitive |
| 0.8 | Balanced creativity (default) |
| 1.5 | Wild, often incoherent |

---

## What You Learned

- **PyTorch concept**: `torch.inference_mode()` for fast, no-grad forward passes; top-k sampling for diverse outputs
- **Build step**: Token-by-token generation loop with temperature control
- The model can now produce Emacs-related text given a prompt

---

[← Chapter 10: Training Loop](chapter-10-quantize.md) | [Next → Chapter 12: Fine-Tune for Q&A](chapter-12-ship.md)
