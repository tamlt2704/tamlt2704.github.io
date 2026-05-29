---
title: "Chapter 7: Deployment"
description: "Exporting and serving PyTorch models"
---

# Chapter 7: Deployment

## TorchScript Export

```python
import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

model = SimpleModel()
model.eval()

# Trace-based export
example_input = torch.randn(1, 10)
traced = torch.jit.trace(model, example_input)
traced.save("model_traced.pt")

# Load without Python
loaded = torch.jit.load("model_traced.pt")
output = loaded(example_input)
```

## ONNX Export

```python
torch.onnx.export(
    model,
    example_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
```

## FastAPI Serving

```python
# server.py
from fastapi import FastAPI
import torch
import numpy as np

app = FastAPI()
model = torch.jit.load("model_traced.pt")
model.eval()

@app.post("/predict")
async def predict(data: dict):
    input_tensor = torch.tensor(data["features"], dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
    prediction = output.argmax(dim=1).item()
    return {"prediction": prediction, "confidence": output.softmax(1).max().item()}

# Run: uvicorn server:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model_traced.pt server.py ./
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Exercises

1. Export a trained CNN to ONNX and run inference with `onnxruntime`.
2. Build a FastAPI endpoint that accepts an image and returns classification results.
3. Create a Docker container serving your model and test it with curl.

---

[← prev](./chapter-06-training.md) | [Overview](./chapter-00-overview.md)
