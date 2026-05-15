# Chapter 12 — Fine-Tune for Q&A

[← Chapter 11: Text Generation](chapter-11-eval.md) | [Next → Chapter 13: RAG Pipeline](chapter-13-rag.md)

---

## Goal

Learn torch.save/load for checkpoints, then fine-tune EmacsGPT on question-answer pairs.

---

## PyTorch Concept: torch.save / torch.load

### Save a Checkpoint

`state_dict()` captures all learnable parameters as a dictionary.

```python
import torch
import torch.nn as nn

model = nn.Linear(4, 2)

# Save
torch.save(model.state_dict(), "checkpoint.pt")

# Load into a new model (same architecture)
new_model = nn.Linear(4, 2)
new_model.load_state_dict(torch.load("checkpoint.pt"))
print("Loaded successfully!")
```

Always save `state_dict()` (not the whole model) — it's portable and architecture-independent.

---

## Applying It: Create Q&A Training Data

We format Q&A pairs so the model learns the pattern: `Q: ... A: ...`

```python
# src/qa_data.py
import json

qa_pairs = [
    ("How do I save a file?", "Use C-x C-s to save the current buffer to its file."),
    ("How do I quit Emacs?", "Use C-x C-c to exit Emacs."),
    ("How do I undo?", "Use C-/ or C-x u to undo the last change."),
    ("How do I search?", "Use C-s for incremental forward search."),
    ("How do I open a file?", "Use C-x C-f to visit a file."),
    # ... add 50-100 pairs from the manual
]

def format_qa(pairs):
    """Format as single strings for next-token prediction."""
    return [f"Q: {q}\nA: {a}\n<eos>" for q, a in pairs]

formatted = format_qa(qa_pairs)
json.dump(formatted, open("data/qa_pairs.json", "w"), indent=2)
print(f"Created {len(formatted)} Q&A training examples")
```

---

## Fine-Tune on Q&A

```python
# src/finetune.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tokenizers import Tokenizer
from model.gpt import EmacsGPT
import json

# Load pretrained model
model = EmacsGPT()
model.load_state_dict(torch.load("data/emacs-gpt.pt"))

tokenizer = Tokenizer.from_file("data/tokenizer.json")
qa_texts = json.load(open("data/qa_pairs.json"))

# Tokenize all Q&A pairs
all_ids = [tokenizer.encode(t).ids for t in qa_texts]

# Fine-tune with lower learning rate
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(10):
    total_loss = 0
    for ids in all_ids:
        x = torch.tensor([ids[:-1]])
        y = torch.tensor([ids[1:]])
        logits = model(x)
        loss = loss_fn(logits.view(-1, 8192), y.view(-1))
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    print(f"Epoch {epoch} loss: {total_loss / len(all_ids):.4f}")

torch.save(model.state_dict(), "data/emacs-gpt-qa.pt")
print("Fine-tuned model saved!")
```

---

## Test the Fine-Tuned Model

```python
from generate import generate

answer = generate("Q: How do I split the window?\nA:")
print(answer)
# A: Use C-x 2 to split the current window vertically, or C-x 3 for horizontal.
```

---

## What You Learned

- **PyTorch concept**: `torch.save(state_dict)` / `torch.load` for portable checkpoints
- **Build step**: Fine-tuned EmacsGPT on Q&A pairs with lower learning rate
- The model now responds in Q&A format, not just free-form text completion

---

[← Chapter 11: Text Generation](chapter-11-eval.md) | [Next → Chapter 13: RAG Pipeline](chapter-13-rag.md)
