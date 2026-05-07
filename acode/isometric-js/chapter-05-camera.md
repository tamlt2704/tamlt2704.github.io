# Chapter 5: Camera

[← Chapter 4: Mouse Picking](chapter-04-mouse-picking.md) | [Chapter 6: Depth Sorting →](chapter-06-depth-sorting.md)

---

## The Task

The map is 50×50 now. It doesn't fit on screen. Riku wants to scroll around — WASD keys, edge-of-screen panning, and middle-mouse drag. "Like every RTS ever made."

The camera is just an offset. But it touches everything: rendering, picking, and eventually zoom.

## Camera as an Offset

A camera doesn't move the world — it moves the viewport. In 2D, that's just subtracting an offset from every draw call:

```typescript
// src/engine/camera.ts
export class Camera {
  x = 0;  // World position of the camera (top-left of viewport)
  y = 0;
  speed = 400; // Pixels per second

  // Convert world position to screen position
  worldToScreen(worldX: number, worldY: number) {
    return {
      screenX: worldX - this.x,
      screenY: worldY - this.y,
    };
  }

  // Convert screen position to world position
  screenToWorld(screenX: number, screenY: number) {
    return {
      worldX: screenX + this.x,
      worldY: screenY + this.y,
    };
  }
}
```

When the camera moves right, everything on screen moves left. That's the subtraction.

## World Coords vs Screen Coords

Before the camera, world and screen were the same. Now they diverge:

```
┌─────────────────────────────────────────────────────────────┐
│                         WORLD                                │
│                                                              │
│         ┌──────────────────────┐                            │
│         │      SCREEN          │                            │
│         │   (what you see)     │                            │
│         │                      │  camera.x, camera.y        │
│         │                      │  = top-left of this box    │
│         └──────────────────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Every rendering call now uses the camera:

```typescript
function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // The grid offset centers tile (0,0) — this is a world-space offset
  const worldOffsetX = canvas.width / 2;
  const worldOffsetY = 100;

  for (let x = 0; x < grid.width; x++) {
    for (let y = 0; y < grid.height; y++) {
      const { screenX, screenY } = cartToIso(x, y);

      // World position
      const worldX = screenX + worldOffsetX;
      const worldY = screenY + worldOffsetY;

      // Apply camera to get screen position
      const drawX = worldX - camera.x - TILE_W / 2;
      const drawY = worldY - camera.y - TILE_H / 2;

      const sprite = sprites.get(grid.getTile(x, y)!);
      if (sprite) {
        ctx.drawImage(sprite, drawX, drawY, TILE_W, TILE_H);
      }
    }
  }
}
```

Or more cleanly, use `ctx.translate`:

```typescript
function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  // Now draw everything in world coordinates — no manual subtraction
  drawGrid(grid, sprites, worldOffsetX, worldOffsetY);
  drawHighlight(input.hoveredTile, worldOffsetX, worldOffsetY);

  ctx.restore();

  // HUD elements draw without camera transform (screen space)
  drawFPS();
  drawMinimap();
}
```

`ctx.translate` is cleaner — you don't pass the camera to every draw function.

## Keyboard Panning (WASD)

Track which keys are held:

```typescript
// src/engine/input.ts
export class InputManager {
  keys: Set<string> = new Set();

  constructor(canvas: HTMLCanvasElement) {
    window.addEventListener('keydown', (e) => {
      this.keys.add(e.key.toLowerCase());
    });

    window.addEventListener('keyup', (e) => {
      this.keys.delete(e.key.toLowerCase());
    });
  }

  isKeyDown(key: string): boolean {
    return this.keys.has(key);
  }
}
```

Update the camera each frame:

```typescript
function update(dt: number) {
  // WASD panning
  if (input.isKeyDown('w') || input.isKeyDown('arrowup')) {
    camera.y -= camera.speed * dt;
  }
  if (input.isKeyDown('s') || input.isKeyDown('arrowdown')) {
    camera.y += camera.speed * dt;
  }
  if (input.isKeyDown('a') || input.isKeyDown('arrowleft')) {
    camera.x -= camera.speed * dt;
  }
  if (input.isKeyDown('d') || input.isKeyDown('arrowright')) {
    camera.x += camera.speed * dt;
  }
}
```

Multiply by `dt` (delta time in seconds) so movement is frame-rate independent. 400 pixels/second feels right for a city builder.

## Edge-of-Screen Panning

Move the camera when the mouse is near the edge — classic RTS behavior:

```typescript
const EDGE_THRESHOLD = 40; // pixels from edge
const EDGE_SPEED = 300;    // pixels per second

