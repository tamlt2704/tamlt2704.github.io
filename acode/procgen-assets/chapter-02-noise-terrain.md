# Chapter 2: Noise Terrain

[← Ch 1](chapter-01-seeded-starfield.md) | [Ch 3 →](chapter-03-planet-textures.md)

---

## Juno's Request

> "The starfield looks great, but now I need terrain. When you approach a planet, you see its surface profile — mountains, valleys, plains. It needs to look organic, not jagged. And different seeds should give wildly different landscapes."

She sketches on a napkin:

> "Imagine a side-scrolling view. The terrain line should flow — smooth hills, occasional peaks, flat stretches. Not random zigzags."

---

## The Problem: Random vs Noise

```
Random:  ╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲  (TV static sideways)
Noise:   ──╱╲──────╱──╲──╱╲──── (actual terrain)
```

The difference: **spatial coherence**. Nearby inputs produce nearby outputs.

---

## Simplex Noise: The Basics

Simplex noise maps coordinates to values in the range [-1, 1]:

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

const prng = Alea('terrain-seed');
const noise2D = createNoise2D(prng);

// 1D terrain: only vary x, keep y constant
const height = noise2D(x * frequency, 0);
// Returns value between -1 and 1
```

### Frequency Controls Scale

```
Low frequency (0.005):   ───────╱────────╲───────  (broad hills)
Med frequency (0.02):    ──╱╲──╱──╲──╱╲──╱──╲──   (rolling hills)
High frequency (0.08):   ╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲  (jagged peaks)
```

```typescript
// frequency = how "zoomed in" you are
const broad = noise2D(x * 0.005, 0);  // continent-scale features
const medium = noise2D(x * 0.02, 0);  // hill-scale features
const fine = noise2D(x * 0.08, 0);    // rock-scale detail
```

---

## Octaves: Fractal Noise (fBm)

Real terrain has features at multiple scales simultaneously. We layer noise at different frequencies:

```
Octave 1 (amp=1.0, freq=1x):    ───╱──────╲──────╱───
Octave 2 (amp=0.5, freq=2x):    ──╱╲──╱──╲──╱╲──╱──╲
Octave 3 (amp=0.25, freq=4x):   ─╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲
─────────────────────────────────────────────────────────
Sum:                             ──╱╲╱──╱╲──╲╱──╱╲╱──  (natural!)
```

```typescript
function fractalNoise(
  noise: (x: number, y: number) => number,
  x: number,
  y: number,
  octaves: number = 6,
  lacunarity: number = 2.0,   // frequency multiplier per octave
  persistence: number = 0.5   // amplitude multiplier per octave
): number {
  let value = 0;
  let amplitude = 1;
  let frequency = 1;
  let maxValue = 0;

  for (let i = 0; i < octaves; i++) {
    value += noise(x * frequency, y * frequency) * amplitude;
    maxValue += amplitude;
    amplitude *= persistence;
    frequency *= lacunarity;
  }

  return value / maxValue; // normalize to [-1, 1]
}
```

### Parameter Effects

| Parameter | What It Does | Terrain Analogy |
|-----------|-------------|-----------------|
| `octaves` | Number of layers | More = more detail |
| `lacunarity` | Frequency growth rate | Higher = sharper detail |
| `persistence` | Amplitude decay rate | Higher = rougher terrain |
| `base frequency` | Starting scale | Lower = broader features |

---

## 1D Terrain Profile

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

function generateTerrainProfile(seed: string | number, width: number, baseFreq = 0.008, octaves = 5): number[] {
  const prng = Alea(seed);
  const noise = createNoise2D(prng);
  const heights: number[] = [];
  for (let x = 0; x < width; x++) {
    heights.push((fractalNoise(noise, x * baseFreq, 0, octaves) + 1) / 2);
  }
  return heights;
}
```

### Rendering the Profile

```typescript
function renderProfile(heights: number[], W: number, H: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d')!;

  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, '#1a0a2e'); grad.addColorStop(1, '#16213e');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);

  ctx.beginPath(); ctx.moveTo(0, H);
  for (let x = 0; x < W; x++) ctx.lineTo(x, H - heights[x] * H * 0.7);
  ctx.lineTo(W, H); ctx.closePath();
  ctx.fillStyle = '#2d4a3e'; ctx.fill();
  return canvas;
}
```

