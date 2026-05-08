# Chapter 9: Custom Training

[← Chapter 8: Transformers](chapter-08-transformers.md) | [Chapter 10: Saving and Loading →](chapter-10-checkpoints.md)

---

## The Project

Client: a game studio wants AI-generated character faces. They need a GAN (Generative Adversarial Network) — two models training against each other. One generates faces, the other detects fakes. Standard training loops won't cut it.

Mara: "GANs are two models playing a game. The generator tries to fool the discriminator. The discriminator tries to catch fakes. You train them in alternation."

## Custom Loss Functions

```python
import torch
import torch.nn as nn

# Method 1: Function-based
def focal_loss(logits, targets, alpha=0.25, gamma=2.0):
    """Focuses on hard examples by down-weighting easy ones."""
    bce = nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction='none')
    pt = torch.exp(-bce)
    loss = alpha * (1 - pt) ** gamma * bce
    return loss.mean()

# Method 2: Class-based (stateful)
class LabelSmoothingLoss(nn.Module):
    def __init__(self, num_classes, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
        self.num_classes = num_classes

    def forward(self, logits, targets):
        confidence = 1.0 - self.smoothing
        smooth_val = self.smoothing / (self.num_classes - 1)
        one_hot = torch.full_like(logits, smooth_val)
        one_hot.scatter_(1, targets.unsqueeze(1), confidence)
        log_probs = torch.nn.functional.log_softmax(logits, dim=1)
        return -(one_hot * log_probs).sum(dim=1).mean()
```

## Multiple Models and Optimizers

```python
# Each model gets its own optimizer
generator = Generator()
discriminator = Discriminator()

opt_g = torch.optim.Adam(generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
opt_d = torch.optim.Adam(discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))

# Train them separately in each step
# Step 1: Train discriminator
opt_d.zero_grad()
d_loss.backward()
opt_d.step()

# Step 2: Train generator
opt_g.zero_grad()
g_loss.backward()
opt_g.step()
```

## Gradient Penalty (WGAN-GP)

```python
def gradient_penalty(discriminator, real, fake):
    """Enforces Lipschitz constraint on discriminator."""
    batch_size = real.size(0)
    alpha = torch.rand(batch_size, 1, 1, 1, device=real.device)
    interpolated = (alpha * real + (1 - alpha) * fake).requires_grad_(True)

    d_interpolated = discriminator(interpolated)
    gradients = torch.autograd.grad(
        outputs=d_interpolated,
        inputs=interpolated,
        grad_outputs=torch.ones_like(d_interpolated),
        create_graph=True,
        retain_graph=True
    )[0]

    gradients = gradients.view(batch_size, -1)
    penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()
    return penalty
```

## The Client Project: Face GAN

```python
import torch
import torch.nn as nn

LATENT_DIM = 100
IMG_CHANNELS = 3
IMG_SIZE = 64

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            # Input: (batch, 100, 1, 1)
            nn.ConvTranspose2d(LATENT_DIM, 512, 4, 1, 0),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # (batch, 512, 4, 4)
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            # (batch, 256, 8, 8)
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            # (batch, 128, 16, 16)
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            # (batch, 64, 32, 32)
            nn.ConvTranspose2d(64, IMG_CHANNELS, 4, 2, 1),
            nn.Tanh()
            # (batch, 3, 64, 64)
        )

    def forward(self, z):
        return self.net(z.view(-1, LATENT_DIM, 1, 1))

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(IMG_CHANNELS, 64, 4, 2, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.Conv2d(256, 512, 4, 2, 1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
            nn.Conv2d(512, 1, 4, 1, 0),  # (batch, 1, 1, 1)
        )

    def forward(self, img):
        return self.net(img).view(-1)

# Training loop
G = Generator()
D = Discriminator()
opt_g = torch.optim.Adam(G.parameters(), lr=0.0002, betas=(0.5, 0.999))
opt_d = torch.optim.Adam(D.parameters(), lr=0.0002, betas=(0.5, 0.999))

# Simulate real face data
real_faces = torch.randn(256, 3, 64, 64).clamp(-1, 1)
batch_size = 32

for step in range(500):
    # --- Train Discriminator ---
    idx = torch.randint(0, len(real_faces), (batch_size,))
    real = real_faces[idx]
    z = torch.randn(batch_size, LATENT_DIM)
    fake = G(z).detach()  # detach: don't backprop into G

    d_real = D(real).mean()
    d_fake = D(fake).mean()
    gp = gradient_penalty(D, real, fake)
    d_loss = -d_real + d_fake + 10 * gp  # WGAN-GP loss

    opt_d.zero_grad()
    d_loss.backward()
    opt_d.step()

    # --- Train Generator (every 5 D steps) ---
    if step % 5 == 0:
        z = torch.randn(batch_size, LATENT_DIM)
        fake = G(z)
        g_loss = -D(fake).mean()  # Generator wants D(fake) to be high

        opt_g.zero_grad()
        g_loss.backward()
        opt_g.step()

    if step % 100 == 0:
        print(f"Step {step}: D_loss={d_loss.item():.4f} G_loss={g_loss.item():.4f}")
```

## What You Learned

- **Custom loss** — write as a function or nn.Module subclass
- **Multiple optimizers** — each model gets its own optimizer
- **Alternating training** — train D and G in separate steps
- **detach()** — prevents gradients flowing into the wrong model
- **Gradient penalty** — uses `torch.autograd.grad` for second-order gradients
- **GAN architecture** — ConvTranspose2d (upsamples), Conv2d (downsamples)

The GAN generates faces. But training takes hours — you need to save progress and resume. Next: checkpoints and model saving.

---

[← Chapter 8: Transformers](chapter-08-transformers.md) | [Chapter 10: Saving and Loading →](chapter-10-checkpoints.md)