function updateEdgePan(dt: number) {
  const { mouseX, mouseY } = input;

  if (mouseX < EDGE_THRESHOLD) {
    camera.x -= EDGE_SPEED * dt;
  } else if (mouseX > canvas.width - EDGE_THRESHOLD) {
    camera.x += EDGE_SPEED * dt;
  }

  if (mouseY < EDGE_THRESHOLD) {
    camera.y -= EDGE_SPEED * dt;
  } else if (mouseY > canvas.height - EDGE_THRESHOLD) {
    camera.y += EDGE_SPEED * dt;
  }
}
```

Add it to the update loop:

```typescript
function update(dt: number) {
  updateKeyboardPan(dt);
  updateEdgePan(dt);
}
```

## Middle-Mouse Drag to Pan

The most satisfying pan method — grab the world and drag it:

```typescript
// src/engine/input.ts (additions)
export class InputManager {
  private isDragging = false;
  private dragStartX = 0;
  private dragStartY = 0;
  private cameraStartX = 0;
  private cameraStartY = 0;

  setupDragPan(canvas: HTMLCanvasElement, camera: Camera) {
    canvas.addEventListener('mousedown', (e) => {
      // Middle mouse button (button 1)
      if (e.button === 1) {
        e.preventDefault();
        this.isDragging = true;
        this.dragStartX = e.clientX;
        this.dragStartY = e.clientY;
        this.cameraStartX = camera.x;
        this.cameraStartY = camera.y;
        canvas.style.cursor = 'grabbing';
      }
    });

    canvas.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const dx = e.clientX - this.dragStartX;
        const dy = e.clientY - this.dragStartY;
        camera.x = this.cameraStartX - dx;
        camera.y = this.cameraStartY - dy;
      }
    });

    window.addEventListener('mouseup', (e) => {
      if (e.button === 1) {
        this.isDragging = false;
        canvas.style.cursor = 'default';
      }
    });

    // Prevent context menu on middle click
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  }
}
```

Note: `camera.x = cameraStartX - dx` — dragging right moves the camera left (the world moves right under your cursor). This feels natural.

## Camera Bounds

Don't let the player scroll into the void:

```typescript
// src/engine/camera.ts
export class Camera {
  x = 0;
  y = 0;
  speed = 400;

  // World bounds
  minX = -200;
  minY = -200;
  maxX = 2000;
  maxY = 2000;

  clamp() {
    this.x = Math.max(this.minX, Math.min(this.maxX, this.x));
    this.y = Math.max(this.minY, Math.min(this.maxY, this.y));
  }

  setBounds(gridWidth: number, gridHeight: number, tileW: number, tileH: number) {
    // Calculate world bounds from grid size
    const worldWidth = (gridWidth + gridHeight) * (tileW / 2);
    const worldHeight = (gridWidth + gridHeight) * (tileH / 2);

    this.minX = -200;
    this.minY = -200;
    this.maxX = worldWidth + 200;
    this.maxY = worldHeight + 200;
  }
}
```

Call `camera.clamp()` after every position update:

```typescript
function update(dt: number) {
  updateKeyboardPan(dt);
  updateEdgePan(dt);
  camera.clamp();
}
```

## Updating Mouse Picking for Camera

Here's the critical part. The mouse position is in **screen space**. The grid is in **world space**. With a camera, you must convert:

```typescript
function getHoveredTile(mouseX: number, mouseY: number): { x: number; y: number } {
  // Screen → World (add camera offset)
  const worldMouseX = mouseX + camera.x;
  const worldMouseY = mouseY + camera.y;

  // World → Grid (subtract the grid's world offset, then inverse transform)
  const relX = worldMouseX - worldOffsetX;
  const relY = worldMouseY - worldOffsetY;

  return isoToCart(relX, relY);
}
```

Before the camera, `screenX === worldX`. Now they differ by `camera.x` and `camera.y`. If you forget this conversion, clicking highlights the wrong tile — offset by however far you've scrolled.

## The Full Camera Class

```typescript
// src/engine/camera.ts
export class Camera {
  x = 0;
  y = 0;
  speed = 400;
  private minX = -Infinity;
  private minY = -Infinity;
  private maxX = Infinity;
  private maxY = Infinity;

  worldToScreen(worldX: number, worldY: number) {
    return {
      screenX: worldX - this.x,
      screenY: worldY - this.y,
    };
  }

