---
title: "Chapter 4: RNNs for Text"
description: "Recurrent Neural Networks for sequence data"
---

# Chapter 4: RNNs for Text

## LSTM for Sentiment Analysis

```python
import torch
import torch.nn as nn

class SentimentLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        embedded = self.dropout(self.embedding(x))
        _, (hidden, _) = self.lstm(embedded)
        # Concatenate forward and backward hidden states
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        return self.fc(self.dropout(hidden))

model = SentimentLSTM(vocab_size=10000, embed_dim=128, hidden_dim=256, output_dim=2)
```

## Text Preprocessing

```python
from collections import Counter

def build_vocab(texts, max_vocab=10000):
    counter = Counter()
    for text in texts:
        counter.update(text.lower().split())
    vocab = {"<pad>": 0, "<unk>": 1}
    for word, _ in counter.most_common(max_vocab - 2):
        vocab[word] = len(vocab)
    return vocab

def encode(text, vocab, max_len=100):
    tokens = text.lower().split()
    ids = [vocab.get(t, 1) for t in tokens[:max_len]]
    ids += [0] * (max_len - len(ids))  # pad
    return torch.tensor(ids)
```

## Training

```python
# Synthetic example
texts = ["great movie loved it", "terrible waste of time"] * 500
labels = [1, 0] * 500
vocab = build_vocab(texts)

X = torch.stack([encode(t, vocab) for t in texts])
y = torch.tensor(labels)

dataset = torch.utils.data.TensorDataset(X, y)
loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    model.train()
    total_loss = 0
    for batch_x, batch_y in loader:
        optimizer.zero_grad()
        loss = criterion(model(batch_x), batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    if epoch % 3 == 0:
        print(f"Epoch {epoch}, Loss: {total_loss/len(loader):.4f}")
```

## Exercises

1. Implement a GRU-based model and compare performance with LSTM.
2. Add attention mechanism to weight important words in the sequence.
3. Build a character-level text generator using an LSTM.

---

[← prev](./chapter-03-cnn.md) | [next →](./chapter-05-transfer.md)
