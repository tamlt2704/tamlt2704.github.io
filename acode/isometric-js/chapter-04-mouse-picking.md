# Chapter 4: Mouse Picking

[← Chapter 3: Tile Sprites](chapter-03-tile-sprites.md) | [Chapter 5: Camera →](chapter-05-camera.md)

---

## The Task

Riku wants a build menu. Click a tile, see what's there. Click an empty tile, place a building. But first — you need to know *which* tile the mouse is over.

"Just use the inverse of that iso function, right?"

Almost. There's a subtle bug waiting.

## Mouse Events on Canvas

First, capture the mouse position relative to the canvas:

```typescript
// src/engine/input.ts
export class InputManager {
  mouseX = 0;
  mouseY = 0;
  mouseDown = false;
  hoveredTile: { x: number; y: number } | null = null;

  constructor(canvas: HTMLCanvasElement) {
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.mouseX = e.clientX - rect.left;
      this.mouseY = e.clientY - rect.top;
    });

    canvas.addEventListener('mousedown', () => {
      this.mouseDown = true;
    });

    canvas.addEventListener('mouseup', () => {
      this.mouseDown = false;
    });
  }
}
```

`getBoundingClientRect()` handles cases where the canvas isn't at (0,0) — toolbars, margins, scroll offsets. Always use it.

## Screen → World → Grid

The mouse gives you **screen coordinates**. You need **grid coordinates**. The pipeline:

```
Screen (640, 360)
    │
    ▼  subtract world offset
World (140, 260)
    │
    ▼  isoToCart()
Grid (3, 5)
```

Step 1: Remove the offset you added when rendering:

```typescript
function screenToWorld(screenX: number, screenY: number, offsetX: number, offsetY: number) {
  return {
    worldX: screenX - offsetX,
    worldY: screenY - offsetY,
  };
}
```

Step 2: Apply the inverse transform:

```typescript
function isoToCart(worldX: number, worldY: number): { x: number; y: number } {
  return {
    x: Math.floor((worldX / (TILE_W / 2) + worldY / (TILE_H / 2)) / 2),
    y: Math.floor((worldY / (TILE_H / 2) - worldX / (TILE_W / 2)) / 2),
  };
}
```

Combined:

```typescript
function getHoveredTile(
  mouseX: number,
  mouseY: number,
  offsetX: number,
  offsetY: number
): { x: number; y: number } {
  const worldX = mouseX - offsetX;
  const worldY = mouseY - offsetY;

  return isoToCart(worldX, worldY);
}
```

## The Off-by-One Problem

You wire it up. Move the mouse over the grid. The highlighted tile is... almost right. Sometimes it's one tile off. Especially near the edges of diamonds.

The problem: `Math.floor()` rounds toward negative infinity. For the isometric diamond shape, this creates a bias. The mouse can be inside one diamond but the floored coordinates point to an adjacent tile.

```
        ╱╲
       ╱  ╲
      ╱ A  ╲        ← Mouse is here, inside tile A
     ╱──────╲
    ╱╲  B   ╱╲      ← But floor() says tile B
   ╱  ╲    ╱  ╲
  ╱    ╲  ╱    ╲
   ╲    ╲╱    ╱
    ╲        ╱
     ╲      ╱
```

### The Fix: Fractional Coordinates

Instead of flooring immediately, compute the fractional position and check which half of the cell the point falls in:

```typescript
function isoToCart(worldX: number, worldY: number): { x: number; y: number } {
  // Get floating-point grid coordinates
  const rawX = (worldX / (TILE_W / 2) + worldY / (TILE_H / 2)) / 2;
  const rawY = (worldY / (TILE_H / 2) - worldX / (TILE_W / 2)) / 2;

  // Floor to get the tile
  return {
    x: Math.floor(rawX),
    y: Math.floor(rawY),
  };
}
```

This actually works correctly for the 2:1 diamond ratio. The real issue is usually the **offset**. If your offset doesn't match what you used during rendering, picking is off by a tile.

### The Real Fix: Match Your Rendering Offset

The most common "off-by-one" in isometric picking comes from inconsistent offsets:

```typescript
// WRONG: rendering uses center of diamond, picking uses top-left
// Rendering:
const drawX = screenX + offsetX - TILE_W / 2;
const drawY = screenY + offsetY - TILE_H / 2;

// Picking (must match!):
const worldX = mouseX - offsetX;
const worldY = mouseY - offsetY;
```

If rendering offsets the diamond center by `(-TILE_W/2, -TILE_H/2)` for drawImage, your picking needs to account for the same reference point. Since `cartToIso` returns the diamond center, and we subtract `TILE_W/2` and `TILE_H/2` only for the drawImage call, the picking offset stays as-is:

```typescript
// Correct: picking uses the same offset as the cartToIso output
function getHoveredTile(mouseX: number, mouseY: number): { x: number; y: number } {
  const worldX = mouseX - offsetX;
  const worldY = mouseY - offsetY;
  return isoToCart(worldX, worldY);
}
```

The `drawImage` offset is purely visual — it doesn't change the coordinate system.

## Highlighting the Hovered Tile

Draw a semi-transparent overlay on the tile under the mouse:

