# Chapter 1: Tokenization

[prev: Overview](chapter-00-overview.md) | [next: Embeddings](chapter-02-embeddings.md)

Tokenization converts raw text into a sequence of integers that the model can process. The choice of tokenizer directly affects vocabulary size, sequence length, and what the model can represent.

## Tokenization Strategies

### Character-Level

Every character is a token. Simple but produces very long sequences.

```python
text = "hello world"
# Character-level: each char is a token
chars = sorted(set(text))
char_to_id = {c: i for i, c in enumerate(chars)}
id_to_char = {i: c for c, i in char_to_id.items()}

encoded = [char_to_id[c] for c in text]
decoded = "".join(id_to_char[i] for i in encoded)
print(f"Vocab size: {len(chars)}")   # 8
print(f"Encoded: {encoded}")          # [2, 1, 4, 4, 5, 0, 7, 5, 6, 4, 0]
print(f"Decoded: {decoded}")          # "hello world"
```

**Pros**: Tiny vocabulary (256 for UTF-8 bytes), handles any text.
**Cons**: Very long sequences, hard to learn word-level patterns.

### Word-Level

Split on whitespace/punctuation. Each word is a token.

```python
text = "The cat sat on the mat."
tokens = text.lower().split()
vocab = sorted(set(tokens))
word_to_id = {w: i for i, w in enumerate(vocab)}

encoded = [word_to_id[w] for w in tokens]
print(f"Vocab size: {len(vocab)}")  # 5
print(f"Tokens: {tokens}")          # ['the', 'cat', 'sat', 'on', 'the', 'mat.']
```

**Pros**: Short sequences, semantically meaningful tokens.
**Cons**: Huge vocabulary, cannot handle unseen words (OOV problem).

### Subword (BPE) — The Standard

Byte Pair Encoding finds a middle ground: common words stay whole, rare words split into subword pieces.

`"unhappiness"` → `["un", "happiness"]` or `["un", "happ", "iness"]`

## Implementing BPE from Scratch

```python
from collections import Counter, defaultdict

class BPETokenizer:
    def __init__(self, vocab_size=300):
        self.vocab_size = vocab_size
        self.merges = {}       # (pair) -> new_token
        self.vocab = {}        # id -> bytes

    def _get_stats(self, token_ids_list):
        """Count frequency of adjacent pairs across all words."""
        counts = Counter()
        for token_ids in token_ids_list:
            for i in range(len(token_ids) - 1):
                counts[(token_ids[i], token_ids[i + 1])] += 1
        return counts

    def _merge(self, token_ids, pair, new_id):
        """Replace all occurrences of pair with new_id."""
        result = []
        i = 0
        while i < len(token_ids):
            if i < len(token_ids) - 1 and (token_ids[i], token_ids[i + 1]) == pair:
                result.append(new_id)
                i += 2
            else:
                result.append(token_ids[i])
                i += 1
        return result

    def train(self, text):
        """Train BPE on text corpus."""
        # Start with raw bytes as initial tokens
        tokens = list(text.encode("utf-8"))
        token_ids_list = [tokens]

        # Initialize vocab with single bytes (0-255)
        self.vocab = {i: bytes([i]) for i in range(256)}
        next_id = 256

        while next_id < self.vocab_size:
            stats = self._get_stats(token_ids_list)
            if not stats:
                break

            # Find most frequent pair
            best_pair = max(stats, key=stats.get)

            # Create new token by merging the pair
            self.merges[best_pair] = next_id
            self.vocab[next_id] = self.vocab[best_pair[0]] + self.vocab[best_pair[1]]

            # Apply merge to all sequences
            token_ids_list = [
                self._merge(ids, best_pair, next_id) for ids in token_ids_list
            ]
            next_id += 1

        print(f"Trained BPE: {len(self.merges)} merges, vocab size {len(self.vocab)}")

    def encode(self, text):
        """Encode text to token IDs."""
        token_ids = list(text.encode("utf-8"))
        for pair, new_id in self.merges.items():
            token_ids = self._merge(token_ids, pair, new_id)
        return token_ids

    def decode(self, token_ids):
        """Decode token IDs back to text."""
        raw_bytes = b"".join(self.vocab[id] for id in token_ids)
        return raw_bytes.decode("utf-8", errors="replace")
```

### Training and Using the Tokenizer

```python
# Train on sample text
corpus = "the cat sat on the mat. the cat is happy. the dog sat on the mat."
tokenizer = BPETokenizer(vocab_size=280)
tokenizer.train(corpus)

# Encode and decode
text = "the cat sat"
ids = tokenizer.encode(text)
recovered = tokenizer.decode(ids)
print(f"Text: '{text}'")
print(f"Token IDs: {ids}")
print(f"Decoded: '{recovered}'")
print(f"Compression: {len(text.encode('utf-8'))} bytes -> {len(ids)} tokens")
```

