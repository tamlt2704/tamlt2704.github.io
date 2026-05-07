# Chapter 12: Pixel Sprites

[← Ch 11](chapter-11-creatures.md) | [Ch 13 →](chapter-13-faces-icons.md)

---

## Juno's Request

> "I need pixel art sprites — spaceships, characters, enemies — generated, not drawn. Noise creates a silhouette, mirror it for symmetry, add an outline, fill with palette colors. 16×16 or 32×32. They should look hand-drawn but they're pure algorithm."

---

## The Algorithm

```
1. Generate noise mask (half-width × full-height)
2. Threshold → binary silhouette
3. Mirror horizontally → symmetric shape
4. Detect outline pixels (filled with empty neighbor)
5. Color: body from palette, darker interior detail
```

---

## Implementation

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

function generateSprite(seed: string | number, width = 16, height = 16, threshold = 0.3, noiseScale = 0.3): HTMLCanvasElement {
  const rng = Alea(seed);
  const noise = createNoise2D(rng);
  const halfW = Math.ceil(width / 2);
  const mask = new Uint8Array(width * height); // 0=empty, 1=body, 2=outline

  // Generate half-mask with bias toward center
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < halfW; x++) {
      const centerBias = 1 - (x/halfW) * 0.5;
      const vertBias = 1 - Math.abs(y-height/2)/(height/2) * 0.3;
      const n = (noise(x*noiseScale, y*noiseScale) + 1) / 2;
      if (n * centerBias * vertBias > threshold) {
        mask[y*width+x] = 1;
        mask[y*width+(width-1-x)] = 1; // mirror
      }
    }
  }

  // Outline detection
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (mask[y*width+x] !== 1) continue;
      const neighbors = [[x-1,y],[x+1,y],[x,y-1],[x,y+1]];
      for (const [nx,ny] of neighbors) {
        if (nx<0||nx>=width||ny<0||ny>=height||mask[ny*width+nx]===0) {
          mask[y*width+x] = 2; break;
        }
      }
    }
  }

  // Render
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(width, height);

  const hue = rng() * 360;
  const body = hslToRgb(hue, 50, 50);
  const dark = hslToRgb(hue, 40, 30);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y*width+x)*4, cell = mask[y*width+x];
      if (cell === 2) { imageData.data[i]=20; imageData.data[i+1]=20; imageData.data[i+2]=30; imageData.data[i+3]=255; }
      else if (cell === 1) {
        const detail = noise(x*0.5, y*0.5) > 0;
        const [r,g,b] = detail ? body : dark;
        imageData.data[i]=r; imageData.data[i+1]=g; imageData.data[i+2]=b; imageData.data[i+3]=255;
      }
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Ship Configs

```typescript
const SHIP_CONFIGS = {
  fighter: { width:12, height:16, threshold:0.25, noiseScale:0.25 },
  cruiser: { width:16, height:24, threshold:0.2, noiseScale:0.2 },
  scout:   { width:10, height:10, threshold:0.35, noiseScale:0.35 },
};
```

---

## Batch Generation

```typescript
function generateFleet(baseSeed: string, count = 20, config = SHIP_CONFIGS.fighter): HTMLCanvasElement {
  const cols = 5, rows = Math.ceil(count/cols);
  const pad = 4, cellW = config.width+pad, cellH = config.height+pad;
  const canvas = document.createElement('canvas');
  canvas.width = cols*cellW; canvas.height = rows*cellH;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < count; i++) {
    const sprite = generateSprite(`${baseSeed}-${i}`, config.width, config.height, config.threshold, config.noiseScale);
    ctx.drawImage(sprite, (i%cols)*cellW+pad/2, Math.floor(i/cols)*cellH+pad/2);
  }
  return canvas;
}
```

---

## Pixel-Perfect Display

```typescript
function displaySprite(sprite: HTMLCanvasElement, scale = 4): HTMLCanvasElement {
  const display = document.createElement('canvas');
  display.width = sprite.width * scale; display.height = sprite.height * scale;
  display.style.imageRendering = 'pixelated';
  const ctx = display.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(sprite, 0, 0, display.width, display.height);
  return display;
}
```

---

## Visual Result

```
Generated fleet (all unique, all symmetric):
┌───┬───┬───┬───┬───┐
│ ▲ │ ◆ │ ▼ │ ◇ │ △ │
│╱█╲│╱█╲│╲█╱│╱█╲│╱█╲│
│███│███│███│███│███│
│╲█╱│╲█╱│╱█╲│╲█╱│╲█╱│
├───┼───┼───┼───┼───┤
│ ◆ │ ▲ │ ◇ │ △ │ ▼ │
│███│╱█╲│╱█╲│╱█╲│╲█╱│
│█ █│█ █│███│█ █│█ █│
│███│╲█╱│╲█╱│╲█╱│╱█╲│
└───┴───┴───┴───┴───┘
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| `threshold` | 0.15 | 0.45 | Dense/bulky vs sparse/spindly |
| `noiseScale` | 0.15 | 0.5 | Smooth blobs vs detailed |
| Sprite size | 8×8 | 32×32 | Minimal vs detailed |

**Juno's notes:**

> "12×16 is the sweet spot for ships. The outline is critical — without it, sprites look like noise. With it, they look drawn."

---

## Exercises

1. **Engine glow:** Find bottom-center filled pixels. Add bright orange/yellow rows below as exhaust.

2. **Damage states:** Same seed, but randomly remove 10-20% of body pixels and add dark red "scorch" nearby.

3. **Enemy classes:** Wide/flat for tanks, tall/thin for scouts, small/dense for swarms. Generate 10 of each.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Half-mask | Generate left half, mirror for symmetry |
| Noise threshold | `noise > threshold` → filled pixel |
| Center bias | More fill toward center, less at edges |
| Outline detection | Filled pixel with any empty neighbor |
| Pixel-perfect | `imageSmoothingEnabled = false` |
| Batch | Sequential seeds: `seed-0`, `seed-1`, etc. |

---

[← Ch 11](chapter-11-creatures.md) | [Ch 13 →](chapter-13-faces-icons.md)
