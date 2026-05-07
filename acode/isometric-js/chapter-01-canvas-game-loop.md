# Chapter 1: The Canvas & Game Loop

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Isometric Projection →](chapter-02-isometric-projection.md)

---

## The Task

Riku sends you the first tile — a 64×32 green diamond. "Just draw a grid of these. I need to see how they tile before I draw more."

Before isometric math, you need the basics: a canvas, a game loop, and a flat grid.

## Setting Up the Canvas

```typescript
// src/main.ts
const canvas = document.getElementById('game') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

window.addEventListener('resize', resize);
resize();
```

The canvas fills the window. Every time the window resizes, the canvas resizes too.

## The Game Loop

Games don't render once — they render 60 times per second. The game loop:

```typescript
let lastTime = 0;

function gameLoop(timestamp: number) {
  const deltaTime = (timestamp - lastTime) / 1000; // seconds
  lastTime = timestamp;

  update(deltaTime);
  render();

  requestAnimationFrame(gameLoop);
}

function update(dt: number) {
  // Game logic here (movement, physics, input)
}

function render() {
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw everything
  drawGrid();
}

requestAnimationFrame(gameLoop);
```

`requestAnimationFrame` syncs with the monitor's refresh rate (usually 60fps). `deltaTime` ensures consistent speed regardless of frame rate.

## Drawing a Flat Grid

Start with a simple top-down grid — squares:

```typescript
const GRID_SIZE = 10;
const TILE_SIZE = 48;

function drawGrid() {
  for (let x = 0; x < GRID_SIZE; x++) {
    for (let y = 0; y < GRID_SIZE; y++) {
      const screenX = x * TILE_SIZE + 100;
      const screenY = y * TILE_SIZE + 100;

      ctx.strokeStyle = '#444';
      ctx.strokeRect(screenX, screenY, TILE_SIZE, TILE_SIZE);

      // Alternate colors for visibility
      ctx.fillStyle = (x + y) % 2 === 0 ? '#2d5a27' : '#3a7a34';
      ctx.fillRect(screenX, screenY, TILE_SIZE, TILE_SIZE);
    }
  }
}
```

You see a flat checkerboard. Boring. But it proves the loop works and tiles render correctly.

## The Grid Data Structure

A 2D array represents the world:

```typescript
type TileType = 'grass' | 'water' | 'road' | 'empty';

const grid: TileType[][] = [];

function initGrid(width: number, height: number) {
  for (let x = 0; x < width; x++) {
    grid[x] = [];
    for (let y = 0; y < height; y++) {
      grid[x][y] = 'grass';
    }
  }
}

initGrid(GRID_SIZE, GRID_SIZE);
```

Each cell stores what type of tile it is. Later, this becomes more complex (buildings, elevation, entities), but a 2D array is the foundation.

## Separating Concerns

```typescript
// src/engine/grid.ts
export class Grid {
  width: number;
  height: number;
  tiles: TileType[][];

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.tiles = [];

    for (let x = 0; x < width; x++) {
      this.tiles[x] = [];
      for (let y = 0; y < height; y++) {
        this.tiles[x][y] = 'grass';
      }
    }
  }

  getTile(x: number, y: number): TileType | null {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) return null;
    return this.tiles[x][y];
  }

  setTile(x: number, y: number, type: TileType) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      this.tiles[x][y] = type;
    }
  }
}
```

```typescript
// src/engine/renderer.ts
export class Renderer {
  ctx: CanvasRenderingContext2D;
  tileSize: number;

  constructor(ctx: CanvasRenderingContext2D, tileSize: number) {
    this.ctx = ctx;
    this.tileSize = tileSize;
  }

  clear(width: number, height: number) {
    this.ctx.clearRect(0, 0, width, height);
  }

  drawFlatGrid(grid: Grid, offsetX: number, offsetY: number) {
    for (let x = 0; x < grid.width; x++) {
      for (let y = 0; y < grid.height; y++) {
        const screenX = x * this.tileSize + offsetX;
        const screenY = y * this.tileSize + offsetY;

        const tile = grid.getTile(x, y);
        this.ctx.fillStyle = this.getTileColor(tile);
        this.ctx.fillRect(screenX, screenY, this.tileSize, this.tileSize);
        this.ctx.strokeStyle = '#333';
        this.ctx.strokeRect(screenX, screenY, this.tileSize, this.tileSize);
      }
    }
  }

  private getTileColor(tile: TileType | null): string {
    switch (tile) {
      case 'grass': return '#2d5a27';
      case 'water': return '#1a4a8a';
      case 'road': return '#555';
      default: return '#111';
    }
  }
}
```

## Frame Rate Display

Useful during development:

```typescript
let fps = 0;
let frameCount = 0;
let fpsTimer = 0;

function update(dt: number) {
  frameCount++;
  fpsTimer += dt;
  if (fpsTimer >= 1) {
    fps = frameCount;
    frameCount = 0;
    fpsTimer = 0;
  }
}

function render() {
  // ... draw grid ...

  // FPS counter
  ctx.fillStyle = '#fff';
  ctx.font = '14px monospace';
  ctx.fillText(`FPS: ${fps}`, 10, 20);
}
```

## Riku's Reaction

Riku looks at the flat grid: "That's... squares. I drew diamonds. Isometric diamonds."

You: "I know. The flat grid proves the data structure and game loop work. Tomorrow I rotate it."

Riku: "Rotate it?"

You: "Not literally. I transform the coordinates. Every (x, y) in the grid maps to a different screen position that makes it look 3D. The data stays flat — only the rendering changes."

## What You Built

- **Canvas setup** — full-window canvas with resize handling
- **Game loop** — `requestAnimationFrame` with delta time
- **Grid data structure** — 2D array of tile types
- **Flat renderer** — draws squares in a grid
- **Separation** — Grid (data) vs Renderer (display) vs main (loop)

The grid is flat. The data is ready. Next: the two functions that make it look isometric.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Isometric Projection →](chapter-02-isometric-projection.md)
