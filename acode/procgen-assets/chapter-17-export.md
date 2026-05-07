# Chapter 17: Export

[← Ch 16](chapter-16-performance.md) | [Ch 18 →](chapter-18-designer-tools.md)

---

## Juno's Request

> "I need to export generated assets as files. PNG sprite sheets for marketing. Atlas textures for the mobile port. And metadata — which sprite is where in the sheet. Batch generation: 100 ships packed into one texture atlas with a JSON manifest."

---

## Render to PNG

The simplest export — canvas to downloadable file:

```typescript
function canvasToPNG(canvas: HTMLCanvasElement, filename: string): void {
  canvas.toBlob(blob => {
    if (!blob) return;
    const link = document.createElement('a');
    link.download = filename;
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  }, 'image/png');
}

// Export a single asset
function exportAsset(seed: string): void {
  const canvas = generatePlanetTexture(seed, 256);
  canvasToPNG(canvas, `planet-${seed}.png`);
}
```

---

## Sprite Sheet Packing (Shelf Algorithm)

```typescript
interface PackedSprite { id: string; x: number; y: number; width: number; height: number; canvas: HTMLCanvasElement; }

function shelfPack(sprites: {id:string; canvas:HTMLCanvasElement}[], maxWidth = 1024): {atlas:HTMLCanvasElement; packed:PackedSprite[]} {
  const sorted = [...sprites].sort((a,b) => b.canvas.height - a.canvas.height);
  const packed: PackedSprite[] = [];
  let shelfY = 0, shelfH = 0, shelfX = 0;

  for (const sprite of sorted) {
    const w = sprite.canvas.width, h = sprite.canvas.height;
    if (shelfX + w > maxWidth) { shelfY += shelfH; shelfH = 0; shelfX = 0; }
    packed.push({ id: sprite.id, x: shelfX, y: shelfY, width: w, height: h, canvas: sprite.canvas });
    shelfX += w;
    shelfH = Math.max(shelfH, h);
  }

  const totalH = shelfY + shelfH;
  const atlas = document.createElement('canvas');
  atlas.width = maxWidth; atlas.height = totalH;
  const ctx = atlas.getContext('2d')!;
  for (const p of packed) ctx.drawImage(p.canvas, p.x, p.y);
  return { atlas, packed };
}
```

---

## Atlas JSON Metadata

```typescript
interface AtlasManifest {
  meta: { image: string; size: {w:number;h:number}; generated: string; };
  frames: { id: string; frame: {x:number;y:number;w:number;h:number}; seed: string; }[];
}

function generateManifest(packed: PackedSprite[], atlasW: number, atlasH: number, imageName: string): AtlasManifest {
  return {
    meta: { image: imageName, size: {w:atlasW, h:atlasH}, generated: new Date().toISOString() },
    frames: packed.map(p => ({ id: p.id, frame: {x:p.x, y:p.y, w:p.width, h:p.height}, seed: p.id })),
  };
}

function exportManifest(manifest: AtlasManifest, filename: string): void {
  const blob = new Blob([JSON.stringify(manifest, null, 2)], {type:'application/json'});
  const link = document.createElement('a');
  link.download = filename; link.href = URL.createObjectURL(blob);
  link.click(); URL.revokeObjectURL(link.href);
}
```

---

## Batch Generation Pipeline

```typescript
async function batchGenerate(seeds: string[], type: string, size: number): Promise<{atlas:HTMLCanvasElement; manifest:AtlasManifest}> {
  const sprites = seeds.map(seed => ({
    id: `${type}-${seed}`,
    canvas: type === 'ship' ? generateSprite(seed, size, size) : generatePlanetTexture(seed, size),
  }));
  const { atlas, packed } = shelfPack(sprites);
  const manifest = generateManifest(packed, atlas.width, atlas.height, `${type}-atlas.png`);
  return { atlas, manifest };
}

// Usage: 50 ships → one atlas + JSON
const seeds = Array.from({length:50}, (_,i) => `ship-${i}`);
const { atlas, manifest } = await batchGenerate(seeds, 'ship', 32);
canvasToPNG(atlas, 'ships-atlas.png');
exportManifest(manifest, 'ships-atlas.json');
```

---

## Loading an Atlas in Game

```typescript
class SpriteAtlas {
  private image: HTMLImageElement;
  private frames: Map<string, {x:number;y:number;w:number;h:number}>;

  constructor(src: string, manifest: AtlasManifest) {
    this.image = new Image(); this.image.src = src;
    this.frames = new Map(manifest.frames.map(f => [f.id, f.frame]));
  }

  draw(ctx: CanvasRenderingContext2D, id: string, x: number, y: number, scale = 1): void {
    const f = this.frames.get(id);
    if (!f) return;
    ctx.drawImage(this.image, f.x, f.y, f.w, f.h, x, y, f.w*scale, f.h*scale);
  }
}
```

---

## Visual Result

```
ships-atlas.png (50 ships packed):
┌────────────────────────────────────────────┐
│ ▲ ◆ ▼ ◇ △ ▲ ◆ ▼ ◇ △ ▲ ◆ ▼ ◇ △ ▲ ◆ ▼ │
│╱█╲╱█╲╲█╱╱█╲╱█╲╱█╲╱█╲╲█╱╱█╲╱█╲╱█╲╱█╲╲█╱│
│ ... (packed efficiently)                   │
└────────────────────────────────────────────┘

ships-atlas.json:
{ "frames": [{"id":"ship-0","frame":{"x":0,"y":0,"w":32,"h":32}}, ...] }
```

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| Atlas size | 512-4096px | "1024 safe for all GPUs" |
| Sprite padding | 0-2px | "1px prevents bleeding" |
| Sort order | Height-first | "Better shelf packing" |
| Batch size | 10-200 | "50-100 per atlas" |

---

## Exercises

1. **Padding:** Add 1px transparent padding around each sprite. Update manifest coordinates.

2. **Power-of-two:** Find smallest power-of-two dimensions that fit all sprites.

3. **Multi-atlas:** If sprites don't fit in 1024×1024, split into multiple atlases automatically.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| `canvas.toBlob()` | Export as PNG Blob |
| Shelf packing | Sort by height, place left-to-right, new row when full |
| Atlas manifest | JSON with frame positions and metadata |
| Batch generation | Loop seeds → generate → pack → export |
| SpriteAtlas class | Load atlas + manifest, draw by ID |

---

[← Ch 16](chapter-16-performance.md) | [Ch 18 →](chapter-18-designer-tools.md)