## Special Tokens

Special tokens provide structure that the model needs for generation and batching:

```python
class Tokenizer:
    """Tokenizer with special token support."""

    SPECIAL_TOKENS = {
        "<PAD>": 0,   # Padding for batch alignment
        "<UNK>": 1,   # Unknown/out-of-vocabulary
        "<BOS>": 2,   # Beginning of sequence
        "<EOS>": 3,   # End of sequence
    }

    def __init__(self, bpe_tokenizer):
        self.bpe = bpe_tokenizer
        # Offset BPE IDs to make room for special tokens
        self.offset = len(self.SPECIAL_TOKENS)
        self.vocab_size = self.bpe.vocab_size + self.offset

    def encode(self, text, add_special=True):
        ids = [id + self.offset for id in self.bpe.encode(text)]
        if add_special:
            ids = [self.SPECIAL_TOKENS["<BOS>"]] + ids + [self.SPECIAL_TOKENS["<EOS>"]]
        return ids

    def decode(self, ids):
        # Filter out special tokens
        filtered = [id - self.offset for id in ids if id >= self.offset]
        return self.bpe.decode(filtered)

    @property
    def pad_id(self):
        return self.SPECIAL_TOKENS["<PAD>"]

    @property
    def bos_id(self):
        return self.SPECIAL_TOKENS["<BOS>"]

    @property
    def eos_id(self):
        return self.SPECIAL_TOKENS["<EOS>"]
```

### Padding Sequences for Batching

```python
import torch

def pad_sequences(sequences, pad_id=0):
    """Pad sequences to same length for batching."""
    max_len = max(len(s) for s in sequences)
    padded = []
    attention_mask = []
    for seq in sequences:
        pad_len = max_len - len(seq)
        padded.append(seq + [pad_id] * pad_len)
        attention_mask.append([1] * len(seq) + [0] * pad_len)
    return torch.tensor(padded), torch.tensor(attention_mask)
    # padded shape: (batch_size, max_len)
    # attention_mask shape: (batch_size, max_len)

# Example
sequences = [[2, 10, 11, 12, 3], [2, 20, 21, 3]]
tokens, mask = pad_sequences(sequences)
print(f"Tokens:\n{tokens}")
print(f"Mask:\n{mask}")
```

## Using tiktoken (OpenAI)

tiktoken is the production BPE tokenizer used by GPT models:

```python
import tiktoken

# GPT-2 tokenizer
enc = tiktoken.get_encoding("gpt2")
text = "Hello, world! This is a test."
ids = enc.encode(text)
decoded = enc.decode(ids)
print(f"Tokens: {ids}")
print(f"Num tokens: {len(ids)}")
print(f"Decoded: {decoded}")

# GPT-4 tokenizer (cl100k_base)
enc4 = tiktoken.get_encoding("cl100k_base")
ids4 = enc4.encode(text)
print(f"GPT-4 tokens: {len(ids4)}")  # Usually fewer tokens (larger vocab)
```

## Using SentencePiece (Google)

SentencePiece trains directly on raw text (no pre-tokenization):

```python
import sentencepiece as spm

# Train a sentencepiece model
# spm.SentencePieceTrainer.train(
#     input='corpus.txt',
#     model_prefix='sp_model',
#     vocab_size=32000,
#     model_type='bpe'
# )

# Load and use
# sp = spm.SentencePieceProcessor(model_file='sp_model.model')
# ids = sp.encode("Hello world", out_type=int)
# text = sp.decode(ids)
```

## tiktoken vs SentencePiece

| Feature          | tiktoken                 | SentencePiece                   |
| ---------------- | ------------------------ | ------------------------------- |
| Used by          | OpenAI (GPT-2/3/4)       | Google (T5), Meta (LLaMA)       |
| Pre-tokenization | Regex split first        | Trains on raw text              |
| Speed            | Very fast (Rust backend) | Fast (C++ backend)              |
| Unicode          | Byte-level BPE           | Native Unicode or byte-fallback |
| Training         | Pre-trained vocabs only  | Train your own                  |
| Vocab sizes      | 50k-100k                 | Configurable                    |

## Key Takeaways

- BPE balances vocabulary size with sequence length
- Start from bytes (256 base tokens), iteratively merge frequent pairs
- Special tokens give the model structural signals
- Production models use tiktoken or SentencePiece
- Larger vocabularies = shorter sequences but bigger embedding matrices
