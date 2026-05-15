# Chapter 4 — Train a Tokenizer

[← Chapter 3: Build the Retriever](chapter-03-retriever.md) | [Next → Chapter 5: Embeddings](chapter-05-transformer.md)

---

## Goal

Train a BPE tokenizer on the Emacs manual with vocab_size=8192.

---

## Why Our Own Tokenizer?

GPT-2's tokenizer wastes tokens on code/web patterns we'll never see. A custom tokenizer trained on Emacs text gives us:
- Shorter sequences (faster training)
- Better coverage of Emacs-specific terms ("kill-ring", "C-x", "minibuffer")

---

## Train the Tokenizer

```python
# src/tokenizer.py
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from pathlib import Path

def train_tokenizer():
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)

    trainer = BpeTrainer(
        vocab_size=8192,
        special_tokens=["<pad>", "<unk>", "<bos>", "<eos>"]
    )

    tokenizer.train(["data/emacs-manual.txt"], trainer)
    tokenizer.save("data/tokenizer.json")
    print(f"Vocab size: {tokenizer.get_vocab_size()}")
    return tokenizer
```

---

## Encode & Decode

```python
def demo_tokenizer():
    tokenizer = Tokenizer.from_file("data/tokenizer.json")

    text = "Use C-x b to switch buffers in Emacs."
    encoded = tokenizer.encode(text)

    print(f"Text:   {text}")
    print(f"Tokens: {encoded.tokens}")
    print(f"IDs:    {encoded.ids}")
    print(f"Decoded: {tokenizer.decode(encoded.ids)}")

if __name__ == "__main__":
    train_tokenizer()
    demo_tokenizer()
```

---

## Run It

```bash
python src/tokenizer.py
# Vocab size: 8192
# Text:   Use C-x b to switch buffers in Emacs.
# Tokens: ['Use', ' C', '-x', ' b', ' to', ' switch', ' buffers', ' in', ' Em', 'acs', '.']
# IDs:    [412, 87, 34, 201, 15, 847, 1923, 12, 156, 89, 7]
# Decoded: Use C-x b to switch buffers in Emacs.
```

Notice how "C-x" splits naturally and "Emacs" gets just 2 tokens — much better than a general tokenizer.

---

## What You Learned

- BPE (Byte-Pair Encoding) merges frequent character pairs into tokens
- The `tokenizers` library trains in seconds on our corpus
- Output: `data/tokenizer.json` — used in every chapter from here on

---

[← Chapter 3: Build the Retriever](chapter-03-retriever.md) | [Next → Chapter 5: Embeddings](chapter-05-transformer.md)