  screenToWorld(screenX: number, screenY: number) {
    return {
      worldX: screenX + this.x,
      worldY: screenY + this.y,
    };
  }

  pan(dx: number, dy: number) {
    this.x += dx;
    this.y += dy;
    this.clamp();
  }

  centerOn(worldX: number, worldY: number, viewportW: number, viewportH: number) {
    this.x = worldX - viewportW / 2;
    this.y = worldY - viewportH / 2;
    this.clamp();
  }

  setBounds(minX: number, minY: number, maxX: number, maxY: number) {
    this.minX = minX;
    this.minY = minY;
    this.maxX = maxX;
    this.maxY = maxY;
    this.clamp();
  }

  private clamp() {
    this.x = Math.max(this.minX, Math.min(this.maxX, this.x));
    this.y = Math.max(this.minY, Math.min(this.maxY, this.y));
  }
}
```

## Smooth Camera (Optional)

Instead of snapping, lerp toward the target:

```typescript
// In update():
const targetX = /* desired camera position */;
const targetY = /* desired camera position */;
const smoothing = 0.1; // 0 = no movement, 1 = instant snap

camera.x += (targetX - camera.x) * smoothing;
camera.y += (targetY - camera.y) * smoothing;
```

This gives a floaty, cinematic feel. Good for cutscenes, less good for precise building placement. Make it toggleable.

## Putting It All Together

```typescript
// src/main.ts
import { Camera } from './engine/camera';
import { InputManager } from './engine/input';
import { Grid } from './engine/grid';

const camera = new Camera();
const input = new InputManager(canvas);
input.setupDragPan(canvas, camera);

// Center camera on the middle of the grid at start
const centerIso = cartToIso(grid.width / 2, grid.height / 2);
camera.centerOn(
  centerIso.screenX + worldOffsetX,
  centerIso.screenY + worldOffsetY,
  canvas.width,
  canvas.height
);

function update(dt: number) {
  // Keyboard pan
  if (input.isKeyDown('w')) camera.pan(0, -camera.speed * dt);
  if (input.isKeyDown('s')) camera.pan(0, camera.speed * dt);
  if (input.isKeyDown('a')) camera.pan(-camera.speed * dt, 0);
  if (input.isKeyDown('d')) camera.pan(camera.speed * dt, 0);

  // Update hovered tile (with camera)
  const { worldX, worldY } = camera.screenToWorld(input.mouseX, input.mouseY);
  const relX = worldX - worldOffsetX;
  const relY = worldY - worldOffsetY;
  const tile = isoToCart(relX, relY);

  input.hoveredTile = isValidTile(tile.x, tile.y, grid) ? tile : null;
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  renderer.drawGrid(grid, sprites, worldOffsetX, worldOffsetY);

  if (input.hoveredTile) {
    drawHighlight(ctx, input.hoveredTile.x, input.hoveredTile.y, worldOffsetX, worldOffsetY);
  }

  ctx.restore();

  // HUD (screen space)
  ctx.fillStyle = '#fff';
  ctx.font = '12px monospace';
  ctx.fillText(`Camera: (${Math.round(camera.x)}, ${Math.round(camera.y)})`, 10, 20);
  if (input.hoveredTile) {
    ctx.fillText(`Tile: (${input.hoveredTile.x}, ${input.hoveredTile.y})`, 10, 36);
  }
}
```

## Riku's Reaction

Riku scrolls around the 50×50 map. WASD, edge pan, middle-click drag. The tile highlight follows the mouse perfectly even while scrolling.

Riku: "This feels like a real game now. But look —" He places a tall building. Then places another one behind it. The one behind renders *on top* of the one in front.

You: "Depth sorting. We're drawing in grid order, not visual order."

Riku: "Fix it."

## What You Built

- **Camera class** — world offset with pan, bounds, and coordinate conversion
- **WASD panning** — frame-rate independent keyboard movement
- **Edge-of-screen panning** — RTS-style auto-scroll near edges
- **Middle-mouse drag** — grab-and-move with natural direction
- **Camera bounds** — prevent scrolling into the void
- **Updated picking** — screen → world → grid with camera offset
- **ctx.translate** — clean separation of world-space and screen-space drawing

The world scrolls. Picking still works. But objects render in the wrong order. Next: the painter's algorithm and depth sorting.

---

[← Chapter 4: Mouse Picking](chapter-04-mouse-picking.md) | [Chapter 6: Depth Sorting →](chapter-06-depth-sorting.md)
