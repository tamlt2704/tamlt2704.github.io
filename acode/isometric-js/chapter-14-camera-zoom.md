# Chapter 14: Camera & Zoom

[← Chapter 13: Pathfinding](chapter-13-pathfinding.md) | [Chapter 15: Lighting →](chapter-15-lighting.md)

---

## The Task

Riku zooms in on the browser (Ctrl+Plus). The pixels get bigger but the game doesn't respond — the mouse picking breaks, the viewport doesn't adjust. "I need real zoom. Scroll wheel to zoom in and out. And it should zoom toward where my mouse is, not the corner."

Zoom-toward-mouse is the interaction every map app gets right. Getting it right in an isometric game means understanding scale transforms and anchor points.

## Scale Transform Basics

Zooming is a scale applied to the world container. Everything in the world gets bigger or smaller, but the screen stays the same size:

```typescript
// src/engine/camera.ts
const TILE_W = 64;
const TILE_H = 32;

export class Camera {
  x = 0;       // World-space offset
  y = 0;
  zoom = 1;    // 1 = normal, 2 = zoomed in 2x, 0.5 = zoomed out
  minZoom = 0.25;
  maxZoom = 3;

  private targetZoom = 1;
  private zoomSpeed = 0.1;

  screenToWorld(screenX: number, screenY: number): { wx: number; wy: number } {
    // Convert screen coordinates to world coordinates accounting for zoom
    const wx = screenX / this.zoom + this.x;
    const wy = screenY / this.zoom + this.y;
    return { wx, wy };
  }

  worldToScreen(worldX: number, worldY: number): { sx: number; sy: number } {
    const sx = (worldX - this.x) * this.zoom;
    const sy = (worldY - this.y) * this.zoom;
    return { sx, sy };
  }
}
```

## Zoom Toward Mouse Position

The key insight: when you zoom in, the point under the mouse should stay under the mouse. This means adjusting the camera position as zoom changes.

```typescript
// src/engine/camera.ts (continued)
export class Camera {
  // ... previous code ...

  zoomAt(screenX: number, screenY: number, delta: number) {
    const oldZoom = this.zoom;

    // Calculate new zoom level
    this.zoom *= 1 - delta * this.zoomSpeed;
    this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom));

    if (this.zoom === oldZoom) return; // Hit bounds, no change

    // The world point under the mouse before zoom
    const worldX = screenX / oldZoom + this.x;
    const worldY = screenY / oldZoom + this.y;

    // After zoom, that same world point should still be at screenX, screenY
    // screenX = (worldX - newCameraX) * newZoom
    // newCameraX = worldX - screenX / newZoom
    this.x = worldX - screenX / this.zoom;
    this.y = worldY - screenY / this.zoom;
  }

  smoothZoomAt(screenX: number, screenY: number, delta: number) {
    // Same math but with lerp for smooth animation
    const oldZoom = this.zoom;
    this.targetZoom *= 1 - delta * this.zoomSpeed;
    this.targetZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.targetZoom));

    // Store mouse position for interpolation
    this.zoomAnchorX = screenX;
    this.zoomAnchorY = screenY;
  }

  private zoomAnchorX = 0;
  private zoomAnchorY = 0;

  update(dt: number) {
    if (Math.abs(this.zoom - this.targetZoom) > 0.001) {
      const oldZoom = this.zoom;
      this.zoom += (this.targetZoom - this.zoom) * Math.min(1, dt * 12);

      // Adjust position to keep anchor point stable
      const worldX = this.zoomAnchorX / oldZoom + this.x;
      const worldY = this.zoomAnchorY / oldZoom + this.y;
      this.x = worldX - this.zoomAnchorX / this.zoom;
      this.y = worldY - this.zoomAnchorY / this.zoom;
    }
  }
}
```

## Scroll Wheel Handling

```typescript
// src/engine/input.ts
export function setupZoomInput(canvas: HTMLCanvasElement, camera: Camera) {
  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Normalize wheel delta across browsers
    const delta = Math.sign(e.deltaY) * 0.15;

    camera.zoomAt(mouseX, mouseY, delta);
  }, { passive: false });
}
```

## Applying Zoom to the Renderer

With PixiJS, zoom is a scale on the world container:

```typescript
// src/engine/iso-stage.ts (updated)
export class IsoStage {
  readonly world: Container;

  applyCamera(camera: Camera) {
    this.world.scale.set(camera.zoom);
    this.world.x = -camera.x * camera.zoom;
    this.world.y = -camera.y * camera.zoom;
  }
}

// In game loop:
function render() {
  isoStage.applyCamera(camera);
  // PixiJS handles the rest
}
```

With raw Canvas 2D (fallback):

