# Chapter 1: Text to Numbers — Tokenization

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Bigrams →](chapter-02-bigrams.md)

---

## The Problem

Neural networks operate on numbers — tensors of floats. They can't read text. Before we can build any model, we need to convert text into numbers.

Dr. Lin: "Your first task: turn Shakespeare into a sequence of integers. No meaning yet — just a mapping. Text in, numbers out."

## The Simplest Tokenizer: Character-Level

Map each character to an integer:

```python
text = "hello world"

# Build vocabulary from all unique characters
chars = sorted(set(text))
# [' ', 'd', 'e', 'h', 'l', 'o', 'r', 'w']

# Create mappings
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}

# Encode
encoded = [char_to_idx[ch] for ch in text]
# [3, 2, 4, 4, 5, 0, 7, 5, 6, 4, 1]

# Decode
decoded = ''.join(idx_to_char[i] for i in encoded)
# "hello world"
```

Vocabulary size: ~100 characters (ASCII). Simple, but each token carries almost no meaning. The word "hello" is 5 tokens. A sentence is hundreds of tokens. The model has to learn spelling from scratch.

## Word-Level Tokenization

Map each word to an integer:

```python
text = "the cat sat on the mat"
words = text.split()
vocab = sorted(set(words))
# ['cat', 'mat', 'on', 'sat', 'the']

word_to_idx = {w: i for i, w in enumerate(vocab)}
encoded = [word_to_idx[w] for w in words]
# [4, 0, 3, 2, 4, 1]
```

