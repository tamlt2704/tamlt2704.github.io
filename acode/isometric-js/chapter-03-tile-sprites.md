# Chapter 3: Tile Sprites

[← Chapter 2: Isometric Projection](chapter-02-isometric-projection.md) | [Chapter 4: Mouse Picking →](chapter-04-mouse-picking.md)

---

## The Task

Riku drops a folder in the shared drive: `tiles/grass_01.png`, `tiles/water_01.png`, `tiles/road_straight.png`, `tiles/road_corner.png`. Each is a 64×32 PNG — a diamond-shaped tile with transparent corners.

"Replace those ugly colored diamonds with my actual art. And make sure they line up perfectly — no gaps, no overlaps."

Time to load images and draw them at the right positions.

## Loading Images with Promises

You can't draw an image until it's loaded. And you have multiple tiles. Loading them one by one with callbacks is a mess. Use `Promise.all`:

```typescript
// src/engine/assets.ts
export type SpriteMap = Map<string, HTMLImageElement>;

export function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load: ${src}`));
    img.src = src;
  });
}

export async function loadSprites(
  manifest: Record<string, string>
): Promise<SpriteMap> {
  const entries = Object.entries(manifest);

  const images = await Promise.all(
    entries.map(([_, src]) => loadImage(src))
  );

  const sprites: SpriteMap = new Map();
  entries.forEach(([key, _], i) => {
    sprites.set(key, images[i]);
  });

  return sprites;
}
```

Usage:

```typescript
// src/main.ts
import { loadSprites, SpriteMap } from './engine/assets';

const TILE_MANIFEST = {
  grass: '/assets/tiles/grass_01.png',
  water: '/assets/tiles/water_01.png',
  road: '/assets/tiles/road_straight.png',
  roadCorner: '/assets/tiles/road_corner.png',
};

let sprites: SpriteMap;

async function init() {
  sprites = await loadSprites(TILE_MANIFEST);
  console.log(`Loaded ${sprites.size} sprites`);
  requestAnimationFrame(gameLoop);
}

init();
```

All images load in parallel. The game loop doesn't start until every sprite is ready. No half-rendered frames.

## Drawing Sprites at Isometric Positions

Replace `drawDiamond()` with `drawImage()`:

```typescript
function drawTileSprite(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  screenX: number,
  screenY: number
) {
  // screenX, screenY is the CENTER of the diamond
  // drawImage needs the TOP-LEFT corner of the image
  ctx.drawImage(
    img,
    screenX - TILE_W / 2,
    screenY - TILE_H / 2,
    TILE_W,
    TILE_H
  );
}
```

Wait. That doesn't look right. The tiles overlap wrong. Some have gaps. What's going on?

## The Anchor Point Problem

Here's the issue. In Chapter 2, `cartToIso()` returns the **center** of the diamond:

```
        ╱╲    ← top vertex
       ╱  ╲
      ╱  · ╲   ← center (what cartToIso returns)
       ╲  ╱
        ╲╱    ← bottom vertex
```

But `ctx.drawImage(img, x, y)` draws from the **top-left corner** of the image bounding box. The bounding box of a 64×32 diamond is a 64×32 rectangle:

```
┌────────────────────────────┐  ← drawImage starts here (top-left)
│        ╱╲                  │
│       ╱  ╲                 │
│      ╱    ╲                │  64px wide, 32px tall
│       ╲    ╱               │
│        ╲  ╱                │
│         ╲╱                 │
└────────────────────────────┘
```

The anchor point for isometric tiles is the **top-center** of the diamond — the top vertex. This is where the tile "sits" in world space.

```typescript
const TILE_W = 64;
const TILE_H = 32;

function drawTileSprite(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  isoX: number,
  isoY: number
) {
  // isoX, isoY = the top-center of the diamond (anchor point)
  // To get the top-left of the bounding box: shift left by half width
  ctx.drawImage(
    img,
    isoX - TILE_W / 2,
    isoY,
    TILE_W,
    TILE_H
  );
}
```

But wait — `cartToIso()` returns the **center** of the diamond, not the top. So we need to adjust:

```typescript
function cartToIso(x: number, y: number) {
  return {
    screenX: (x - y) * (TILE_W / 2),
    screenY: (x + y) * (TILE_H / 2),
  };
}