```typescript
function drawHighlight(
  ctx: CanvasRenderingContext2D,
  gridX: number,
  gridY: number,
  offsetX: number,
  offsetY: number
) {
  const { screenX, screenY } = cartToIso(gridX, gridY);
  const cx = screenX + offsetX;
  const cy = screenY + offsetY;

  ctx.beginPath();
  ctx.moveTo(cx, cy - TILE_H / 2);
  ctx.lineTo(cx + TILE_W / 2, cy);
  ctx.lineTo(cx, cy + TILE_H / 2);
  ctx.lineTo(cx - TILE_W / 2, cy);
  ctx.closePath();

  ctx.fillStyle = 'rgba(255, 255, 100, 0.3)';
  ctx.fill();
  ctx.strokeStyle = 'rgba(255, 255, 100, 0.8)';
  ctx.lineWidth = 2;
  ctx.stroke();
}
```

## Bounds Checking

Don't highlight tiles outside the grid:

```typescript
function isValidTile(x: number, y: number, grid: Grid): boolean {
  return x >= 0 && x < grid.width && y >= 0 && y < grid.height;
}

function update() {
  const tile = getHoveredTile(input.mouseX, input.mouseY);

  if (isValidTile(tile.x, tile.y, grid)) {
    input.hoveredTile = tile;
  } else {
    input.hoveredTile = null;
  }
}
```

## Click to Select

```typescript
// src/engine/input.ts
export class InputManager {
  mouseX = 0;
  mouseY = 0;
  hoveredTile: { x: number; y: number } | null = null;
  selectedTile: { x: number; y: number } | null = null;

  private clickHandlers: Array<(x: number, y: number) => void> = [];

  constructor(canvas: HTMLCanvasElement) {
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.mouseX = e.clientX - rect.left;
      this.mouseY = e.clientY - rect.top;
    });

    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      this.clickHandlers.forEach((fn) => fn(mx, my));
    });
  }

  onClick(handler: (screenX: number, screenY: number) => void) {
    this.clickHandlers.push(handler);
  }
}
```

Wire it up:

```typescript
input.onClick((screenX, screenY) => {
  const tile = getHoveredTile(screenX, screenY);
  if (isValidTile(tile.x, tile.y, grid)) {
    input.selectedTile = tile;
    console.log(`Selected tile: (${tile.x}, ${tile.y}) = ${grid.getTile(tile.x, tile.y)}`);
  }
});
```

## Drawing the Selection

Different style for selected vs hovered:

```typescript
function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw the grid
  renderer.drawGrid(grid, sprites, offsetX, offsetY);

  // Draw hover highlight
  if (input.hoveredTile) {
    drawHighlight(ctx, input.hoveredTile.x, input.hoveredTile.y, offsetX, offsetY);
  }

  // Draw selection (thicker border, different color)
  if (input.selectedTile) {
    const { screenX, screenY } = cartToIso(input.selectedTile.x, input.selectedTile.y);
    const cx = screenX + offsetX;
    const cy = screenY + offsetY;

    ctx.beginPath();
    ctx.moveTo(cx, cy - TILE_H / 2);
    ctx.lineTo(cx + TILE_W / 2, cy);
    ctx.lineTo(cx, cy + TILE_H / 2);
    ctx.lineTo(cx - TILE_W / 2, cy);
    ctx.closePath();

    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  requestAnimationFrame(render);
}
```

## Debug Overlay: Show Grid Coordinates

During development, draw the (x, y) on each tile:

```typescript
function drawDebugCoords(offsetX: number, offsetY: number) {
  ctx.font = '10px monospace';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
  ctx.textAlign = 'center';

  for (let x = 0; x < grid.width; x++) {
    for (let y = 0; y < grid.height; y++) {
      const { screenX, screenY } = cartToIso(x, y);
      ctx.fillText(
        `${x},${y}`,
        screenX + offsetX,
        screenY + offsetY + 4
      );
    }
  }
}
```

This is invaluable for debugging picking issues. If the highlighted tile doesn't match the coordinates shown, your offset is wrong.

## The Complete Picking System

```typescript
// src/engine/picking.ts
export class IsoPicker {
  private tileW: number;
  private tileH: number;

  constructor(tileW = 64, tileH = 32) {
    this.tileW = tileW;
    this.tileH = tileH;
  }

  screenToGrid(
    screenX: number,
    screenY: number,
    offsetX: number,
    offsetY: number
  ): { x: number; y: number } {
    const worldX = screenX - offsetX;
    const worldY = screenY - offsetY;

    const rawX = (worldX / (this.tileW / 2) + worldY / (this.tileH / 2)) / 2;
    const rawY = (worldY / (this.tileH / 2) - worldX / (this.tileW / 2)) / 2;

    return {
      x: Math.floor(rawX),
      y: Math.floor(rawY),
    };
  }

  isInBounds(x: number, y: number, gridW: number, gridH: number): boolean {
    return x >= 0 && x < gridW && y >= 0 && y < gridH;
  }
}
```

## Riku's Reaction

You show Riku the highlight following the mouse. He clicks a water tile — it outlines in green.

Riku: "Nice. But the map is only 10×10. I want 50×50. I can't see the whole thing."

You: "We need a camera. Scroll around the map."

Riku: "WASD? Or click-and-drag?"

You: "Both."

## What You Built

- **Mouse event handling** — position relative to canvas with `getBoundingClientRect`
- **Screen → World → Grid pipeline** — subtract offset, then inverse transform
- **isoToCart()** — the inverse of cartToIso, with proper floor behavior
- **The offset trap** — picking offset must match rendering offset exactly
- **Tile highlighting** — semi-transparent diamond overlay on hover
- **Click selection** — store and render the selected tile
- **Bounds checking** — ignore clicks outside the grid

Mouse picking works. But the map is stuck in place. Next: a camera that lets you scroll around a larger world.

---

[← Chapter 3: Tile Sprites](chapter-03-tile-sprites.md) | [Chapter 5: Camera →](chapter-05-camera.md)
