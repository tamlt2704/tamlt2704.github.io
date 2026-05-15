# Chapter 13 — RAG Pipeline

[← Chapter 12: Fine-Tune for Q&A](chapter-12-ship.md) | [Next → Chapter 14: Quantize & Ship](chapter-14-ship.md)

---

## Goal

Combine the retriever (Chapter 3) with the model (Chapter 11) into a full RAG pipeline.

---

## No New PyTorch Concept

This chapter is pure integration — connecting pieces we already built.

---

## The RAG Idea

Without RAG, the model can only answer from what it memorized during training. With RAG:

1. **Retrieve** relevant chunks from the manual
2. **Format** them as context in the prompt
3. **Generate** an answer grounded in the retrieved text

This means the model can answer questions about content it hasn't memorized perfectly.

---

## Build the RAG Pipeline

```python
# src/rag.py
from retriever import retrieve
from generate import generate

def rag_answer(question, top_k=3, max_tokens=150):
    """Retrieve context, format prompt, generate answer."""
    # Step 1: Retrieve relevant chunks
    results = retrieve(question, top_k=top_k)
    context = "\n---\n".join(chunk for chunk, score in results)

    # Step 2: Format prompt with context
    prompt = (
        f"Context:\n{context}\n\n"
        f"Q: {question}\n"
        f"A:"
    )

    # Step 3: Generate answer
    answer = generate(prompt, max_tokens=max_tokens, temperature=0.5)

    # Extract just the answer part
    answer_text = answer.split("A:")[-1].strip()
    return answer_text
```

---

## Demo

```python
if __name__ == "__main__":
    questions = [
        "How do I swap two windows?",
        "What is the kill ring?",
        "How do I run a shell command?",
    ]

    for q in questions:
        print(f"Q: {q}")
        print(f"A: {rag_answer(q)}")
        print()
```

```bash
python src/rag.py
# Q: How do I swap two windows?
# A: Use `window-swap-states` or C-x 4 0 to swap the buffers
#    displayed in two windows.
#
# Q: What is the kill ring?
# A: The kill ring stores text you've killed (cut). Use C-y to
#    yank the most recent kill, and M-y to cycle through older ones.
```

---

## Why Lower Temperature?

We use `temperature=0.5` for RAG because we want factual, grounded answers — not creative text. The context provides the facts; the model just needs to summarize them.

---

## RAG vs Pure Generation

| Approach | Pros | Cons |
|----------|------|------|
| Pure generation | Fast, no retrieval step | Hallucinates, limited to training data |
| RAG | Grounded, can cite sources | Slower, depends on retrieval quality |

---

## What You Learned

- RAG = Retrieve + Augment prompt + Generate
- Lower temperature for factual Q&A
- The retriever from Chapter 3 and generator from Chapter 11 combine into a working system

---

[← Chapter 12: Fine-Tune for Q&A](chapter-12-ship.md) | [Next → Chapter 14: Quantize & Ship](chapter-14-ship.md)