function drawTileAt(ctx: CanvasRenderingContext2D, img: HTMLImageElement, x: number, y: number, offsetX: number, offsetY: number) {
  const { screenX, screenY } = cartToIso(x, y);

  // cartToIso gives us the CENTER of the diamond
  // drawImage needs the TOP-LEFT of the bounding box
  // Center → Top-left: subtract half width horizontally, subtract half height vertically
  const drawX = screenX + offsetX - TILE_W / 2;
  const drawY = screenY + offsetY - TILE_H / 2;

  ctx.drawImage(img, drawX, drawY, TILE_W, TILE_H);
}
```

Now tiles line up perfectly. The key insight: **cartToIso gives the diamond center; drawImage needs the bounding box top-left.**

## The Full Rendering Loop

```typescript
// src/engine/renderer.ts
import { SpriteMap } from './assets';

export class IsoRenderer {
  private ctx: CanvasRenderingContext2D;
  private tileW: number;
  private tileH: number;

  constructor(ctx: CanvasRenderingContext2D, tileW = 64, tileH = 32) {
    this.ctx = ctx;
    this.tileW = tileW;
    this.tileH = tileH;
  }

  cartToIso(x: number, y: number) {
    return {
      screenX: (x - y) * (this.tileW / 2),
      screenY: (x + y) * (this.tileH / 2),
    };
  }

  drawGrid(grid: Grid, sprites: SpriteMap, offsetX: number, offsetY: number) {
    for (let x = 0; x < grid.width; x++) {
      for (let y = 0; y < grid.height; y++) {
        const tile = grid.getTile(x, y);
        if (!tile) continue;

        const sprite = sprites.get(tile);
        if (!sprite) continue;

        const { screenX, screenY } = this.cartToIso(x, y);

        this.ctx.drawImage(
          sprite,
          screenX + offsetX - this.tileW / 2,
          screenY + offsetY - this.tileH / 2,
          this.tileW,
          this.tileH
        );
      }
    }
  }
}
```

## Tile Atlas: One Image, Many Tiles

Loading 50 individual PNGs means 50 HTTP requests. Riku's tile count is growing. Solution: pack all tiles into a single **spritesheet** (tile atlas).

```
┌────┬────┬────┬────┐
│ 0  │ 1  │ 2  │ 3  │   Each cell is 64×32
├────┼────┼────┼────┤   Tile 0 = grass
│ 4  │ 5  │ 6  │ 7  │   Tile 1 = water
├────┼────┼────┼────┤   Tile 2 = road
│ 8  │ 9  │ 10 │ 11 │   ...
└────┴────┴────┴────┘
```

Draw a specific tile from the atlas using the 9-argument `drawImage`:

```typescript
// src/engine/atlas.ts
export class TileAtlas {
  private image: HTMLImageElement;
  private tileW: number;
  private tileH: number;
  private columns: number;

  constructor(image: HTMLImageElement, tileW: number, tileH: number) {
    this.image = image;
    this.tileW = tileW;
    this.tileH = tileH;
    this.columns = Math.floor(image.width / tileW);
  }

  drawTile(
    ctx: CanvasRenderingContext2D,
    tileId: number,
    destX: number,
    destY: number
  ) {
    const srcX = (tileId % this.columns) * this.tileW;
    const srcY = Math.floor(tileId / this.columns) * this.tileH;

    ctx.drawImage(
      this.image,
      srcX, srcY, this.tileW, this.tileH,   // source rectangle
      destX, destY, this.tileW, this.tileH   // destination rectangle
    );
  }
}
```

Usage with the renderer:

```typescript
// src/main.ts
import { loadImage } from './engine/assets';
import { TileAtlas } from './engine/atlas';

let atlas: TileAtlas;

async function init() {
  const atlasImage = await loadImage('/assets/tiles/atlas.png');
  atlas = new TileAtlas(atlasImage, TILE_W, TILE_H);
  requestAnimationFrame(gameLoop);
}
```

Now the grid stores tile IDs (numbers) instead of strings:

```typescript
// Grid cell: 0 = grass, 1 = water, 2 = road, etc.
type TileId = number;