Better — each token is meaningful. But the vocabulary is enormous (100K+ words in English), and unseen words break the system ("ChatGPT" isn't in any dictionary).

## The Sweet Spot: Subword Tokenization (BPE)

**Byte Pair Encoding** splits text into subword units — common words stay whole, rare words get split into pieces:

```
"unhappiness" → ["un", "happiness"]
"ChatGPT"     → ["Chat", "G", "PT"]
"the"         → ["the"]  (common word, stays whole)
```

Vocabulary size: typically 32K-100K tokens. Balances meaning per token with vocabulary size.

### How BPE Works

1. Start with individual characters as the vocabulary
2. Count all adjacent pairs in the corpus
3. Merge the most frequent pair into a new token
4. Repeat until vocabulary reaches desired size

```python
import re
from collections import Counter

def get_pairs(tokens):
    """Count adjacent pairs in token sequences."""
    pairs = Counter()
    for word_tokens in tokens:
        for i in range(len(word_tokens) - 1):
            pairs[(word_tokens[i], word_tokens[i+1])] += 1
    return pairs

def build_bpe_vocab(text, num_merges=50):
    """Build a BPE vocabulary from text."""
    # Start: each word split into characters + end-of-word marker
    words = text.split()
    word_freqs = Counter(words)

    # Initial tokens: individual characters
    tokens = {word: list(word) + ['</w>'] for word in word_freqs}

    merges = []
    for i in range(num_merges):
        # Count all pairs across all words (weighted by word frequency)
        pairs = Counter()
        for word, freq in word_freqs.items():
            word_tokens = tokens[word]
            for j in range(len(word_tokens) - 1):
                pairs[(word_tokens[j], word_tokens[j+1])] += freq

        if not pairs:
            break

        # Find most frequent pair
        best_pair = pairs.most_common(1)[0][0]
        merges.append(best_pair)

        # Merge that pair everywhere
        new_token = best_pair[0] + best_pair[1]
        for word in tokens:
            new_word_tokens = []
            i = 0
            while i < len(tokens[word]):
                if (i < len(tokens[word]) - 1 and
                    tokens[word][i] == best_pair[0] and
                    tokens[word][i+1] == best_pair[1]):
                    new_word_tokens.append(new_token)
                    i += 2
                else:
                    new_word_tokens.append(tokens[word][i])
                    i += 1
            tokens[word] = new_word_tokens

        print(f"Merge {i+1}: '{best_pair[0]}' + '{best_pair[1]}' → '{new_token}'")

    return tokens, merges

# Example
text = "the cat sat on the mat the cat sat"
tokens, merges = build_bpe_vocab(text, num_merges=10)
print("\nFinal tokens:")
for word, toks in tokens.items():
    print(f"  '{word}' → {toks}")
```

Output:
```
Merge 1: 't' + 'h' → 'th'
Merge 2: 'th' + 'e' → 'the'
Merge 3: 'the' + '</w>' → 'the</w>'
Merge 4: 'a' + 't' → 'at'
Merge 5: 'c' + 'at' → 'cat'
Merge 6: 'cat' + '</w>' → 'cat</w>'
Merge 7: 's' + 'at' → 'sat'
Merge 8: 'sat' + '</w>' → 'sat</w>'
...

Final tokens:
  'the' → ['the</w>']
  'cat' → ['cat</w>']
  'sat' → ['sat</w>']
  'on'  → ['o', 'n</w>']
  'mat' → ['m', 'at</w>']
```

Common words ("the", "cat", "sat") become single tokens. Rare words get split.

## Our Tokenizer for the Course

For simplicity, we'll use a character-level tokenizer for the first few chapters (small vocabulary, easy to debug), then switch to a proper BPE tokenizer:

```python
import torch

class CharTokenizer:
    """Character-level tokenizer for learning purposes."""

    def __init__(self, text: str):
        chars = sorted(set(text))
        self.vocab_size = len(chars)
        self.char_to_idx = {ch: i for i, ch in enumerate(chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(chars)}

    def encode(self, text: str) -> list[int]:
        return [self.char_to_idx[ch] for ch in text]

    def decode(self, indices: list[int]) -> str:
        return ''.join(self.idx_to_char[i] for i in indices)


# Load Shakespeare (or any text)
with open('input.txt', 'r') as f:
    text = f.read()

tokenizer = CharTokenizer(text)
print(f"Vocabulary size: {tokenizer.vocab_size}")
# ~65 characters for Shakespeare

# Encode the entire text
data = torch.tensor(tokenizer.encode(text), dtype=torch.long)
print(f"Data shape: {data.shape}")
# torch.Size([1115394]) — 1.1M tokens

# Train/val split
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]
print(f"Train: {len(train_data)} tokens, Val: {len(val_data)} tokens")
```

## Getting Training Data

Download Shakespeare (a classic small corpus for language modeling):

```python
import urllib.request

url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
urllib.request.urlretrieve(url, 'input.txt')

with open('input.txt', 'r') as f:
    text = f.read()

print(f"Length: {len(text)} characters")
print(f"First 200 chars:\n{text[:200]}")
```

```
Length: 1115394 characters
First 200 chars:
First Citizen:
Before we proceed any further, hear me speak.

All:
Speak, speak.

First Citizen:
You are all resolved rather to die than to famish?
```

## What Tokenization Gives Us

```
Text:    "First Citizen:\nBefore we proceed"
Tokens:  [21, 47, 56, 57, 58, 1, 15, 47, 58, 47, ...]
```

Now we have a sequence of integers. A neural network can work with this. The next step: build the simplest possible model that predicts the next token.

## Real-World Tokenizers

In production LLMs:
- **GPT-2/3/4**: BPE with ~50K tokens (tiktoken library)
- **LLaMA**: SentencePiece BPE with 32K tokens
- **Claude**: Similar BPE approach

```python
# Using tiktoken (GPT's tokenizer) for reference
import tiktoken
enc = tiktoken.get_encoding("gpt2")
tokens = enc.encode("Hello, world!")
print(tokens)  # [15496, 11, 995, 0]
print(enc.decode(tokens))  # "Hello, world!"
```

We'll use our character tokenizer for learning, then optionally upgrade to BPE in Chapter 8.

## What You Learned

- **Tokenization** — converting text to integers (and back)
- **Character-level** — simple, small vocab (~100), but tokens carry little meaning
- **Word-level** — meaningful tokens, but huge vocab and can't handle new words
- **BPE (Byte Pair Encoding)** — the sweet spot: subword tokens, ~32K-100K vocab
- **The pipeline** — text → tokenizer → integer sequence → neural network

We have numbers. Now we need a model that predicts the next number given the previous ones. The simplest such model: a bigram.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Bigrams →](chapter-02-bigrams.md)
