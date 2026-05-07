# Chapter 3: Planet Textures

[← Ch 2](chapter-02-noise-terrain.md) | [Ch 4 →](chapter-04-heightmaps.md)

---

## Juno's Request

> "When you discover a new planet in Drift, I want a texture preview — a little sphere showing what the surface looks like. Water planets, desert planets, ice worlds. Each seed gives a different planet. The texture wraps around the sphere so there's no visible seam."

---

## The Algorithm: Noise → Color Thresholds

```
Noise value:  0.0 ──── 0.35 ── 0.42 ── 0.45 ── 0.7 ── 0.85 ── 1.0
Biome:        │deep water│shallow│ sand │ grass │ rock │  snow  │
```

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

interface Biome {
  threshold: number;
  color: [number, number, number];
  name: string;
}

const EARTH_BIOMES: Biome[] = [
  { threshold: 0.35, color: [30, 60, 120],  name: 'deep water' },
  { threshold: 0.42, color: [50, 100, 160], name: 'shallow water' },
  { threshold: 0.45, color: [194, 178, 128], name: 'sand' },
  { threshold: 0.65, color: [34, 139, 34],  name: 'grass' },
  { threshold: 0.85, color: [80, 80, 70],   name: 'rock' },
  { threshold: 1.00, color: [220, 224, 230], name: 'snow' },
];

function getBiomeColor(elevation: number, biomes: Biome[]): [number, number, number] {
  for (const biome of biomes) {
    if (elevation < biome.threshold) return biome.color;
  }
  return biomes[biomes.length - 1].color;
}
```

---

## Generating the Texture

```typescript
function generatePlanetTexture(
  seed: string | number, size: number = 128,
  biomes: Biome[] = EARTH_BIOMES, scale: number = 0.03, octaves: number = 5
): HTMLCanvasElement {
  const prng = Alea(seed);
  const noise = createNoise2D(prng);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(size, size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const elevation = (fbm(noise, x * scale, y * scale, octaves) + 1) / 2;
      const [r, g, b] = getBiomeColor(elevation, biomes);
      const i = (y * size + x) * 4;
      imageData.data[i] = r; imageData.data[i+1] = g;
      imageData.data[i+2] = b; imageData.data[i+3] = 255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Wrapping Noise on a Sphere

Flat noise has seams when wrapped. Map x to a circle in noise space:

```typescript
function generateWrappingTexture(
  seed: string | number, width: number, height: number,
  biomes: Biome[], scale: number = 4.0, octaves: number = 5
): HTMLCanvasElement {
  const prng = Alea(seed);
  const noise = createNoise2D(prng);
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(width, height);

  for (let py = 0; py < height; py++) {
    for (let px = 0; px < width; px++) {
      const angle = (px / width) * Math.PI * 2;
      const nx = Math.cos(angle) * scale;
      const ny = Math.sin(angle) * scale;
      const nz = (py / height) * scale * 2;

      const elevation = (fbm(noise, nx + nz, ny + nz, octaves) + 1) / 2;
      const [r, g, b] = getBiomeColor(elevation, biomes);
      const i = (py * width + px) * 4;
      imageData.data[i] = r; imageData.data[i+1] = g;
      imageData.data[i+2] = b; imageData.data[i+3] = 255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

```
Without wrapping:          With wrapping:
┌──────────|──────────┐    ┌─────────────────────┐
│ grass    |seam grass│    │ grass  grass  grass  │
│ water    |    water │    │ water  water  water  │
└──────────|──────────┘    └─────────────────────┘
```

---

## Planet Variety: Parameter Presets

```typescript
const DESERT_BIOMES: Biome[] = [
  { threshold: 0.15, color: [60, 40, 20],   name: 'canyon' },
  { threshold: 0.40, color: [140, 100, 50], name: 'sand' },
  { threshold: 0.65, color: [180, 140, 70], name: 'dunes' },
  { threshold: 1.00, color: [220, 200, 150], name: 'mesa' },
];

const ICE_BIOMES: Biome[] = [
  { threshold: 0.30, color: [20, 40, 80],   name: 'deep ocean' },
  { threshold: 0.55, color: [180, 200, 220], name: 'ice shelf' },
  { threshold: 1.00, color: [245, 248, 255], name: 'snow peak' },
];

function planetTypeFromSeed(seed: string | number): Biome[] {
  const rng = Alea(seed);
  const roll = rng();
  if (roll < 0.3) return EARTH_BIOMES;
  if (roll < 0.5) return DESERT_BIOMES;
  if (roll < 0.7) return ICE_BIOMES;
  return generateAlienBiomes(rng); // random hue-based palette
}
```

---

## Rendering as a Sphere

Apply the texture to a circular mask with lighting:

```typescript
function renderAsSphere(texture: HTMLCanvasElement, size: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const cx = size/2, cy = size/2, radius = size/2 - 2;

  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.clip();
  ctx.drawImage(texture, 0, 0, size, size);

  // Lighting: bright upper-left, dark edges
  const gradient = ctx.createRadialGradient(cx - radius*0.3, cy - radius*0.3, 0, cx, cy, radius);
  gradient.addColorStop(0, 'rgba(255,255,255,0.15)');
  gradient.addColorStop(0.7, 'rgba(0,0,0,0)');
  gradient.addColorStop(1, 'rgba(0,0,0,0.5)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
  return canvas;
}
```

---

## Visual Result

```
Earth-like:     Desert:         Ice:
  ┌──────┐       ┌──────┐       ┌──────┐
  │▓▓░░██│       │▒▒▓▓▒▒│       │░░░░▒▒│
  │░░██▓▓│       │▓▓▒▒▓▓│       │░░▒▒░░│
  │██▓▓░░│       │▒▒▓▓▒▒│       │▒▒░░░░│
  └──────┘       └──────┘       └──────┘
```

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| `scale` (0.01-0.08) | Continent size | "0.03 gives 2-3 continents on 128px" |
| `octaves` (3-7) | Coastline detail | "5 is the sweet spot" |
| Water threshold | Ocean coverage | "0.35-0.45 for earth-like" |
| Biome count | Complexity | "4-6 biomes per planet" |

---

## Exercises

1. **Polar ice caps:** Add latitude modifier — pixels near top/bottom pushed toward "snow" using `cos(y/height*π)`.

2. **Cloud layer:** Second noise map, semi-transparent white overlay, thresholded at 0.6.

3. **Planet rotation:** Wider texture (256×128 for 128×128 display). Shift x-offset each frame.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Biome thresholds | Elevation ranges mapped to colors |
| Wrapping | Map x to `(cos(θ), sin(θ))` in noise space |
| Planet variety | Different biome tables + noise params per type |
| Sphere rendering | Circular clip + radial gradient for 3D illusion |
| Seed → type | First `rng()` call determines planet category |

---

[← Ch 2](chapter-02-noise-terrain.md) | [Ch 4 →](chapter-04-heightmaps.md)
