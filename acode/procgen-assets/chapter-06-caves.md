# Chapter 6: Caves

[← Ch 5](chapter-05-color-palettes.md) | [Ch 7 →](chapter-07-wfc.md)

---

## Juno's Request

> "Some planets have underground cave systems. I need organic-looking caves — not grid corridors. Think natural limestone caverns with irregular walls and connected chambers. And every cave must be fully traversable — no isolated pockets."

---

## Cellular Automata: The Concept

Start with random noise, apply rules, caves emerge:

```
Iteration 0 (random):    Iteration 6 (caves):
██░██░░█░██░░█░█          █████░░░░░█████
░█░░██░█░░█░██░░          █████░░░░░░████
██░░█░░██░█░█░█░          ████░░░░░░░░███
░░██░█░░█░░██░██          ░░░░░░░░░░░░░██
█░░█░██░░█░░█░░█          ░░░░░░░░░░░░░██
░██░░█░██░██░█░░          █████░░░░░░████
```

Rule: A cell becomes wall if it has ≥ 5 wall neighbors (B5678/S45678).

---

## Implementation

```typescript
import Alea from 'alea';

function createCaveGrid(width: number, height: number, seed: string | number, fill: number = 0.45): Uint8Array {
  const rng = Alea(seed);
  const grid = new Uint8Array(width * height);
  for (let i = 0; i < grid.length; i++) grid[i] = rng() < fill ? 1 : 0;
  // Solid borders
  for (let x = 0; x < width; x++) { grid[x] = 1; grid[(height-1)*width+x] = 1; }
  for (let y = 0; y < height; y++) { grid[y*width] = 1; grid[y*width+(width-1)] = 1; }
  return grid;
}

function automataStep(grid: Uint8Array, width: number, height: number): Uint8Array {
  const next = new Uint8Array(grid.length);
  for (let y = 1; y < height-1; y++) {
    for (let x = 1; x < width-1; x++) {
      let walls = 0;
      for (let dy = -1; dy <= 1; dy++)
        for (let dx = -1; dx <= 1; dx++)
          walls += grid[(y+dy)*width+(x+dx)];
      const idx = y * width + x;
      next[idx] = grid[idx] === 1 ? (walls >= 4 ? 1 : 0) : (walls >= 5 ? 1 : 0);
    }
  }
  // Keep borders solid
  for (let x = 0; x < width; x++) { next[x] = 1; next[(height-1)*width+x] = 1; }
  for (let y = 0; y < height; y++) { next[y*width] = 1; next[y*width+(width-1)] = 1; }
  return next;
}

function generateCave(seed: string | number, width: number, height: number, iterations: number = 6): Uint8Array {
  let grid = createCaveGrid(width, height, seed);
  for (let i = 0; i < iterations; i++) grid = automataStep(grid, width, height);
  return grid;
}
```

---

## Flood Fill: Finding Connected Regions

```typescript
function floodFill(grid: Uint8Array, width: number, height: number, startX: number, startY: number): Set<number> {
  const region = new Set<number>();
  const stack: [number, number][] = [[startX, startY]];
  while (stack.length > 0) {
    const [x, y] = stack.pop()!;
    const idx = y * width + x;
    if (x < 0 || x >= width || y < 0 || y >= height) continue;
    if (grid[idx] !== 0 || region.has(idx)) continue;
    region.add(idx);
    stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
  }
  return region;
}

function findAllRegions(grid: Uint8Array, width: number, height: number): Set<number>[] {
  const visited = new Set<number>();
  const regions: Set<number>[] = [];
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = y * width + x;
      if (grid[idx] === 0 && !visited.has(idx)) {
        const region = floodFill(grid, width, height, x, y);
        region.forEach(i => visited.add(i));
        regions.push(region);
      }
    }
  }
  return regions;
}
```

---

## Ensuring Connectivity

Connect isolated regions by carving tunnels:

```typescript
function connectRegions(grid: Uint8Array, width: number, height: number): void {
  const regions = findAllRegions(grid, width, height);
  if (regions.length <= 1) return;
  regions.sort((a, b) => b.size - a.size);
  const main = regions[0];

  for (let i = 1; i < regions.length; i++) {
    // Find closest pair between main and isolated region
    let bestDist = Infinity, bestA = 0, bestB = 0;
    for (const a of main) {
      const ax = a % width, ay = Math.floor(a / width);
      for (const b of regions[i]) {
        const bx = b % width, by = Math.floor(b / width);
        const dist = Math.abs(ax-bx) + Math.abs(ay-by);
        if (dist < bestDist) { bestDist = dist; bestA = a; bestB = b; }
      }
    }
    // Carve tunnel
    let x = bestA % width, y = Math.floor(bestA / width);
    const tx = bestB % width, ty = Math.floor(bestB / width);
    while (x !== tx || y !== ty) {
      grid[y * width + x] = 0;
      if (x !== tx) x += x < tx ? 1 : -1;
      else y += y < ty ? 1 : -1;
    }
    regions[i].forEach(idx => main.add(idx));
  }
}
```

---

## Rendering

```typescript
function renderCave(grid: Uint8Array, width: number, height: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(width, height);
  for (let i = 0; i < grid.length; i++) {
    const pi = i * 4;
    if (grid[i] === 1) { imageData.data[pi]=30; imageData.data[pi+1]=25; imageData.data[pi+2]=40; }
    else { imageData.data[pi]=60; imageData.data[pi+1]=55; imageData.data[pi+2]=50; }
    imageData.data[pi+3] = 255;
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| `fillChance` | 0.35 | 0.55 | Open caverns vs tight tunnels |
| `iterations` | 3 | 8 | Rough edges vs smooth walls |
| `birthThreshold` | 4 | 6 | More open vs more closed |

**Juno's notes:**

> "fillChance 0.45 with 5-6 iterations is the sweet spot. Always run connectivity check — nothing worse than a cave the player can see but can't reach."

---

## Exercises

1. **Cave biomes:** Use distance-from-wall to assign colors. Far from walls = "deep cave" (darker). Near walls = "mossy" (green tint).

2. **Multiple rules:** Run 3 iterations with B5678/S45678, then 3 with B5678/S3456. Compare to one rule for all 6.

3. **Cave with rooms:** Before running automata, stamp 3-5 rectangular rooms. The automata smooths edges and connects them organically.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Cellular automata | Grid + neighbor-counting rules + iterations |
| B5678/S45678 | Birth if ≥5 walls, survive if ≥4 walls |
| Fill chance | Initial density — 0.45 is standard |
| Flood fill | BFS/DFS to find connected floor regions |
| Connectivity | Find all regions, tunnel between isolated ones |

---

[← Ch 5](chapter-05-color-palettes.md) | [Ch 7 →](chapter-07-wfc.md)
