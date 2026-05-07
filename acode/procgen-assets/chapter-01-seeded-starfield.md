# Chapter 1: Seeded Starfields

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-noise-terrain.md)

---

## Juno's Request

> "I need a starfield background for the title screen and the space travel segments. Every time you start a new run, the stars should be different — but if you reload the same seed, the stars are identical. Oh, and I want parallax: dim stars in the back, bright ones in the front, moving at different speeds."

---

## The Problem with Math.random()

```typescript
// Different stars every page load — no determinism, no seed sharing
for (let i = 0; i < 500; i++) {
  drawStar(Math.random() * 800, Math.random() * 600);
}
```

---

## Seeded PRNG: Alea

A seeded PRNG produces the same sequence given the same seed:

```typescript
import Alea from 'alea';

const rng = Alea('seed-42');
console.log(rng()); // 0.7197... always
console.log(rng()); // 0.2653... always

const rng2 = Alea('seed-42');
console.log(rng2()); // 0.7197... same!
```

**Key insight:** The sequence is fixed. Call order matters — different call order gives different results downstream.

---

## The Algorithm: Star Placement

```
For each star:
  1. x = rng() * width
  2. y = rng() * height
  3. brightness = rng()  (weighted toward dim)
  4. size = brightness-based (brighter = larger)
  5. layer = brightness bucket (for parallax)
```

### Brightness Distribution

Real starfields have many dim stars and few bright ones. We use a power curve:

```
brightness = rng() ^ exponent

exponent = 3:  ████████████████░░░░  (mostly dim — realistic)
exponent = 1:  ██████████░░░░░░░░░░  (uniform — boring)
exponent = 0.5: ████░░░░░░░░░░░░░░░░  (mostly bright — unrealistic)
```

```
Brightness distribution (exponent = 3):
  ★ (bright)  |██                          ~5%
  ☆ (medium)  |████████                    ~20%
  · (dim)     |████████████████████████    ~75%
```

---

## Implementation

```typescript
import Alea from 'alea';

interface Star {
  x: number;
  y: number;
  brightness: number;
  size: number;
  layer: number; // 0 = far/slow, 2 = near/fast
}

function generateStarfield(
  seed: string | number,
  width: number,
  height: number,
  count: number = 600
): Star[] {
  const rng = Alea(seed);
  const stars: Star[] = [];

  for (let i = 0; i < count; i++) {
    const x = rng() * width;
    const y = rng() * height;
    // Power curve: cube the value → most stars are dim
    const brightness = Math.pow(rng(), 3);
    const size = brightness > 0.8 ? 2 : brightness > 0.4 ? 1.5 : 1;
    // Brighter stars are "closer" (higher layer)
    const layer = brightness > 0.7 ? 2 : brightness > 0.3 ? 1 : 0;

    stars.push({ x, y, brightness, size, layer });
  }

  return stars;
}
```

---

## Rendering with ImageData

Write directly to the pixel buffer for pixel-perfect control:

```typescript
function renderStarfield(stars: Star[], width: number, height: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(width, height);
  const data = imageData.data;

  // Background (deep space — slight blue tint, not pure black)
  for (let i = 0; i < data.length; i += 4) { data[i]=4; data[i+1]=4; data[i+2]=12; data[i+3]=255; }

  // Plot stars with warm/cool color tint
  for (const star of stars) {
    const px = Math.floor(star.x), py = Math.floor(star.y);
    if (px < 0 || px >= width || py < 0 || py >= height) continue;
    const i = (py * width + px) * 4;
    const b = Math.floor(star.brightness * 255);
    data[i] = Math.min(255, b + 20);     // warm bias for bright
    data[i+1] = Math.min(255, b + 5);
    data[i+2] = Math.min(255, b + 40);   // cool bias for dim
    data[i+3] = 255;
  }

  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Parallax Scrolling

Stars on different layers move at different speeds:

```typescript
function updateParallax(stars: Star[], scrollX: number, width: number): void {
  const speeds = [0.2, 0.5, 1.0]; // layer 0=slow, 2=fast
  for (const star of stars) {
    star.x -= speeds[star.layer] * scrollX;
    if (star.x < 0) star.x += width;
    if (star.x >= width) star.x -= width;
  }
}
```

```
Layer 0 (far):   · · · · · · · ·   speed: 0.2x
Layer 1 (mid):   ☆   ☆   ☆   ☆    speed: 0.5x
Layer 2 (near):  ★       ★         speed: 1.0x
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| `count` | 100 | 2000 | Sparse vs dense field |
| `exponent` | 1 | 5 | Uniform vs mostly-dim |
| `layer speeds` | [0.1, 0.3, 0.6] | [0.3, 0.7, 1.5] | Subtle vs dramatic parallax |
| `color tint` | pure white | warm/cool bias | Sterile vs atmospheric |

**Juno's feedback loop:**

> "Too few stars — feels empty. Too many — feels like noise. 400-600 with exponent 3 hits the sweet spot. The warm/cool tint is subtle but makes it feel like a real sky."

---

## Why Determinism Matters

```typescript
const worldSeed = 'drift-7291';
const titleStars = generateStarfield(worldSeed + '-title', 800, 600);
const level3Stars = generateStarfield(worldSeed + '-level-3', 800, 600);
```

Derive sub-seeds from the world seed. Each system gets its own deterministic stream.

---

## Visual Result

```
┌────────────────────────────────────────────────┐
│                    ·                            │
│  ·        ★              ·                     │
│         ·      ·                ☆              │
│                        ·              ·        │
│    ☆          ·                                │
│              ·       ·        ·                │
│  ·                         ★        ·         │
│        ·          ·                            │
│                ·        ·       ·    ·         │
│   ·       ·                          ☆        │
└────────────────────────────────────────────────┘
  Seed: "drift-42" | Stars: 500 | Exponent: 3
```

---

## Exercises

1. **Twinkle effect:** Add a `phase` per star. Modulate brightness with `sin(time + phase)`. Only bright stars twinkle.

2. **Star clusters:** Add 3-5 cluster centers. Generate 50 extra stars near each using `(rng()+rng()+rng())/3` for gaussian approximation.

3. **Nebula glow:** Pick 2-3 points. Tint nearby background pixels with faint color using falloff: `1 / (1 + dist * 0.05)`.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| `Alea(seed)` | Returns a function that produces 0-1 floats deterministically |
| Power curve | `rng() ^ n` — higher n = more values near 0 |
| ImageData | `(y * width + x) * 4` gives RGBA index for pixel (x, y) |
| Parallax | Multiple layers at different scroll speeds = depth illusion |
| Sub-seeds | `seed + '-suffix'` gives independent deterministic streams |
| Brightness | Real stars: many dim, few bright. Use exponent ≥ 3 |

---

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-noise-terrain.md)