---

## 2D Noise: Terrain Maps

Extend to 2D for top-down heightmaps — same principle, both axes vary:

```typescript
function generateTerrainMap(seed: string | number, width: number, height: number): number[][] {
  const prng = Alea(seed);
  const noise = createNoise2D(prng);
  const map: number[][] = [];

  for (let y = 0; y < height; y++) {
    map[y] = [];
    for (let x = 0; x < width; x++) {
      map[y][x] = (fractalNoise(noise, x * 0.01, y * 0.01, 6) + 1) / 2;
    }
  }
  return map;
}
```

Render by mapping each value to a grayscale pixel via ImageData, same pattern as Ch 1.

---

## Visual Comparison

```
1 octave:                    6 octaves:
┌──────────────────┐         ┌──────────────────┐
│░░░░▒▒▒▓▓███▓▓▒░░│         │░░▒░▒▓▒▓██▓█▓▒▒░░│
│░░░▒▒▒▓▓████▓▒▒░░│         │░░▒▒▓▒▓███▓█▓▒░▒░│
│░░▒▒▒▓▓█████▓▒▒░░│         │░▒▒▓▒▓████▓▓▒▒░░░│
│░░▒▒▓▓██████▓▒▒░░│         │░▒▓▒▓█████▓▒▓▒░░░│
│░▒▒▓▓███████▓▒░░░│         │▒▒▓▓▓████▓▓▒▒░░░░│
│░▒▒▓▓███████▓▒░░░│         │▒▓▓▓████▓▓▒▒░▒░░░│
└──────────────────┘         └──────────────────┘
 (smooth, blobby)             (detailed, natural)
```

---

## Parameter Tuning

| Terrain Type | Frequency | Octaves | Persistence | Result |
|-------------|-----------|---------|-------------|--------|
| Rolling plains | 0.005 | 3 | 0.4 | Gentle, broad |
| Mountains | 0.01 | 6 | 0.6 | Sharp, detailed |
| Alien spires | 0.02 | 4 | 0.7 | Tall, jagged |
| Ocean floor | 0.003 | 5 | 0.3 | Smooth, deep |

**Juno's notes:**

> "Persistence is the magic knob. Low persistence (0.3) = smooth rolling hills. High persistence (0.7) = craggy mountains. The base frequency sets the 'continent size' — too high and you get tiny islands, too low and the whole map is one big slope."

---

## Common Pitfalls

```typescript
// BAD: noise returns [-1, 1], but you treat it as [0, 1]
const height = noise(x * 0.01, 0); // could be negative!
// GOOD: (noise(...) + 1) / 2 → now 0-1

// BAD: integer inputs → noise repeats at grid points
const v = noise(x, y); // boring patterns
// GOOD: noise(x * 0.02, y * 0.02) → smooth variation

// BAD: same noise for unrelated things (correlated!)
// GOOD: offset y-coordinate: noise(x*0.01, 100) for trees vs noise(x*0.01, 0) for terrain
```

---

## Exercises

1. **Terrain layers:** Three profiles at frequencies 0.003, 0.01, 0.04. Render as overlapping ranges — back=faint blue, mid=gray, front=dark green.

2. **Island mask:** Multiply 2D noise by radial gradient: `mask = 1 - sqrt((x-cx)²+(y-cy)²)/radius`. Forces terrain into island shape.

3. **Animated terrain:** Use time as noise parameter: `noise(x*0.01, time*0.005)`. Terrain slowly morphs each frame.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Simplex noise | Maps coordinates → [-1, 1] with spatial coherence |
| Frequency | Scale multiplier. Higher = more detail, smaller features |
| Octaves (fBm) | Layer multiple noise passes at increasing frequency |
| Lacunarity | How much frequency increases per octave (usually 2.0) |
| Persistence | How much amplitude decreases per octave (0.3-0.7) |
| Normalization | `(noise + 1) / 2` converts [-1,1] to [0,1] |
| 1D terrain | `noise(x * freq, 0)` — vary x only |
| 2D terrain | `noise(x * freq, y * freq)` — heightmap |

---

[← Ch 1](chapter-01-seeded-starfield.md) | [Ch 3 →](chapter-03-planet-textures.md)
