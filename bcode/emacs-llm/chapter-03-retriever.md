# Chapter 3 — Build the Retriever

[← Chapter 2: Chunk the Text](chapter-02-chunking.md) | [Next → Chapter 4: Train a Tokenizer](chapter-04-tokenizer.md)

---

## Goal

Build a hybrid retriever (BM25 + semantic embeddings) that finds relevant chunks for a query.

---

## Why Hybrid?

- **BM25** catches exact keyword matches ("C-x 4 0")
- **Semantic embeddings** catch meaning ("swap windows" → "exchange buffer positions")
- Combining both gives better recall than either alone

---

## Build the Index

```python
# src/retriever.py
import json
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Load chunks
chunks = json.loads(Path("data/chunks.json").read_text())
tokenized = [c.lower().split() for c in chunks]

# BM25 index
bm25 = BM25Okapi(tokenized)

# Semantic index
embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(chunks, show_progress_bar=True)
np.save("data/embeddings.npy", embeddings)
print(f"Indexed {len(chunks)} chunks")
```

---

## Hybrid Retrieval Function

```python
def retrieve(query, top_k=5):
    """Combine BM25 + cosine similarity, return top-k chunks."""
    # BM25 scores
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_scores = bm25_scores / (bm25_scores.max() + 1e-8)

    # Semantic scores
    q_emb = embedder.encode([query])
    cos_scores = (embeddings @ q_emb.T).squeeze()
    cos_scores = cos_scores / (cos_scores.max() + 1e-8)

    # Combine (equal weight)
    combined = 0.5 * bm25_scores + 0.5 * cos_scores
    top_idx = combined.argsort()[-top_k:][::-1]

    return [(chunks[i], float(combined[i])) for i in top_idx]
```

---

## Test It

```python
if __name__ == "__main__":
    results = retrieve("how to swap windows")
    for chunk, score in results:
        print(f"[{score:.3f}] {chunk[:80]}...")
```

```bash
python src/retriever.py
# [0.847] ...exchange the positions of two windows using C-x 4 0...
# [0.791] ...window-swap-states swaps the buffers displayed...
```

---

## What You Learned

- BM25 handles keyword matching; sentence-transformers handle semantics
- Normalizing + averaging scores gives a simple but effective hybrid
- Output: working `retrieve()` function we'll plug into RAG in Chapter 13

---

[← Chapter 2: Chunk the Text](chapter-02-chunking.md) | [Next → Chapter 4: Train a Tokenizer](chapter-04-tokenizer.md)