function renderGrid(grid: Grid<TileId>, offsetX: number, offsetY: number) {
  for (let x = 0; x < grid.width; x++) {
    for (let y = 0; y < grid.height; y++) {
      const tileId = grid.getTile(x, y);
      if (tileId === null || tileId < 0) continue;

      const { screenX, screenY } = cartToIso(x, y);

      atlas.drawTile(
        ctx,
        tileId,
        screenX + offsetX - TILE_W / 2,
        screenY + offsetY - TILE_H / 2
      );
    }
  }
}
```

One image load. One texture in GPU memory. Much faster than individual files.

## Handling Tall Sprites

Some of Riku's tiles are taller than 32px — a tree is 64×64, a house is 64×96. The extra height extends **above** the diamond:

```
     🌲          ← sprite extends above the tile
     │ │
┌────┼─┼────┐
│    ╱╲     │   ← the 64×32 diamond footprint
│   ╱  ╲    │
│  ╱    ╲   │
│   ╲  ╱    │
│    ╲╱     │
└───────────┘
```

For tall sprites, offset the Y position by the extra height:

```typescript
function drawTallSprite(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  isoX: number,
  isoY: number,
  tileW: number,
  tileH: number
) {
  const spriteH = img.height;
  const extraHeight = spriteH - tileH;

  // Draw so the bottom of the sprite aligns with the diamond
  ctx.drawImage(
    img,
    isoX - tileW / 2,
    isoY - extraHeight,
    tileW,
    spriteH
  );
}
```

The diamond footprint stays at `(isoX, isoY)`. The sprite just extends upward. This becomes critical in Chapter 6 (depth sorting) and Chapter 7 (multi-tile objects).

## Putting It Together

```typescript
// src/main.ts
import { Grid } from './engine/grid';
import { IsoRenderer } from './engine/renderer';
import { loadSprites, SpriteMap } from './engine/assets';

const canvas = document.getElementById('game') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const TILE_W = 64;
const TILE_H = 32;

const grid = new Grid(10, 10);
const renderer = new IsoRenderer(ctx, TILE_W, TILE_H);

let sprites: SpriteMap;

async function init() {
  sprites = await loadSprites({
    grass: '/assets/tiles/grass_01.png',
    water: '/assets/tiles/water_01.png',
    road: '/assets/tiles/road_straight.png',
  });

  // Set up some terrain
  grid.setTile(3, 3, 'water');
  grid.setTile(3, 4, 'water');
  grid.setTile(4, 3, 'water');
  grid.setTile(4, 4, 'water');

  for (let i = 0; i < 10; i++) {
    grid.setTile(i, 5, 'road');
  }

  requestAnimationFrame(gameLoop);
}

function gameLoop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const offsetX = canvas.width / 2;
  const offsetY = 100;

  renderer.drawGrid(grid, sprites, offsetX, offsetY);

  requestAnimationFrame(gameLoop);
}

init();
```

Run it. The colored diamonds are gone. Riku's pixel art tiles sit perfectly in the isometric grid — grass textures, water ripples, stone roads. It looks like a game.

## Riku's Reaction

Riku zooms in on the browser: "That's it. That's my art. But I can't click on anything — how do I select a tile to see what's there?"

You: "Mouse picking. I need to convert the click position back to grid coordinates. That's the inverse transform."

Riku: "The `isoToCart` thing from last chapter?"

You: "Exactly. But there's a catch with how diamonds work..."

## What You Built

- **Image loading** — `Promise.all` for parallel sprite loading
- **Sprite positioning** — anchor point at diamond center, offset to top-left for drawImage
- **Tile atlas** — single spritesheet with source rectangle slicing
- **Tall sprites** — extra height extends above the diamond footprint
- **The coordinate dance** — cartToIso gives center, drawImage needs top-left corner

The grid has real art now. Next problem: clicking on a tile and knowing which one you hit.

---

[← Chapter 2: Isometric Projection](chapter-02-isometric-projection.md) | [Chapter 4: Mouse Picking →](chapter-04-mouse-picking.md)
