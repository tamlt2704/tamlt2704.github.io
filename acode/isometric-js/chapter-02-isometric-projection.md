# Chapter 2: Isometric Projection

[← Chapter 1: Canvas & Game Loop](chapter-01-canvas-game-loop.md) | [Chapter 3: Tile Sprites →](chapter-03-tile-sprites.md)

---

## The Task

Riku: "Make the grid look like this." He shows you a screenshot of SimCity 2000. Diamond-shaped tiles arranged in a grid that looks 3D but isn't.

You need to transform flat (x, y) grid coordinates into screen positions that create the isometric illusion.

## The Math: Why It Works

Isometric projection takes a top-down grid and rotates it 45°, then squishes it vertically by half. The result: a diamond grid that looks like you're viewing it from above at an angle.

```
Top-down:                    Isometric:
┌──┬──┬──┐                       ◇
│  │  │  │                     ◇   ◇
├──┼──┼──┤        →         ◇   ◇   ◇
│  │  │  │                     ◇   ◇
├──┼──┼──┤                       ◇
│  │  │  │
└──┴──┴──┘
```

The transform:

```typescript
const TILE_W = 64;  // Width of the diamond
const TILE_H = 32;  // Height of the diamond (half of width = 2:1 ratio)

function cartToIso(cartX: number, cartY: number) {
  return {
    screenX: (cartX - cartY) * (TILE_W / 2),
    screenY: (cartX + cartY) * (TILE_H / 2),
  };
}
```

### Why (x - y) and (x + y)?

Think of it as two operations:
1. **Rotate 45°**: The x-axis goes down-right, the y-axis goes down-left
2. **Scale vertically by 0.5**: Squish the height to create the 2:1 ratio

- `(x - y)` gives the horizontal offset — moving right in x goes right on screen, moving right in y goes left on screen
- `(x + y)` gives the vertical offset — both x and y move downward on screen

```typescript
// Tile (0,0) → screen (0, 0)
// Tile (1,0) → screen (32, 16)   — down-right
// Tile (0,1) → screen (-32, 16)  — down-left
// Tile (1,1) → screen (0, 32)    — straight down
```

## Drawing the Isometric Grid

```typescript
function drawIsoGrid(grid: Grid, offsetX: number, offsetY: number) {
  for (let x = 0; x < grid.width; x++) {
    for (let y = 0; y < grid.height; y++) {
      const { screenX, screenY } = cartToIso(x, y);

      // Offset to center on canvas
      const drawX = screenX + offsetX;
      const drawY = screenY + offsetY;

      drawDiamond(drawX, drawY, grid.getTile(x, y));
    }
  }
}

function drawDiamond(cx: number, cy: number, tile: TileType | null) {
  ctx.beginPath();
  ctx.moveTo(cx, cy - TILE_H / 2);             // Top
  ctx.lineTo(cx + TILE_W / 2, cy);             // Right
  ctx.lineTo(cx, cy + TILE_H / 2);             // Bottom
  ctx.lineTo(cx - TILE_W / 2, cy);             // Left
  ctx.closePath();

  ctx.fillStyle = getTileColor(tile);
  ctx.fill();
  ctx.strokeStyle = '#1a3a1a';
  ctx.lineWidth = 1;
  ctx.stroke();
}
```

Run it. You see a diamond-shaped grid. The flat squares are gone — replaced by the isometric illusion.

## Centering the Grid

The grid's (0,0) tile renders at the top. To center it on screen:

```typescript
function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Center the grid on the canvas
  const offsetX = canvas.width / 2;
  const offsetY = 150;  // Some padding from top

  drawIsoGrid(grid, offsetX, offsetY);
}
```

## The Inverse Transform: Screen → Grid

You'll need this for mouse picking (Chapter 4), but let's derive it now.

Given a screen position, which grid tile is it over?

```typescript
function isoToCart(screenX: number, screenY: number) {
  // Inverse of the cartToIso transform
  return {
    cartX: Math.floor((screenX / (TILE_W / 2) + screenY / (TILE_H / 2)) / 2),
    cartY: Math.floor((screenY / (TILE_H / 2) - screenX / (TILE_W / 2)) / 2),
  };
}
```

This is the algebraic inverse of `cartToIso`. If:
```
screenX = (x - y) * (TILE_W / 2)
screenY = (x + y) * (TILE_H / 2)
```

