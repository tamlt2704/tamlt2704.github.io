# Chapter 16: Performance

[← Ch 15](chapter-15-items-loot.md) | [Ch 17 →](chapter-17-export.md)

---

## Juno's Request

> "Generation is too slow. A planet texture takes 80ms. If I generate 20 assets, that's over a second of freeze. The game needs 60fps — 16ms per frame. We need caching, off-thread generation, and lazy loading."

---

## Strategy 1: Caching

Never regenerate what you've already made:

```typescript
class AssetCache {
  private cache = new Map<string, HTMLCanvasElement>();
  private maxSize: number;
  constructor(maxSize = 100) { this.maxSize = maxSize; }

  get(key: string): HTMLCanvasElement | undefined { return this.cache.get(key); }
  set(key: string, canvas: HTMLCanvasElement): void {
    if (this.cache.size >= this.maxSize) this.cache.delete(this.cache.keys().next().value!);
    this.cache.set(key, canvas);
  }
  has(key: string): boolean { return this.cache.has(key); }
}

// Key includes everything that affects output
function getPlanetTexture(seed: string, size: number): HTMLCanvasElement {
  const key = `planet-${seed}-${size}`;
  if (planetCache.has(key)) return planetCache.get(key)!;
  const texture = generatePlanetTexture(seed, size);
  planetCache.set(key, texture);
  return texture;
}
```

---

## Strategy 2: Web Workers

Move generation off the main thread:

```typescript
// asset-worker.ts
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

self.onmessage = (e: MessageEvent) => {
  const { type, seed, width, height, id } = e.data;
  const imageData = generateAsset(type, seed, width, height);
  self.postMessage({ id, buffer: imageData.data.buffer, width, height }, [imageData.data.buffer]);
};
```

```typescript
// main.ts
class AssetWorkerPool {
  private workers: Worker[] = [];
  private pending = new Map<string, (c: HTMLCanvasElement) => void>();
  private nextId = 0;

  constructor(size = 2) {
    for (let i = 0; i < size; i++) {
      const w = new Worker(new URL('./asset-worker.ts', import.meta.url), {type:'module'});
      w.onmessage = (e) => this.handleResult(e.data);
      this.workers.push(w);
    }
  }

  generate(type: string, seed: string, w: number, h: number): Promise<HTMLCanvasElement> {
    return new Promise(resolve => {
      const id = `${this.nextId++}`;
      this.pending.set(id, resolve);
      this.workers[this.nextId % this.workers.length].postMessage({type, seed, width:w, height:h, id});
    });
  }

  private handleResult(data: {id:string; buffer:ArrayBuffer; width:number; height:number}): void {
    const resolve = this.pending.get(data.id);
    if (!resolve) return;
    this.pending.delete(data.id);
    const canvas = document.createElement('canvas');
    canvas.width = data.width; canvas.height = data.height;
    const ctx = canvas.getContext('2d')!;
    ctx.putImageData(new ImageData(new Uint8ClampedArray(data.buffer), data.width, data.height), 0, 0);
    resolve(canvas);
  }
}
```

---

## Strategy 3: Lazy Loading

Generate on demand, show placeholder until ready:

```typescript
class LazyAssetManager {
  private pool = new AssetWorkerPool(2);
  private cache = new AssetCache(100);

  getAsset(seed: string, type: string, w: number, h: number): HTMLCanvasElement {
    const key = `${type}-${seed}-${w}x${h}`;
    if (this.cache.has(key)) return this.cache.get(key)!;

    // Start async generation, return placeholder
    this.pool.generate(type, seed, w, h).then(canvas => this.cache.set(key, canvas));
    return createPlaceholder(w, h);
  }
}

function createPlaceholder(w: number, h: number): HTMLCanvasElement {
  const c = document.createElement('canvas'); c.width=w; c.height=h;
  const ctx = c.getContext('2d')!;
  ctx.fillStyle='#1a1a2e'; ctx.fillRect(0,0,w,h);
  ctx.strokeStyle='#3a3a5e'; ctx.strokeRect(2,2,w-4,h-4);
  return c;
}
```

---

## Strategy 4: Level of Detail (LOD)

```typescript
function getLODTexture(seed: string, distance: number, cache: AssetCache): HTMLCanvasElement {
  if (distance < 100) return getOrGenerate(cache, seed, 128);  // high detail
  if (distance < 300) return getOrGenerate(cache, seed, 64);   // medium
  return getOrGenerate(cache, seed, 32);                        // low (fast)
}
```

```
Far (>300):    Medium (100-300):   Close (<100):
┌────┐         ┌────────┐          ┌────────────────┐
│░▒▓█│ 32px   │░░▒▒▓▓██│ 64px    │░░░▒▒▒▓▓▓█████│ 128px
└────┘         └────────┘          └────────────────┘
```

---

## Performance Budget

```
Frame budget: 16ms (60fps)
├── Rendering:      4-6ms  (draw cached sprites)
├── Game logic:     3-4ms  (physics, AI)
├── Animation:      1-2ms  (sin, lerp, spring)
├── Cache lookups:  <1ms
└── Headroom:       4-6ms  (GC, browser)

Rule: if generation > 5ms → send to worker
      if generation < 5ms → cache after first call
      Never generate same thing twice
```

---

## Parameter Tuning

| Strategy | When | Tradeoff |
|----------|------|----------|
| Cache | Repeated access | Memory |
| Workers | Multiple assets simultaneously | Complexity |
| Lazy loading | Large worlds | Visible pop-in |
| LOD | Distance-based | Multiple resolutions stored |

---

## Exercises

1. **Cache hit rate:** Add hits/misses counters. Log hit rate every 60 frames. Aim for >90%.

2. **Progressive loading:** Generate 10 assets via worker pool. Show progress bar filling as each completes.

3. **Performance comparison:** Same 128×128 planet on main thread vs worker. Generate 4 simultaneously — workers should win.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Cache | `Map<key, canvas>` — never regenerate same asset |
| Cache key | seed + size + all params |
| Web Worker | Off-thread, communicate via `postMessage` |
| Transferable | `ArrayBuffer` transferred (not copied) |
| Lazy loading | Placeholder until ready |
| LOD | Low-res far, high-res close |
| Budget | 16ms/frame. Generation must not block render. |

---

[← Ch 15](chapter-15-items-loot.md) | [Ch 17 →](chapter-17-export.md)