```typescript
function render() {
  ctx.save();
  ctx.scale(camera.zoom, camera.zoom);
  ctx.translate(-camera.x, -camera.y);

  // Draw world...
  renderTerrain();
  renderBuildings();
  renderNPCs();

  ctx.restore();

  // Draw HUD (not affected by zoom)
  renderHUD();
}
```

## Updating Mouse Picking for Zoom

The mouse picking from Chapter 4 assumed zoom = 1. Now every screen-to-world conversion must account for zoom:

```typescript
// src/game/picking.ts (updated)
export function screenToGrid(
  screenX: number,
  screenY: number,
  camera: Camera
): { gridX: number; gridY: number } {
  // Convert screen → world (accounting for zoom and pan)
  const { wx, wy } = camera.screenToWorld(screenX, screenY);

  // World → iso grid (same math as before, but on world coords)
  const isoX = wx - worldOffsetX;
  const isoY = wy - worldOffsetY;

  const gridX = Math.floor((isoX / (TILE_W / 2) + isoY / (TILE_H / 2)) / 2);
  const gridY = Math.floor((isoY / (TILE_H / 2) - isoX / (TILE_W / 2)) / 2);

  return { gridX, gridY };
}
```

Update all mouse handlers to use this:

```typescript
canvas.addEventListener('mousemove', (e) => {
  const rect = canvas.getBoundingClientRect();
  const screenX = e.clientX - rect.left;
  const screenY = e.clientY - rect.top;

  // This now works at any zoom level
  const { gridX, gridY } = screenToGrid(screenX, screenY, camera);
  buildMode.updatePreview(gridX, gridY, grid);
});
```

## Pan + Zoom Together

Middle-mouse drag to pan, scroll wheel to zoom. They need to work together:

```typescript
// src/engine/camera-controller.ts
export class CameraController {
  private isPanning = false;
  private lastMouseX = 0;
  private lastMouseY = 0;

  constructor(private camera: Camera, private canvas: HTMLCanvasElement) {
    this.setupListeners();
  }

  private setupListeners() {
    this.canvas.addEventListener('mousedown', (e) => {
      if (e.button === 1) { // Middle mouse
        this.isPanning = true;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
        e.preventDefault();
      }
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (!this.isPanning) return;

      const dx = e.clientX - this.lastMouseX;
      const dy = e.clientY - this.lastMouseY;

      // Pan in world space (divide by zoom so pan speed feels consistent)
      this.camera.x -= dx / this.camera.zoom;
      this.camera.y -= dy / this.camera.zoom;

      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mouseup', (e) => {
      if (e.button === 1) {
        this.isPanning = false;
      }
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const delta = Math.sign(e.deltaY) * 0.15;
      this.camera.zoomAt(mouseX, mouseY, delta);
    }, { passive: false });
  }
}
```

## Zoom Level Indicator

Show the player what zoom level they're at:

```typescript
// src/ui/zoom-indicator.ts
export function renderZoomIndicator(ctx: CanvasRenderingContext2D, camera: Camera) {
  const percent = Math.round(camera.zoom * 100);
  const text = `${percent}%`;

  ctx.save();
  ctx.font = '14px monospace';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
  ctx.textAlign = 'right';
  ctx.fillText(text, ctx.canvas.width - 12, ctx.canvas.height - 12);
  ctx.restore();
}
```

## Clamping Camera Bounds

Don't let the player pan infinitely into the void:

```typescript
// src/engine/camera.ts (addition)
export class Camera {
  // ... previous code ...

  clampToWorld(worldWidth: number, worldHeight: number, screenW: number, screenH: number) {
    const visibleW = screenW / this.zoom;
    const visibleH = screenH / this.zoom;

    // Don't let camera go past world edges
    const maxX = worldWidth - visibleW;
    const maxY = worldHeight - visibleH;

    this.x = Math.max(0, Math.min(maxX, this.x));
    this.y = Math.max(0, Math.min(maxY, this.y));
  }
}
```

## Riku's Reaction

Scroll wheel zooms in smoothly, centered on the cursor. Middle-drag pans. The whole city is explorable at any scale.

Riku: "Now zoom in at night. I want the buildings to glow. Day/night cycle, rain, atmosphere."

You: "Lighting and weather. Tint overlays, point lights, particles. Let's make TinyTown moody."

## What You Built

- **Zoom-toward-mouse** — anchor point math keeps the cursor position stable
- **Smooth zoom** — lerp toward target zoom for fluid feel
- **Scale transform** — applied to PixiJS container or Canvas context
- **Updated mouse picking** — screen-to-world conversion accounts for zoom
- **Pan + zoom** — middle-drag pan with zoom-adjusted speed
- **Camera bounds** — clamp to prevent panning into void
- **Zoom indicator** — show current zoom percentage

The player can explore the city at any scale. Next: making it beautiful with lighting.

---

[← Chapter 13: Pathfinding](chapter-13-pathfinding.md) | [Chapter 15: Lighting →](chapter-15-lighting.md)
