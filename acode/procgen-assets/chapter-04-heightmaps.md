# Chapter 4: Heightmaps

[← Ch 3](chapter-03-planet-textures.md) | [Ch 5 →](chapter-05-color-palettes.md)

---

## Juno's Request

> "When you land on a planet, I want a zoomed-in terrain view — like a topographic map. Contour lines showing elevation, maybe a pseudo-3D view. And the terrain shouldn't look like smooth blobs — I want erosion. Rivers carving valleys."

---

## Heightmap Basics

A heightmap is a 2D grid where each cell stores elevation (0-1). We use `Float32Array` for precision:

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

function generateHeightmap(seed: string | number, size: number, scale: number = 0.015): Float32Array {
  const prng = Alea(seed);
  const noise = createNoise2D(prng);
  const map = new Float32Array(size * size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let value = 0, amp = 1, freq = scale, maxAmp = 0;
      for (let o = 0; o < 6; o++) {
        value += noise(x * freq, y * freq) * amp;
        maxAmp += amp; amp *= 0.5; freq *= 2.0;
      }
      map[y * size + x] = (value / maxAmp + 1) / 2;
    }
  }
  return map;
}
```

---

## Gradient and Slope

The gradient tells you steepness — essential for erosion and contour lines:

```typescript
function getSlope(map: Float32Array, size: number, x: number, y: number): number {
  const left = x > 0 ? map[y * size + (x-1)] : map[y * size + x];
  const right = x < size-1 ? map[y * size + (x+1)] : map[y * size + x];
  const up = y > 0 ? map[(y-1) * size + x] : map[y * size + x];
  const down = y < size-1 ? map[(y+1) * size + x] : map[y * size + x];
  const dx = (right - left) / 2;
  const dy = (down - up) / 2;
  return Math.sqrt(dx * dx + dy * dy);
}
```

---

## Contour Lines

Detect where elevation crosses threshold values between adjacent pixels:

```typescript
function renderContours(map: Float32Array, size: number, levels: number = 10): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(size, size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const h = map[y * size + x];
      const i = (y * size + x) * 4;
      const c = Math.floor(h * 200) + 40;
      imageData.data[i] = c; imageData.data[i+1] = c + 20;
      imageData.data[i+2] = c - 10; imageData.data[i+3] = 255;

      // Contour detection
      if (x < size-1 && y < size-1) {
        const right = map[y * size + (x+1)];
        const below = map[(y+1) * size + x];
        for (let l = 1; l < levels; l++) {
          const t = l / levels;
          if ((h < t && right >= t) || (h >= t && right < t) ||
              (h < t && below >= t) || (h >= t && below < t)) {
            imageData.data[i] = 40; imageData.data[i+1] = 30; imageData.data[i+2] = 20;
            break;
          }
        }
      }
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

```
Contour map:  close lines = steep, far lines = gentle
┌─────────────────────────┐
│         ╭───╮           │
│       ╭─┤   ├─╮         │
│     ╭─┤ │ ▲ │ ├─╮       │
│   ╭─┤ │ ╰───╯ │ ├─╮     │
│   ╰───┤       ├───╯     │
│       ╰───────╯         │
└─────────────────────────┘
```

---

## Thermal Erosion

Rock crumbles when slopes are too steep:

```typescript
function thermalErosion(map: Float32Array, size: number, iterations: number = 30, talus: number = 0.01): void {
  const neighbors = [[-1,0],[1,0],[0,-1],[0,1]];
  for (let iter = 0; iter < iterations; iter++) {
    for (let y = 1; y < size-1; y++) {
      for (let x = 1; x < size-1; x++) {
        const idx = y * size + x;
        for (const [dx, dy] of neighbors) {
          const nIdx = (y+dy) * size + (x+dx);
          const diff = map[idx] - map[nIdx];
          if (diff > talus) {
            const transfer = (diff - talus) * 0.5;
            map[idx] -= transfer; map[nIdx] += transfer;
          }
        }
      }
    }
  }
}
```

---

## Hydraulic Erosion

Simulated raindrops carry and deposit sediment:

```typescript
function hydraulicErosion(map: Float32Array, size: number, drops: number = 5000, rng: () => number): void {
  for (let d = 0; d < drops; d++) {
    let x = Math.floor(rng() * (size-2)) + 1;
    let y = Math.floor(rng() * (size-2)) + 1;
    let sediment = 0, speed = 0;

    for (let step = 0; step < 64; step++) {
      const idx = y * size + x;
      const slope = getSlope(map, size, x, y);
      const left = x > 0 ? map[idx-1] : map[idx];
      const right = x < size-1 ? map[idx+1] : map[idx];
      const up = y > 0 ? map[idx-size] : map[idx];
      const down = y < size-1 ? map[idx+size] : map[idx];

      // Move downhill
      const nx = right < left ? Math.min(x+1, size-2) : Math.max(x-1, 1);
      const ny = down < up ? Math.min(y+1, size-2) : Math.max(y-1, 1);
      if (nx === x && ny === y) break;

      const capacity = Math.max(slope * speed * 4, 0.01);
      if (sediment > capacity) {
        map[idx] += (sediment - capacity) * 0.3; sediment = capacity;
      } else {
        const erode = Math.min((capacity - sediment) * 0.3, map[idx] * 0.1);
        map[idx] -= erode; sediment += erode;
      }
      speed = Math.sqrt(speed * speed + slope);
      x = nx; y = ny;
    }
  }
}
```

---

## Visual Result

```
Grayscale:        Contour:          After erosion:
┌──────────┐      ┌──────────┐      ┌──────────┐
│░░▒▒▓▓██▓▓│      │  ╭──╮    │      │░░▒▒▓▓██▓▓│
│▒▒▓▓██████│      │╭─┤▲ ├─╮  │      │▒▒▓╲▓████▓│  ← river
│░▒▒▓▓████▓│      │╰─┤  ├─╯  │      │░▒▒▓╲████▓│    channels
│░░▒▒▓▓██▓▓│      │  ╰──╯    │      │░░▒▒▓▓██▓▓│
└──────────┘      └──────────┘      └──────────┘
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| Noise scale | 0.005 | 0.03 | Broad plateaus vs many peaks |
| Thermal iterations | 10 | 100 | Subtle vs heavy weathering |
| Talus angle | 0.005 | 0.05 | Easy crumble vs stable cliffs |
| Hydraulic drops | 1000 | 20000 | Light rain vs deep canyons |
| Contour levels | 5 | 20 | Coarse vs fine bands |

**Juno's notes:**

> "Use both erosion types: thermal first (20 iterations), then hydraulic (5000 drops). Contour lines at 12 levels give that topographic map feel."

---

## Exercises

1. **Ridge noise:** Use `abs(noise)` per octave. Creates sharp ridges where noise crosses zero.

2. **River tracing:** From highest points, trace downhill. Where paths converge, draw blue river pixels.

3. **Erosion animation:** One iteration per frame with `requestAnimationFrame`. Watch valleys form.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Heightmap | Float32Array of elevation values (0-1) |
| Gradient | `(right - left) / 2` for dx, `(down - up) / 2` for dy |
| Slope | `sqrt(dx² + dy²)` — steepness magnitude |
| Contour lines | Where elevation crosses threshold between neighbors |
| Thermal erosion | Material moves downhill when slope > talus angle |
| Hydraulic erosion | Raindrops carry/deposit sediment along paths |

---

[← Ch 3](chapter-03-planet-textures.md) | [Ch 5 →](chapter-05-color-palettes.md)
