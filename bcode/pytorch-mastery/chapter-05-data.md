# Chapter 5: Data Loading

[← Chapter 4: Training Loop](chapter-04-training.md) | [Chapter 6: CNNs →](chapter-06-cnn.md)

---

## The Project

Client: a wildlife conservation group has 50,000 camera trap photos. They need an image classification pipeline — but images are different sizes, some are dark, some are blurry. You need to load, transform, augment, and batch them efficiently.

Mara: "Your model is only as good as your data pipeline. Garbage in, garbage out. But also: slow pipeline, slow training."

## The Dataset Class

```python
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample, label

# Usage
data = torch.randn(1000, 3, 64, 64)
labels = torch.randint(0, 5, (1000,))
dataset = CustomDataset(data, labels)
print(f"Dataset size: {len(dataset)}")
print(f"Sample shape: {dataset[0][0].shape}")
```

## DataLoader: Batching and Shuffling

```python
loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,          # Randomize order each epoch
    num_workers=4,         # Parallel data loading
    pin_memory=True,       # Faster CPU→GPU transfer
    drop_last=True         # Drop incomplete final batch
)

for batch_data, batch_labels in loader:
    print(batch_data.shape)   # (32, 3, 64, 64)
    print(batch_labels.shape) # (32,)
    break
```

## Transforms with torchvision

```python
from torchvision import transforms

# Compose a pipeline of transforms
train_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),                    # PIL → tensor, scales to [0,1]
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])  # ImageNet stats
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
```

## Data Augmentation

Augmentation creates variety so the model generalizes:

```python
augmentation = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.ColorJitter(brightness=0.3, saturation=0.3),
    transforms.RandomErasing(p=0.2),  # Randomly erase a patch
])
```

## Built-in Datasets (torchvision)

```python
from torchvision import datasets

# CIFAR-10: 60k 32×32 color images, 10 classes
train_set = datasets.CIFAR10('./data', train=True, download=True,
                              transform=train_transform)
test_set = datasets.CIFAR10('./data', train=False, download=True,
                             transform=val_transform)

# ImageFolder: load from directory structure
# data/train/cat/img001.jpg
# data/train/dog/img001.jpg
train_set = datasets.ImageFolder('data/train', transform=train_transform)
print(train_set.classes)       # ['cat', 'dog']
print(train_set.class_to_idx)  # {'cat': 0, 'dog': 1}
```

## The Client Project: Wildlife Image Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms

# Simulating the wildlife dataset (in practice: ImageFolder)
class WildlifeDataset(Dataset):
    """Camera trap images: 5 species classification."""
    def __init__(self, num_images=5000, transform=None):
        # Simulate variable-quality images
        self.images = torch.rand(num_images, 3, 128, 128)
        self.labels = torch.randint(0, 5, (num_images,))
        self.transform = transform
        self.classes = ['deer', 'bear', 'wolf', 'eagle', 'fox']

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

# Transforms (tensor-based since our data is already tensors)
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Create datasets
full_dataset = WildlifeDataset(5000)
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_set, val_set = random_split(full_dataset, [train_size, val_size])

# DataLoaders
train_loader = DataLoader(train_set, batch_size=64, shuffle=True,
                          num_workers=2, pin_memory=True)
val_loader = DataLoader(val_set, batch_size=64, shuffle=False,
                        num_workers=2, pin_memory=True)

# Verify the pipeline
for images, labels in train_loader:
    print(f"Batch images: {images.shape}")   # (64, 3, 128, 128)
    print(f"Batch labels: {labels.shape}")   # (64,)
    print(f"Label sample: {labels[:5]}")
    break

print(f"\nTrain batches: {len(train_loader)}")
print(f"Val batches: {len(val_loader)}")
```

## What You Learned

- **Dataset** — implement `__len__` and `__getitem__` for any data source
- **DataLoader** — handles batching, shuffling, parallel loading
- **transforms** — resize, crop, normalize, augment images
- **Augmentation** — flips, rotations, color jitter to prevent overfitting
- **torchvision.datasets** — MNIST, CIFAR, ImageFolder for common formats
- **random_split** — divide dataset into train/val/test
- **pin_memory** — speeds up CPU→GPU transfer

The pipeline is ready. But a flat feedforward net won't cut it for images — it ignores spatial structure. Next: convolutional neural networks.

---

[← Chapter 4: Training Loop](chapter-04-training.md) | [Chapter 6: CNNs →](chapter-06-cnn.md)
