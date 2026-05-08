# PyTorch Mastery — From Tensors to Production Models

A narrative-driven course on PyTorch. You're a research engineer at **DeepForge**, a startup building custom ML models for clients. Each chapter is a client project that requires a new PyTorch skill — from basic tensor operations to distributed training.

## Episodes

| # | Title | The Project | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, tensors, GPU, the mental model |
| 01 | [Tensors Are Everything](chapter-01-tensors.md) | Image brightness tool | Creating, indexing, reshaping, broadcasting |
| 02 | [Autograd: Automatic Differentiation](chapter-02-autograd.md) | Curve fitting | Gradients, computational graph, backward() |
| 03 | [Building Neural Networks](chapter-03-nn-module.md) | Digit classifier | nn.Module, layers, forward(), parameters |
| 04 | [Training Loop](chapter-04-training.md) | Sentiment model | Loss, optimizer, epochs, train/eval modes |
| 05 | [Data Loading](chapter-05-data.md) | Image pipeline | Dataset, DataLoader, transforms, augmentation |
| 06 | [CNNs: Seeing Patterns](chapter-06-cnn.md) | Object detector | Conv2d, pooling, feature maps, transfer learning |
| 07 | [RNNs and Sequences](chapter-07-rnn.md) | Stock predictor | RNN, LSTM, GRU, sequence modeling |
| 08 | [Transformers](chapter-08-transformers.md) | Text classifier | Self-attention, positional encoding, encoder |
| 09 | [Custom Training](chapter-09-custom.md) | GAN for faces | Custom losses, multiple optimizers, training tricks |
| 10 | [Saving and Loading](chapter-10-checkpoints.md) | Model registry | state_dict, checkpoints, ONNX export |
| 11 | [GPU and Performance](chapter-11-gpu.md) | Real-time inference | CUDA, mixed precision, profiling, torch.compile |
| 12 | [Deployment](chapter-12-deployment.md) | Production API | TorchScript, ONNX, quantization, serving |

## Prerequisites

- Python 3.10+
- PyTorch 2.0+ (`pip install torch torchvision`)
- Basic Python (functions, classes, list comprehensions)
- High school math (algebra, basic calculus intuition)

## Philosophy

Every PyTorch feature is introduced because a project requires it. You'll hit the wall first — slow training, wrong shapes, GPU errors — then learn the tool that fixes it. The error comes first. The solution follows.
