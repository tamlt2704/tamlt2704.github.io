# Chapter 12: Deployment

[← Chapter 11: GPU and Performance](chapter-11-gpu.md) | [Back to Overview →](README.md)

---

## The Project

Client: a fintech company has a fraud detection model that works in notebooks. They need it running in production — handling 10,000 requests/second with <50ms latency. No more "it works on my machine."

Mara: "A model that can't be deployed is a model that doesn't exist. TorchScript for portability, ONNX for speed, quantization for edge devices, and an API to tie it all together."

## TorchScript: Portable Models

```python
import torch
import torch.nn as nn

class FraudDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(30, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return torch.sigmoid(self.net(x))

model = FraudDetector()
model.eval()

# Method 1: Tracing (records operations with example input)
example_input = torch.randn(1, 30)
traced_model = torch.jit.trace(model, example_input)
traced_model.save("fraud_traced.pt")

# Method 2: Scripting (parses Python code, supports control flow)
scripted_model = torch.jit.script(model)
scripted_model.save("fraud_scripted.pt")

# Load without Python — works in C++, mobile, etc.
loaded = torch.jit.load("fraud_scripted.pt")
output = loaded(torch.randn(1, 30))
print(f"Prediction: {output.item():.4f}")
```

## ONNX Export

```python
model = FraudDetector()
model.eval()

dummy_input = torch.randn(1, 30)
torch.onnx.export(
    model, dummy_input, "fraud.onnx",
    input_names=['features'],
    output_names=['fraud_probability'],
    dynamic_axes={'features': {0: 'batch'}, 'fraud_probability': {0: 'batch'}},
    opset_version=17
)

# Run with ONNX Runtime (2-5x faster than PyTorch for inference)
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("fraud.onnx")
input_data = np.random.randn(1, 30).astype(np.float32)
result = session.run(None, {'features': input_data})
print(f"ONNX prediction: {result[0][0][0]:.4f}")
```

## Quantization: Smaller and Faster

```python
import torch.quantization

model = FraudDetector()
model.eval()

# Dynamic quantization (easiest — quantizes weights, activations at runtime)
quantized_model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)

# Compare sizes
import os
torch.save(model.state_dict(), '/tmp/original.pth')
torch.save(quantized_model.state_dict(), '/tmp/quantized.pth')
orig_size = os.path.getsize('/tmp/original.pth')
quant_size = os.path.getsize('/tmp/quantized.pth')
print(f"Original: {orig_size/1024:.1f} KB")
print(f"Quantized: {quant_size/1024:.1f} KB")
print(f"Reduction: {(1 - quant_size/orig_size)*100:.1f}%")

# Static quantization (calibrate with representative data)
model.qconfig = torch.quantization.get_default_qconfig('x86')
prepared = torch.quantization.prepare(model)
# Run calibration data through prepared model...
# calibration_data = torch.randn(100, 30)
# prepared(calibration_data)
static_quantized = torch.quantization.convert(prepared)
```

## Serving with FastAPI

```python
# serve.py
from fastapi import FastAPI
import torch
import numpy as np
from pydantic import BaseModel

app = FastAPI()

# Load model once at startup
model = torch.jit.load("fraud_scripted.pt")
model.eval()

class Transaction(BaseModel):
    features: list[float]  # 30 features

class Prediction(BaseModel):
    fraud_probability: float
    is_fraud: bool

@app.post("/predict", response_model=Prediction)
async def predict(transaction: Transaction):
    with torch.no_grad():
        tensor = torch.tensor([transaction.features], dtype=torch.float32)
        prob = model(tensor).item()
    return Prediction(
        fraud_probability=prob,
        is_fraud=prob > 0.5
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "fraud_detector_v1"}

# Run: uvicorn serve:app --host 0.0.0.0 --port 8000
```

## The Client Project: Production Fraud API

```python
import torch
import torch.nn as nn
import time
import numpy as np

class FraudDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(30, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return torch.sigmoid(self.net(x))

# Train (simplified)
model = FraudDetector()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.BCELoss()

# Simulate training data
X_train = torch.randn(10000, 30)
y_train = torch.randint(0, 2, (10000, 1)).float()

model.train()
for epoch in range(5):
    pred = model(X_train)
    loss = loss_fn(pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
print(f"Training done. Final loss: {loss.item():.4f}")

# --- Deployment Pipeline ---
model.eval()

# 1. Export TorchScript
scripted = torch.jit.script(model)
scripted.save("fraud_production.pt")

# 2. Export ONNX
torch.onnx.export(model, torch.randn(1, 30), "fraud_production.onnx",
                  input_names=['features'], output_names=['probability'],
                  dynamic_axes={'features': {0: 'batch'}})

# 3. Quantize for CPU deployment
quantized = torch.quantization.quantize_dynamic(model, {nn.Linear}, torch.qint8)

# 4. Benchmark all variants
def benchmark_model(m, x, runs=1000):
    with torch.no_grad():
        for _ in range(10):  # warmup
            m(x)
        start = time.perf_counter()
        for _ in range(runs):
            m(x)
        elapsed = time.perf_counter() - start
    return elapsed / runs * 1000  # ms per inference

test_input = torch.randn(1, 30)
print(f"\nLatency (1 sample):")
print(f"  Original:   {benchmark_model(model, test_input):.3f} ms")
print(f"  TorchScript: {benchmark_model(scripted, test_input):.3f} ms")
print(f"  Quantized:  {benchmark_model(quantized, test_input):.3f} ms")

# Batch throughput
batch_input = torch.randn(256, 30)
print(f"\nLatency (256 batch):")
print(f"  Original:   {benchmark_model(model, batch_input):.3f} ms")
print(f"  TorchScript: {benchmark_model(scripted, batch_input):.3f} ms")
print(f"  Quantized:  {benchmark_model(quantized, batch_input):.3f} ms")
```

## What You Learned

- **TorchScript** — `torch.jit.trace` (simple) or `torch.jit.script` (control flow)
- **ONNX** — cross-platform format, fast inference with onnxruntime
- **Dynamic quantization** — int8 weights, ~2-4x smaller, faster on CPU
- **Static quantization** — calibrate with data for best accuracy
- **FastAPI serving** — load model once, serve predictions via REST
- **Benchmarking** — always measure latency and throughput before shipping

You've gone from tensors to production. The fraud detector is deployed, quantized, and serving 10k req/s. The journey from `torch.tensor([1.0])` to a production API is complete.

---

[← Chapter 11: GPU and Performance](chapter-11-gpu.md) | [Back to Overview →](README.md)
