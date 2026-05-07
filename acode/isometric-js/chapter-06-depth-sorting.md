# Chapter 6: Depth Sorting

[← Chapter 5: Camera](chapter-05-camera.md) | [Chapter 7: Multi-Tile Objects →](chapter-07-multi-tile-objects.md)

---

## The Task

Riku places a house at tile (2, 3). Then a tree at tile (3, 2). The tree should be behind the house — it's further from the viewer. But it renders on top.

"The tree is floating in front of the house. This looks broken."

It is. You're drawing tiles in grid order: `x=0..9, y=0..9`. That's not the same as visual order in isometric projection.

## The Problem: Grid Order ≠ Visual Order

In isometric view, the "camera" looks from the top-right corner down toward the bottom-left. Objects closer to the bottom of the screen are closer to the viewer and should render **on top** of objects further up.

```
Grid order (x then y):        Visual order (back to front):

  0,0 → 1,0 → 2,0              0,0
  0,1 → 1,1 → 2,1            1,0  0,1
  0,2 → 1,2 → 2,2          2,0  1,1  0,2
                               2,1  1,2
                                 2,2
```

Drawing in grid order means tile (3, 2) draws after (2, 3) — but visually (2, 3) is in front. The last thing drawn appears on top. Wrong order = wrong depth.

## The Painter's Algorithm

The fix is simple in concept: **draw back-to-front**. Like a painter who paints the background first, then foreground objects on top.

For isometric with a 2:1 ratio and the camera looking from the top-right:

- Tiles further from the viewer (top of screen) draw first
- Tiles closer to the viewer (bottom of screen) draw last

The screen Y position determines depth. And `screenY = (x + y) * (TILE_H / 2)`. So tiles with a smaller `(x + y)` are further back.

## Sort Order: x + y, Then y

The correct iteration order:

1. Sort by `(x + y)` ascending — back rows first
2. Within the same `(x + y)`, sort by `y` ascending — left-to-right within a row

```typescript
function getDrawOrder(gridWidth: number, gridHeight: number): Array<{ x: number; y: number }> {
  const order: Array<{ x: number; y: number }> = [];

  for (let x = 0; x < gridWidth; x++) {
    for (let y = 0; y < gridHeight; y++) {
      order.push({ x, y });
    }
  }

  order.sort((a, b) => {
    const sumA = a.x + a.y;
    const sumB = b.x + b.y;
    if (sumA !== sumB) return sumA - sumB;  // Back rows first
    return a.y - b.y;                        // Left to right within row
  });

  return order;
}
```

But sorting every frame is wasteful for a static grid. Pre-compute the order once:

```typescript
// Compute once at init
const drawOrder = getDrawOrder(grid.width, grid.height);

// Use every frame
function renderGrid() {
  for (const { x, y } of drawOrder) {
    const tile = grid.getTile(x, y);
    if (!tile) continue;

    const { screenX, screenY } = cartToIso(x, y);
    drawTileSprite(ctx, sprites.get(tile)!, screenX + offsetX, screenY + offsetY);
  }
}
```

## The Diagonal Loop (No Sort Needed)

Even better — iterate diagonally so no sort is required:

```typescript
function renderGridSorted(grid: Grid, offsetX: number, offsetY: number) {
  // Iterate by diagonal (x + y = constant)
  for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= grid.width || y >= grid.height) continue;

      const tile = grid.getTile(x, y);
      if (!tile) continue;

      const { screenX, screenY } = cartToIso(x, y);
      const sprite = sprites.get(tile);
      if (sprite) {
        ctx.drawImage(
          sprite,
          screenX + offsetX - TILE_W / 2,
          screenY + offsetY - TILE_H / 2,
          TILE_W,
          TILE_H
        );
      }
    }
  }
}
```

This iterates along diagonals: first (0,0), then (1,0) and (0,1), then (2,0), (1,1), (0,2), etc. Each diagonal has the same `x + y` value — same screen Y — same depth. Within a diagonal, we go left to right.

## Visualizing the Draw Order

```
Draw order (number = when it's drawn):

         1
       2   3
     4   5   6
       7   8
         9

Tile (0,0) = 1 (drawn first, furthest back)
Tile (2,2) = 9 (drawn last, closest to viewer)
```

Objects drawn later appear on top. A building at (2,2) correctly covers a tree at (1,1).

## Separating Ground and Objects

Ground tiles are flat — they never overlap each other (same height). Objects (buildings, trees) can overlap. Render in two passes:

```typescript
function render() {
  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  // Pass 1: Ground tiles (order doesn't matter for flat tiles, but keep it sorted anyway)
  for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= grid.width || y >= grid.height) continue;

      drawGroundTile(x, y);
    }
  }

  // Pass 2: Objects (buildings, trees) — order matters!
  for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= grid.width || y >= grid.height) continue;

      const obj = objects.getAt(x, y);
      if (obj) {
        drawObject(obj, x, y);
      }
    }
  }

  ctx.restore();
}
```

## Tall Objects and Their Sort Position