Then solving for x and y:
```
x = (screenX / (TILE_W/2) + screenY / (TILE_H/2)) / 2
y = (screenY / (TILE_H/2) - screenX / (TILE_W/2)) / 2
```

## Coordinate Spaces

Three coordinate systems you'll juggle throughout:

| Space | Units | Example |
|---|---|---|
| **Grid** (cartesian) | Tile indices | (3, 5) = column 3, row 5 |
| **World** (isometric) | Pixels in world space | (128, 96) = projected position |
| **Screen** | Pixels on canvas | (640, 360) = where it actually draws |

```
Grid (3, 5) → cartToIso → World (−64, 128) → + camera offset → Screen (576, 278)
```

For now, world and screen are the same (no camera). Chapter 5 adds the camera offset.

## The Rendering Engine

```typescript
// src/engine/renderer.ts
export class IsoRenderer {
  ctx: CanvasRenderingContext2D;
  tileWidth: number;
  tileHeight: number;

  constructor(ctx: CanvasRenderingContext2D, tileWidth = 64, tileHeight = 32) {
    this.ctx = ctx;
    this.tileWidth = tileWidth;
    this.tileHeight = tileHeight;
  }

  cartToIso(x: number, y: number): { screenX: number; screenY: number } {
    return {
      screenX: (x - y) * (this.tileWidth / 2),
      screenY: (x + y) * (this.tileHeight / 2),
    };
  }

  isoToCart(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: Math.floor((screenX / (this.tileWidth / 2) + screenY / (this.tileHeight / 2)) / 2),
      y: Math.floor((screenY / (this.tileHeight / 2) - screenX / (this.tileWidth / 2)) / 2),
    };
  }

  drawGrid(grid: Grid, offsetX: number, offsetY: number) {
    for (let x = 0; x < grid.width; x++) {
      for (let y = 0; y < grid.height; y++) {
        const { screenX, screenY } = this.cartToIso(x, y);
        this.drawDiamond(screenX + offsetX, screenY + offsetY, grid.getTile(x, y));
      }
    }
  }

  drawDiamond(cx: number, cy: number, tile: TileType | null) {
    const hw = this.tileWidth / 2;
    const hh = this.tileHeight / 2;

    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - hh);
    this.ctx.lineTo(cx + hw, cy);
    this.ctx.lineTo(cx, cy + hh);
    this.ctx.lineTo(cx - hw, cy);
    this.ctx.closePath();

    this.ctx.fillStyle = this.getTileColor(tile);
    this.ctx.fill();
    this.ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    this.ctx.stroke();
  }

  private getTileColor(tile: TileType | null): string {
    switch (tile) {
      case 'grass': return '#4a8c3f';
      case 'water': return '#2980b9';
      case 'road': return '#7f8c8d';
      default: return '#2c3e50';
    }
  }
}
```

## Adding Variety

Make the grid more interesting:

```typescript
function initGrid(width: number, height: number): Grid {
  const grid = new Grid(width, height);

  // Add some water
  for (let x = 3; x < 6; x++) {
    for (let y = 6; y < 9; y++) {
      grid.setTile(x, y, 'water');
    }
  }

  // Add a road
  for (let i = 0; i < width; i++) {
    grid.setTile(i, 4, 'road');
  }

  return grid;
}
```

Now you see green grass, blue water, and grey roads — all in isometric perspective.

## Riku's Reaction

Riku: "That's it! That's the look. But those colored diamonds are ugly. I have actual tile images — 64×32 PNGs with grass textures, water ripples, stone roads. Can you use those instead?"

You: "Next chapter."

## What You Built

- **cartToIso()** — the core transform: grid (x,y) → screen position
- **isoToCart()** — the inverse: screen position → grid (x,y)
- **Diamond rendering** — draw tiles as diamonds using canvas paths
- **Coordinate spaces** — grid, world, and screen
- **The 2:1 ratio** — tile width = 2 × tile height for clean pixel art

The grid looks isometric. But colored diamonds aren't a game. Next: replacing them with Riku's actual tile sprites.

---

[← Chapter 1: Canvas & Game Loop](chapter-01-canvas-game-loop.md) | [Chapter 3: Tile Sprites →](chapter-03-tile-sprites.md)
