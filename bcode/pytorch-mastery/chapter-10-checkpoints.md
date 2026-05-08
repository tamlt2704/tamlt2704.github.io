# Chapter 10: Saving and Loading

[← Chapter 9: Custom Training](chapter-09-custom.md) | [Chapter 11: GPU and Performance →](chapter-11-gpu.md)

---

## The Project

Client: a healthcare company trains models for 48 hours. If training crashes at hour 47, they lose everything. They need a model registry — save checkpoints during training, resume from crashes, and export final models for deployment.

Mara: "Always save `state_dict`, never the model object. And always save the optimizer state too — Adam has momentum buffers that matter."

## state_dict: The Model's Weights

```python
import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)

# state_dict is an OrderedDict of parameter name → tensor
print(model.state_dict().keys())
# odict_keys(['0.weight', '0.bias', '2.weight', '2.bias'])

# Save just the weights
torch.save(model.state_dict(), 'model_weights.pth')

# Load into a new model (same architecture required)
new_model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)
new_model.load_state_dict(torch.load('model_weights.pth', weights_only=True))
```

## Full Checkpoint: Resume Training

```python
def save_checkpoint(model, optimizer, epoch, loss, path):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, path)

def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path, weights_only=True)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'], checkpoint['loss']
```

## Checkpointing During Training

```python
model = nn.Linear(100, 10)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

best_val_loss = float('inf')

for epoch in range(100):
    # ... training loop ...
    train_loss = 0.0  # placeholder

    # Validate
    val_loss = 0.0  # placeholder

    # Save best model
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_model.pth')
        print(f"Epoch {epoch}: new best model (val_loss={val_loss:.4f})")

    # Periodic checkpoint (for crash recovery)
    if epoch % 10 == 0:
        save_checkpoint(model, optimizer, epoch, train_loss,
                       f'checkpoint_epoch_{epoch}.pth')
```

## ONNX Export

ONNX (Open Neural Network Exchange) lets you run models in any runtime:

```python
import torch

model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 784)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'},
                  'output': {0: 'batch_size'}}
)
print("Exported to model.onnx")

# Verify with onnxruntime
# import onnxruntime as ort
# session = ort.InferenceSession("model.onnx")
# result = session.run(None, {'input': dummy_input.numpy()})
```

## The Client Project: Model Registry

```python
import torch
import torch.nn as nn
import os
import json
from datetime import datetime

class ModelRegistry:
    """Simple model registry for tracking experiments."""
    def __init__(self, registry_dir='./model_registry'):
        self.registry_dir = registry_dir
        os.makedirs(registry_dir, exist_ok=True)

    def save_model(self, model, optimizer, metadata):
        """Save model with metadata."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_dir = os.path.join(self.registry_dir, timestamp)
        os.makedirs(model_dir, exist_ok=True)

        # Save checkpoint
        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, os.path.join(model_dir, 'checkpoint.pth'))

        # Save metadata
        metadata['timestamp'] = timestamp
        metadata['num_params'] = sum(p.numel() for p in model.parameters())
        with open(os.path.join(model_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

        # Export ONNX
        model.eval()
        dummy = torch.randn(1, metadata.get('input_size', 784))
        torch.onnx.export(model, dummy, os.path.join(model_dir, 'model.onnx'),
                          input_names=['input'], output_names=['output'])

        print(f"Saved model to {model_dir}")
        return model_dir

    def load_model(self, model, optimizer, model_dir):
        """Load model from registry."""
        checkpoint = torch.load(
            os.path.join(model_dir, 'checkpoint.pth'), weights_only=True
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return model, optimizer

# Usage
model = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10))
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

registry = ModelRegistry()
registry.save_model(model, optimizer, {
    'input_size': 784,
    'task': 'digit_classification',
    'val_accuracy': 0.975,
    'epochs_trained': 20,
})
```

## What You Learned

- **state_dict** — dictionary mapping parameter names to tensors
- **torch.save / torch.load** — serialize any Python object (use `weights_only=True`)
- **Checkpointing** — save model + optimizer + epoch for crash recovery
- **Best model** — track validation loss, save when it improves
- **ONNX export** — portable format for cross-platform deployment
- **Model registry** — organize experiments with metadata and versioning

Models are saved. But training is slow on CPU. Next: GPU acceleration, mixed precision, and torch.compile.

---

[← Chapter 9: Custom Training](chapter-09-custom.md) | [Chapter 11: GPU and Performance →](chapter-11-gpu.md)
