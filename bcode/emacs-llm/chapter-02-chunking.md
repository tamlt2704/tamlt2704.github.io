# Chapter 2 — Chunk the Text

[← Chapter 1: Get the Data](chapter-01-data.md) | [Next → Chapter 3: Build the Retriever](chapter-03-retriever.md)

---

## Goal

Split the Emacs manual into overlapping passages of ~300 tokens for retrieval.

---

## Why Chunk?

A retriever needs bite-sized passages, not a 1.2M-character wall of text. Overlapping chunks ensure we don't cut a sentence in half and lose context at boundaries.

---

## The Chunking Function

```python
# src/chunker.py
import json
from pathlib import Path

def chunk_text(text, chunk_size=300, overlap=50):
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # step forward with overlap

    return chunks

if __name__ == "__main__":
    text = Path("data/emacs-manual.txt").read_text(encoding="utf-8")
    chunks = chunk_text(text)

    Path("data/chunks.json").write_text(
        json.dumps(chunks, indent=2), encoding="utf-8"
    )
    print(f"Created {len(chunks)} chunks (avg ~300 words each)")
```

---

## Run It

```bash
python src/chunker.py
# Created 847 chunks (avg ~300 words each)
```

---

## Inspect a Chunk

```python
import json
chunks = json.loads(open("data/chunks.json").read())
print(f"Chunk 42 ({len(chunks[42].split())} words):")
print(chunks[42][:200] + "...")
```

---

## Why 300 Words with 50 Overlap?

- **300 words** ≈ fits in a small model's context window
- **50-word overlap** ≈ one paragraph of shared context between neighbors
- These are starting values — tune later if retrieval quality is poor

---

## What You Learned

- Overlapping chunking preserves context at boundaries
- Simple word-based splitting works well for structured text
- Output: `data/chunks.json` — 800+ passages ready for indexing

---

[← Chapter 1: Get the Data](chapter-01-data.md) | [Next → Chapter 3: Build the Retriever](chapter-03-retriever.md)