A tree sprite is 64×96 — it extends 64px above the tile. Where does it sort?

**By its base tile.** The tree's feet are at (3, 2), so it sorts at (3, 2). The sprite extends upward visually, but its depth position is determined by where it stands.

```
         🌲  ← sprite extends up (visual only)
         │
    ─────┼─────
         ◇    ← base tile (3,2) — this determines sort order
```

```typescript
interface GameObject {
  gridX: number;
  gridY: number;
  sprite: HTMLImageElement;
  spriteHeight: number;  // Full height of the sprite image
}

function drawObject(obj: GameObject, offsetX: number, offsetY: number) {
  const { screenX, screenY } = cartToIso(obj.gridX, obj.gridY);

  // Extra height above the tile
  const extraH = obj.spriteHeight - TILE_H;

  ctx.drawImage(
    obj.sprite,
    screenX + offsetX - TILE_W / 2,
    screenY + offsetY - TILE_H / 2 - extraH,  // Shift up by extra height
    TILE_W,
    obj.spriteHeight
  );
}
```

## The Edge Case: Same-Row Overlap

Two buildings on the same diagonal (same `x + y`) can still overlap if one is tall. The tiebreaker — sort by `y` within the same diagonal — handles this:

```
Building A at (3, 1): sum = 4, drawn first
Building B at (1, 3): sum = 4, drawn second (higher y)
```

Building B is to the left and slightly in front. Drawing it second means it correctly overlaps A's right edge.

## Dynamic Objects: Sort Every Frame

For moving objects (characters, vehicles), you can't pre-compute order. Sort them each frame:

```typescript
function renderDynamicObjects(objects: GameObject[]) {
  // Sort by depth: (x + y) ascending, then y ascending
  const sorted = [...objects].sort((a, b) => {
    const sumA = a.gridX + a.gridY;
    const sumB = b.gridX + b.gridY;
    if (sumA !== sumB) return sumA - sumB;
    return a.gridY - b.gridY;
  });

  for (const obj of sorted) {
    drawObject(obj, worldOffsetX, worldOffsetY);
  }
}
```

For a small number of dynamic objects (< 100), sorting every frame is fine. For thousands, you'd use spatial partitioning (Chapter 12).

## The Complete Renderer with Depth Sorting

```typescript
// src/engine/renderer.ts
export class IsoRenderer {
  private ctx: CanvasRenderingContext2D;
  private tileW: number;
  private tileH: number;

  constructor(ctx: CanvasRenderingContext2D, tileW = 64, tileH = 32) {
    this.ctx = ctx;
    this.tileW = tileW;
    this.tileH = tileH;
  }

  renderWorld(
    grid: Grid,
    objects: GameObject[],
    sprites: SpriteMap,
    offsetX: number,
    offsetY: number
  ) {
    // Sorted diagonal iteration
    for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
      for (let x = 0; x <= sum; x++) {
        const y = sum - x;
        if (x >= grid.width || y >= grid.height) continue;

        // Draw ground tile
        const tile = grid.getTile(x, y);
        if (tile) {
          const sprite = sprites.get(tile);
          if (sprite) {
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

        // Draw any object at this position
        const obj = objects.find(o => o.gridX === x && o.gridY === y);
        if (obj) {
          this.drawObject(obj, offsetX, offsetY);
        }
      }
    }
  }

  private drawObject(obj: GameObject, offsetX: number, offsetY: number) {
    const { screenX, screenY } = this.cartToIso(obj.gridX, obj.gridY);
    const extraH = obj.sprite.height - this.tileH;

    this.ctx.drawImage(
      obj.sprite,
      screenX + offsetX - this.tileW / 2,
      screenY + offsetY - this.tileH / 2 - extraH,
      this.tileW,
      obj.sprite.height
    );
  }

  private cartToIso(x: number, y: number) {
    return {
      screenX: (x - y) * (this.tileW / 2),
      screenY: (x + y) * (this.tileH / 2),
    };
  }
}
```

## Riku's Reaction

The tree at (3, 2) now renders behind the house at (2, 3). Buildings overlap correctly. The city looks right.

Riku: "Perfect. But my town hall is 2×2 tiles. When I place it, it only occupies one tile. The other three tiles show through it."

You: "Multi-tile objects. The building needs a footprint — and only one tile 'owns' it for sorting purposes."

## What You Built

- **Painter's algorithm** — draw back-to-front so closer objects cover farther ones
- **Sort key: x + y** — determines depth in isometric projection
- **Diagonal iteration** — no sort needed, iterate by `sum = x + y`
- **Two-pass rendering** — ground first, objects second
- **Tall sprite positioning** — sort by base tile, draw sprite extending upward
- **Dynamic object sorting** — sort moving objects each frame by depth

Depth sorting is solved for single-tile objects. Next: buildings that span multiple tiles.

---

[← Chapter 5: Camera](chapter-05-camera.md) | [Chapter 7: Multi-Tile Objects →](chapter-07-multi-tile-objects.md)
