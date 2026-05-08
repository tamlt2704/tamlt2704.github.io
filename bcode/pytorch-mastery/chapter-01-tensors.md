# Chapter 1: Tensors Are Everything

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Autograd →](chapter-02-autograd.md)

---

## The Project

First client: a photography app needs a batch image brightness adjustment tool. Images are 3D arrays (height × width × channels). You need to manipulate them efficiently.

Mara: "Everything in PyTorch is a tensor. Images, text, audio, model weights — all tensors. Master tensors and you master PyTorch."

## What Is a Tensor?

A tensor is an n-dimensional array:

```python
import torch

# 0D tensor (scalar)
scalar = torch.tensor(42.0)
print(scalar.shape)  # torch.Size([])

# 1D tensor (vector)
vector = torch.tensor([1.0, 2.0, 3.0])
print(vector.shape)  # torch.Size([3])

# 2D tensor (matrix)
matrix = torch.tensor([[1, 2, 3], [4, 5, 6]])
print(matrix.shape)  # torch.Size([2, 3])

# 3D tensor (e.g., an RGB image: height × width × channels)
image = torch.randn(256, 256, 3)
print(image.shape)  # torch.Size([256, 256, 3])

# 4D tensor (batch of images: batch × channels × height × width)
batch = torch.randn(32, 3, 256, 256)
print(batch.shape)  # torch.Size([32, 3, 256, 256])
```

## Creating Tensors

```python
# From Python data
a = torch.tensor([1, 2, 3])
b = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

# Zeros and ones
zeros = torch.zeros(3, 4)       # 3×4 of zeros
ones = torch.ones(2, 3, 4)     # 2×3×4 of ones

# Random
uniform = torch.rand(3, 4)      # Uniform [0, 1)
normal = torch.randn(3, 4)     # Normal (mean=0, std=1)
integers = torch.randint(0, 10, (3, 4))  # Random ints [0, 10)

# Like another tensor (same shape and device)
x = torch.randn(3, 4)
y = torch.zeros_like(x)        # Same shape as x, filled with zeros
z = torch.randn_like(x)        # Same shape, random values

# Sequences
arange = torch.arange(0, 10, 2)     # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, 5)  # [0, 0.25, 0.5, 0.75, 1.0]

# Identity matrix
eye = torch.eye(4)  # 4×4 identity
```

## Data Types

```python
# Default: float32 for computation, int64 for indices
x = torch.tensor([1.0, 2.0])       # float32
y = torch.tensor([1, 2])           # int64

# Explicit dtype
f16 = torch.tensor([1.0], dtype=torch.float16)   # Half precision
f32 = torch.tensor([1.0], dtype=torch.float32)   # Single precision
f64 = torch.tensor([1.0], dtype=torch.float64)   # Double precision
i32 = torch.tensor([1], dtype=torch.int32)

# Cast
x = torch.tensor([1, 2, 3])
x_float = x.float()    # int64 → float32
x_half = x.half()      # → float16
x_int = x.int()        # → int32
```

## Indexing and Slicing

```python
x = torch.tensor([[1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12]])

# Basic indexing (same as NumPy)
x[0]        # tensor([1, 2, 3, 4]) — first row
x[0, 2]     # tensor(3) — row 0, col 2
x[:, 1]     # tensor([2, 6, 10]) — all rows, col 1
x[1:, :2]   # tensor([[5, 6], [9, 10]]) — rows 1+, first 2 cols

# Boolean indexing
mask = x > 5
x[mask]     # tensor([6, 7, 8, 9, 10, 11, 12])

# Fancy indexing
indices = torch.tensor([0, 2])
x[indices]  # tensor([[1, 2, 3, 4], [9, 10, 11, 12]]) — rows 0 and 2
```

## Reshaping

```python
x = torch.arange(12)  # [0, 1, 2, ..., 11]

# reshape / view
x.reshape(3, 4)    # 3 rows × 4 cols
x.reshape(2, 2, 3) # 2×2×3
x.reshape(-1, 4)   # -1 = infer this dimension → (3, 4)

# view (same as reshape but requires contiguous memory)
x.view(3, 4)

# Flatten
batch = torch.randn(32, 3, 28, 28)  # 32 images
flat = batch.view(32, -1)            # (32, 2352) — flatten each image
# or
flat = batch.flatten(start_dim=1)    # Same thing

# Squeeze / unsqueeze
x = torch.randn(1, 3, 1, 4)
x.squeeze()         # Remove all size-1 dims → (3, 4)
x.squeeze(0)        # Remove dim 0 only → (3, 1, 4)

y = torch.randn(3, 4)
y.unsqueeze(0)      # Add dim at position 0 → (1, 3, 4)
y.unsqueeze(-1)     # Add dim at end → (3, 4, 1)

# Transpose / permute
x = torch.randn(3, 4)
x.T                 # Transpose → (4, 3)
x.t()              # Same for 2D

img = torch.randn(256, 256, 3)  # H×W×C
img.permute(2, 0, 1)            # C×H×W (PyTorch convention)
```

