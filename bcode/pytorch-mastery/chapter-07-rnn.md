# Chapter 7: RNNs and Sequences

[← Chapter 6: CNNs](chapter-06-cnn.md) | [Chapter 8: Transformers →](chapter-08-transformers.md)

---

## The Project

Client: a hedge fund wants a stock price predictor. Given 30 days of price history, predict the next day's closing price. The data is sequential — order matters. Yesterday's price affects today's prediction.

Mara: "RNNs have memory. They process one timestep at a time, carrying a hidden state forward. LSTMs are RNNs that actually remember long-term patterns."

## nn.RNN: The Basics

```python
import torch
import torch.nn as nn

# RNN(input_size, hidden_size, num_layers)
rnn = nn.RNN(input_size=10, hidden_size=32, num_layers=1, batch_first=True)

# Input: (batch, seq_len, input_size)
x = torch.randn(4, 20, 10)  # 4 sequences, 20 timesteps, 10 features

# Output: all hidden states + final hidden state
output, h_n = rnn(x)
print(output.shape)  # (4, 20, 32) — hidden state at each timestep
print(h_n.shape)     # (1, 4, 32) — final hidden state (num_layers, batch, hidden)
```

## nn.LSTM: Long Short-Term Memory

LSTMs solve the vanishing gradient problem with gates:

```python
lstm = nn.LSTM(input_size=10, hidden_size=64, num_layers=2,
               batch_first=True, dropout=0.2)

x = torch.randn(4, 30, 10)  # 4 sequences, 30 timesteps
output, (h_n, c_n) = lstm(x)

print(output.shape)  # (4, 30, 64) — all hidden states
print(h_n.shape)     # (2, 4, 64) — final hidden per layer
print(c_n.shape)     # (2, 4, 64) — final cell state per layer
```

## nn.GRU: Simpler Alternative

```python
gru = nn.GRU(input_size=10, hidden_size=64, num_layers=2,
             batch_first=True, dropout=0.2)

x = torch.randn(4, 30, 10)
output, h_n = gru(x)  # No cell state (simpler than LSTM)
print(output.shape)  # (4, 30, 64)
```

## Packing Variable-Length Sequences

Real sequences have different lengths. Padding wastes computation:

```python
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

# Sequences of different lengths (already padded)
sequences = torch.randn(3, 10, 5)  # 3 sequences, max_len=10, features=5
lengths = torch.tensor([10, 7, 4])  # Actual lengths

# Pack: skip padding during computation
packed = pack_padded_sequence(sequences, lengths, batch_first=True,
                              enforce_sorted=False)

# Run through LSTM
lstm = nn.LSTM(5, 32, batch_first=True)
packed_output, (h_n, c_n) = lstm(packed)

# Unpack back to padded
output, output_lengths = pad_packed_sequence(packed_output, batch_first=True)
print(output.shape)  # (3, 10, 32) — padded output
```

## The Client Project: Stock Price Predictor

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Generate synthetic stock data
torch.manual_seed(42)
def generate_stock_data(num_days=1000):
    """Simulate stock prices with trend + noise."""
    trend = torch.linspace(100, 150, num_days)
    noise = torch.randn(num_days) * 2
    seasonal = 5 * torch.sin(torch.arange(num_days).float() * 0.1)
    return trend + noise + seasonal

class StockDataset(Dataset):
    def __init__(self, prices, window=30):
        self.window = window
        self.prices = prices
        # Normalize
        self.mean = prices.mean()
        self.std = prices.std()
        self.normalized = (prices - self.mean) / self.std

    def __len__(self):
        return len(self.prices) - self.window

    def __getitem__(self, idx):
        x = self.normalized[idx:idx + self.window].unsqueeze(-1)  # (30, 1)
        y = self.normalized[idx + self.window]                     # scalar
        return x, y

class StockPredictor(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        output, (h_n, c_n) = self.lstm(x)
        # Use last hidden state
        last_hidden = output[:, -1, :]  # (batch, hidden_size)
        return self.fc(last_hidden).squeeze(-1)  # (batch,)

# Setup
prices = generate_stock_data(1000)
train_prices = prices[:800]
val_prices = prices[800:]

train_set = StockDataset(train_prices, window=30)
val_set = StockDataset(val_prices, window=30)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
val_loader = DataLoader(val_set, batch_size=32)

model = StockPredictor()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()

# Train
for epoch in range(20):
    model.train()
    train_loss = 0
    for x, y in train_loader:
        pred = model(x)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    if (epoch + 1) % 5 == 0:
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for x, y in val_loader:
                val_loss += loss_fn(model(x), y).item()
        print(f"Epoch {epoch+1}: train={train_loss/len(train_loader):.4f} "
              f"val={val_loss/len(val_loader):.4f}")
```

## What You Learned

- **nn.RNN** — basic recurrent layer, processes sequences step by step
- **nn.LSTM** — gates prevent vanishing gradients, remembers long patterns
- **nn.GRU** — simpler than LSTM, often similar performance
- **Hidden state** — the "memory" passed between timesteps
- **batch_first=True** — input shape is (batch, seq, features)
- **Packing** — skip padded positions for efficiency
- **Last hidden state** — common to use `output[:, -1, :]` for classification/regression

RNNs process sequences one step at a time — slow for long sequences. Transformers process all positions in parallel using attention. That's next.

---

[← Chapter 6: CNNs](chapter-06-cnn.md) | [Chapter 8: Transformers →](chapter-08-transformers.md)
