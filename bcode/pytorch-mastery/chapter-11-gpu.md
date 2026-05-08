# Chapter 11: GPU and Performance

[← Chapter 10: Saving and Loading](chapter-10-checkpoints.md) | [Chapter 12: Deployment →](chapter-12-deployment.md)

---

## The Project

Client: a self-driving car company needs real-time inference — 30fps on video streams. Their model runs at 5fps on CPU. You need GPU acceleration, mixed precision, and compilation to hit the target.

The GPU (NVIDIA A100): "Feed me batches. Big ones. I have 80GB of memory and 6,912 CUDA cores sitting idle."

## .to(device): Moving to GPU

```python
import torch
import torch.nn as nn

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using: {device}")

# Move model to GPU
model = nn.Linear(1000, 100).to(device)

# Move data to GPU
x = torch.randn(64, 1000).to(device)
output = model(x)  # Computed on GPU

# Check where tensors live
print(x.device)       # cuda:0
print(output.device)  # cuda:0

# Common mistake: mixing devices
# x_cpu = torch.randn(64, 1000)
# model(x_cpu)  # RuntimeError: expected device cuda:0
```

## DataParallel: Multiple GPUs

```python
model = nn.Linear(1000, 100).to(device)

# Wrap for multi-GPU (splits batch across GPUs)
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = nn.DataParallel(model)

# DistributedDataParallel is preferred for serious training
# (requires torch.distributed setup — more complex but faster)
```

## Mixed Precision with torch.amp

Float16 is 2x faster and uses half the memory. But some ops need float32 for stability:

```python
from torch.amp import autocast, GradScaler

model = nn.Sequential(
    nn.Linear(784, 256), nn.ReLU(),
    nn.Linear(256, 10)
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scaler = GradScaler('cuda')  # Prevents underflow in float16 gradients

for epoch in range(10):
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)

        # Forward pass in mixed precision
        with autocast('cuda'):
            output = model(x)
            loss = nn.functional.cross_entropy(output, y)

        # Backward with gradient scaling
        optimizer.zero_grad()
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

## torch.compile: PyTorch 2.0 Compiler

```python
model = nn.Sequential(
    nn.Linear(784, 256), nn.ReLU(),
    nn.Linear(256, 128), nn.ReLU(),
    nn.Linear(128, 10)
).to(device)

# Compile the model — fuses operations, reduces overhead
compiled_model = torch.compile(model)

# First call is slow (compilation), subsequent calls are fast
x = torch.randn(64, 784, device=device)
output = compiled_model(x)  # Compiled execution

# Modes:
# torch.compile(model, mode="default")      — balanced
# torch.compile(model, mode="reduce-overhead")  — minimize CPU overhead
# torch.compile(model, mode="max-autotune")     — slowest compile, fastest run
```

## Profiling: Find Bottlenecks

```python
from torch.profiler import profile, record_function, ProfilerActivity

model = nn.Linear(1000, 100).to(device)
x = torch.randn(64, 1000, device=device)

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    with record_function("model_inference"):
        for _ in range(100):
            output = model(x)

print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
```

## The Client Project: Real-Time Inference Pipeline

```python
import torch
import torch.nn as nn
from torch.amp import autocast
import time

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class VisionModel(nn.Module):
    """Simplified model for real-time video processing."""
    def __init__(self, num_classes=20):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = x.flatten(1)
        return self.classifier(x)

# Setup
model = VisionModel().to(device)
model.eval()

# Compile for maximum speed
compiled_model = torch.compile(model, mode="reduce-overhead")

# Benchmark function
def benchmark(model, input_tensor, num_runs=100, warmup=10):
    # Warmup
    for _ in range(warmup):
        with torch.no_grad():
            model(input_tensor)
    if device.type == 'cuda':
        torch.cuda.synchronize()

    start = time.perf_counter()
    for _ in range(num_runs):
        with torch.no_grad():
            with autocast('cuda'):
                model(input_tensor)
    if device.type == 'cuda':
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    fps = num_runs / elapsed
    ms_per_frame = elapsed / num_runs * 1000
    return fps, ms_per_frame

# Simulate video frames
frames = torch.randn(1, 3, 224, 224, device=device)

# Benchmark
fps, latency = benchmark(compiled_model, frames)
print(f"Throughput: {fps:.1f} FPS")
print(f"Latency: {latency:.2f} ms/frame")
print(f"Target: 30 FPS = 33.3 ms/frame")
print(f"{'✓ Target met!' if fps >= 30 else '✗ Need more optimization'}")

# Memory usage
if device.type == 'cuda':
    print(f"\nGPU memory allocated: {torch.cuda.memory_allocated()/1e6:.1f} MB")
    print(f"GPU memory cached: {torch.cuda.memory_reserved()/1e6:.1f} MB")
```

## What You Learned

- **.to(device)** — move models and tensors to GPU
- **DataParallel** — split batches across multiple GPUs
- **torch.amp** — mixed precision (float16 forward, float32 gradients)
- **GradScaler** — prevents gradient underflow in float16
- **torch.compile** — PyTorch 2.0 compiler, fuses ops for speed
- **Profiler** — find CPU/GPU bottlenecks
- **torch.cuda.synchronize()** — wait for GPU before timing

The model is fast. Now ship it to production — TorchScript, ONNX, quantization, and serving behind an API.

---

[← Chapter 10: Saving and Loading](chapter-10-checkpoints.md) | [Chapter 12: Deployment →](chapter-12-deployment.md)