## Operations

```python
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

# Element-wise
a + b       # [5, 7, 9]
a * b       # [4, 10, 18]
a ** 2      # [1, 4, 9]
torch.sqrt(a)  # [1.0, 1.41, 1.73]

# Reduction
a.sum()     # 6.0
a.mean()    # 2.0
a.max()     # 3.0
a.argmax()  # 2 (index of max)

# Matrix operations
A = torch.randn(3, 4)
B = torch.randn(4, 5)
C = A @ B           # Matrix multiply → (3, 5)
C = torch.matmul(A, B)  # Same thing

# Batch matrix multiply
batch_A = torch.randn(32, 3, 4)
batch_B = torch.randn(32, 4, 5)
batch_C = torch.bmm(batch_A, batch_B)  # (32, 3, 5)
```

## Broadcasting

When tensors have different shapes, PyTorch automatically expands them:

```python
# Scalar + tensor
x = torch.tensor([1.0, 2.0, 3.0])
x + 10  # [11, 12, 13] — 10 broadcasts to [10, 10, 10]

# Vector + matrix
x = torch.tensor([1.0, 2.0, 3.0])  # shape (3,)
M = torch.ones(4, 3)                # shape (4, 3)
M + x  # shape (4, 3) — x broadcasts across rows

# The rule: dimensions are compared right-to-left
# Each pair must be: equal, or one of them is 1
# (4, 3) + (3,) → (4, 3) + (1, 3) → (4, 3) ✓
# (4, 3) + (4,) → ERROR (3 ≠ 4)
```

## The Client Project: Batch Brightness Adjustment

```python
# Simulate a batch of images: (batch, channels, height, width)
images = torch.rand(8, 3, 64, 64)  # 8 images, RGB, 64×64

# Adjust brightness: multiply by a per-image factor
# factors shape: (8, 1, 1, 1) — broadcasts across C, H, W
factors = torch.tensor([0.5, 0.8, 1.0, 1.2, 1.5, 0.7, 1.1, 0.9])
factors = factors.view(8, 1, 1, 1)  # Reshape for broadcasting

brightened = images * factors  # (8, 3, 64, 64) — each image scaled differently
brightened = brightened.clamp(0, 1)  # Keep pixel values in [0, 1]

print(f"Input shape: {images.shape}")
print(f"Factors shape: {factors.shape}")
print(f"Output shape: {brightened.shape}")
print(f"Image 0 mean brightness: {images[0].mean():.3f} → {brightened[0].mean():.3f}")
```

## GPU (Preview)

```python
# Move tensors to GPU
if torch.cuda.is_available():
    device = torch.device("cuda")
    x = torch.randn(1000, 1000, device=device)  # Created on GPU
    y = torch.randn(1000, 1000).to(device)       # Moved to GPU
    z = x @ y  # Computed on GPU — 100x faster for large matrices
```

We'll use GPU properly in Chapter 11. For now, everything works on CPU.

## Common Errors and Fixes

```python
# Shape mismatch
a = torch.randn(3, 4)
b = torch.randn(5, 4)
# a + b → RuntimeError: sizes don't match
# Fix: check shapes with print(a.shape, b.shape)

# Device mismatch
x_cpu = torch.randn(3)
x_gpu = torch.randn(3).cuda()
# x_cpu + x_gpu → RuntimeError: expected all tensors on same device
# Fix: x_cpu.to(x_gpu.device) + x_gpu

# In-place vs out-of-place
x = torch.tensor([1.0, 2.0, 3.0])
x.add_(1)   # In-place (modifies x): [2, 3, 4]
y = x.add(1) # Out-of-place (new tensor): y=[3,4,5], x unchanged
```

## What You Learned

- **Tensors** — n-dimensional arrays, the fundamental data type
- **Creating** — zeros, ones, randn, arange, from Python lists
- **Indexing** — same as NumPy: slices, boolean masks, fancy indexing
- **Reshaping** — view, reshape, squeeze, unsqueeze, permute
- **Operations** — element-wise, reductions, matrix multiply (@)
- **Broadcasting** — automatic shape expansion (right-to-left rule)
- **dtype** — float32 for computation, int64 for indices
- **Print shapes** — always. `print(x.shape)` is your best friend.

The brightness tool works. But the next client wants to *learn* a function from data — fit a curve to noisy measurements. That requires gradients. That requires autograd.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Autograd →](chapter-02-autograd.md)
