# Chapter 8: Transformers

[← Chapter 7: RNNs](chapter-07-rnn.md) | [Chapter 9: Custom Training →](chapter-09-custom.md)

---

## The Project

Client: a legal tech company needs a document classifier. Documents are long (500+ tokens). RNNs are too slow — they process one token at a time. Transformers process all tokens in parallel using attention.

Mara: "Attention is just a weighted average. Each token asks: 'which other tokens should I pay attention to?' That's it. The rest is engineering."

## Self-Attention from Scratch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def self_attention(Q, K, V, mask=None):
    """Scaled dot-product attention."""
    d_k = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)  # (batch, seq, seq)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    weights = F.softmax(scores, dim=-1)  # Attention weights
    return weights @ V  # Weighted sum of values

# Example: 2 sequences, 10 tokens, embedding dim 64
batch_size, seq_len, d_model = 2, 10, 64
x = torch.randn(batch_size, seq_len, d_model)

# Q, K, V are linear projections of input
W_q = nn.Linear(d_model, d_model)
W_k = nn.Linear(d_model, d_model)
W_v = nn.Linear(d_model, d_model)

Q, K, V = W_q(x), W_k(x), W_v(x)
output = self_attention(Q, K, V)
print(output.shape)  # (2, 10, 64)
```

## nn.MultiheadAttention

```python
# PyTorch's built-in multi-head attention
mha = nn.MultiheadAttention(embed_dim=64, num_heads=8, batch_first=True)

x = torch.randn(2, 10, 64)  # (batch, seq, embed)
attn_output, attn_weights = mha(x, x, x)  # Self-attention: Q=K=V=x
print(attn_output.shape)   # (2, 10, 64)
print(attn_weights.shape)  # (2, 10, 10) — attention matrix
```

## Positional Encoding

Transformers have no notion of order. Positional encoding adds position info:

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                             -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

## Transformer Encoder Block

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model=128, num_heads=8, ff_dim=256, dropout=0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            nn.GELU(),
            nn.Linear(ff_dim, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Self-attention + residual
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))
        # Feedforward + residual
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout(ff_out))
        return x
```

## The Client Project: Document Classifier

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

VOCAB_SIZE = 15000
MAX_LEN = 200
NUM_CLASSES = 6  # Contract types

class DocumentDataset(Dataset):
    def __init__(self, num_docs=3000):
        self.tokens = torch.randint(0, VOCAB_SIZE, (num_docs, MAX_LEN))
        self.labels = torch.randint(0, NUM_CLASSES, (num_docs,))

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.tokens[idx], self.labels[idx]

class DocumentClassifier(nn.Module):
    def __init__(self, vocab_size=VOCAB_SIZE, d_model=128, num_heads=8,
                 num_layers=4, num_classes=NUM_CLASSES):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, MAX_LEN)
        self.encoder = nn.Sequential(
            *[TransformerBlock(d_model, num_heads) for _ in range(num_layers)]
        )
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, x):
        x = self.embedding(x)           # (batch, seq, d_model)
        x = self.pos_encoding(x)
        x = self.encoder(x)             # (batch, seq, d_model)
        x = x.mean(dim=1)              # Global average pooling
        return self.classifier(x)       # (batch, num_classes)

# Training
train_set = DocumentDataset(2400)
val_set = DocumentDataset(600)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
val_loader = DataLoader(val_set, batch_size=32)

model = DocumentClassifier()
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(5):
    model.train()
    total_loss = 0
    for tokens, labels in train_loader:
        logits = model(tokens)
        loss = loss_fn(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for tokens, labels in val_loader:
            preds = model(tokens).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    print(f"Epoch {epoch+1}: loss={total_loss/len(train_loader):.4f} "
          f"val_acc={correct/total:.4f}")

print(f"\nModel params: {sum(p.numel() for p in model.parameters()):,}")
```

## What You Learned

- **Self-attention** — each token attends to all others (weighted average)
- **Scaled dot-product** — Q·K^T / √d_k prevents gradient explosion
- **Multi-head attention** — multiple attention patterns in parallel
- **Positional encoding** — sin/cos signals inject position information
- **Transformer block** — attention + feedforward + residual + layer norm
- **Global pooling** — average over sequence for classification

The transformer works. But some projects need more control — custom losses, multiple models training together, adversarial objectives. That's custom training.

---

[← Chapter 7: RNNs](chapter-07-rnn.md) | [Chapter 9: Custom Training →](chapter-09-custom.md)
