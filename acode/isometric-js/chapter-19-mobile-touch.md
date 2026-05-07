# Chapter 19: Mobile Touch Controls

[← Chapter 18: Audio](chapter-18-audio.md) | [Chapter 20: Ship It →](chapter-20-ship-it.md)

---

## The Task

Riku opens TinyTown on his phone. Taps the screen — nothing happens. Tries to scroll — the whole page moves. Pinches — the browser zooms the page, not the game.

"Half the game jam judges will play this on mobile. We need touch controls."

Touch is a fundamentally different input model. No hover. No right-click. No scroll wheel. One or two fingers doing everything.

## Touch Events vs Mouse Events

Touch events fire differently than mouse events. A single tap fires: `touchstart` → `touchend` (no `mousemove` between). A drag fires: `touchstart` → `touchmove` (many) → `touchend`.

```typescript
// src/engine/touch-input.ts
export interface TouchState {
  touches: { id: number; x: number; y: number }[];
  pinchDistance: number | null;
  panStartX: number;
  panStartY: number;
  isPanning: boolean;
}

export class TouchInput {
  private state: TouchState = {
    touches: [],
    pinchDistance: null,
    panStartX: 0,
    panStartY: 0,
    isPanning: false,
  };

  private canvas: HTMLCanvasElement;
  private onTap: (x: number, y: number) => void;
  private onPan: (dx: number, dy: number) => void;
  private onPinch: (scale: number, centerX: number, centerY: number) => void;

  constructor(
    canvas: HTMLCanvasElement,
    handlers: {
      onTap: (x: number, y: number) => void;
      onPan: (dx: number, dy: number) => void;
      onPinch: (scale: number, centerX: number, centerY: number) => void;
    }
  ) {
    this.canvas = canvas;
    this.onTap = handlers.onTap;
    this.onPan = handlers.onPan;
    this.onPinch = handlers.onPinch;

    this.setupListeners();
  }

  private setupListeners() {
    this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
    this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
    this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: false });
  }

  private handleTouchStart(e: TouchEvent) {
    e.preventDefault();

    this.state.touches = this.getTouches(e);

    if (e.touches.length === 1) {
      // Single finger: start potential pan or tap
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      this.state.panStartX = touch.clientX - rect.left;
      this.state.panStartY = touch.clientY - rect.top;
      this.state.isPanning = false;
    } else if (e.touches.length === 2) {
      // Two fingers: start pinch
      this.state.pinchDistance = this.getPinchDistance(e.touches[0], e.touches[1]);
    }
  }

  private handleTouchMove(e: TouchEvent) {
    e.preventDefault();

    if (e.touches.length === 1) {
      // One finger pan
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const y = touch.clientY - rect.top;

      const dx = x - this.state.panStartX;
      const dy = y - this.state.panStartY;

      // Only start panning after a small threshold (to distinguish from tap)
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
        this.state.isPanning = true;
      }

      if (this.state.isPanning) {
        this.onPan(dx, dy);
        this.state.panStartX = x;
        this.state.panStartY = y;
      }
    } else if (e.touches.length === 2) {
      // Pinch to zoom
      const newDistance = this.getPinchDistance(e.touches[0], e.touches[1]);

      if (this.state.pinchDistance !== null) {
        const scale = newDistance / this.state.pinchDistance;
        const center = this.getPinchCenter(e.touches[0], e.touches[1]);
        this.onPinch(scale, center.x, center.y);
      }

      this.state.pinchDistance = newDistance;
    }
  }

  private handleTouchEnd(e: TouchEvent) {
    e.preventDefault();

    // If it was a single finger and didn't pan → it's a tap
    if (e.changedTouches.length === 1 && !this.state.isPanning && this.state.touches.length === 1) {
      const touch = e.changedTouches[0];
      const rect = this.canvas.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const y = touch.clientY - rect.top;
      this.onTap(x, y);
    }

    this.state.pinchDistance = null;
    this.state.isPanning = false;
    this.state.touches = this.getTouches(e);
  }

  private getPinchDistance(t1: Touch, t2: Touch): number {
    const dx = t1.clientX - t2.clientX;
    const dy = t1.clientY - t2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  private getPinchCenter(t1: Touch, t2: Touch): { x: number; y: number } {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: (t1.clientX + t2.clientX) / 2 - rect.left,
      y: (t1.clientY + t2.clientY) / 2 - rect.top,
    };
  }

  private getTouches(e: TouchEvent): { id: number; x: number; y: number }[] {
    const rect = this.canvas.getBoundingClientRect();
    return Array.from(e.touches).map(t => ({
      id: t.identifier,
      x: t.clientX - rect.left,
      y: t.clientY - rect.top,
    }));
  }
}
```

## Pinch-to-Zoom

Two fingers moving apart = zoom in. Moving together = zoom out. The zoom anchors at the midpoint between the fingers:

```typescript
// Wiring pinch to camera
const touchInput = new TouchInput(canvas, {
  onTap: (x, y) => {
    // Same as mouse click — pick tile, place building
    const { gridX, gridY } = screenToGrid(x, y, camera);
    handleTileClick(gridX, gridY);
  },

  onPan: (dx, dy) => {
    // Move camera (divide by zoom for consistent speed)
    camera.x -= dx / camera.zoom;
    camera.y -= dy / camera.zoom;
  },

  onPinch: (scale, centerX, centerY) => {
    // Zoom toward pinch center
    const oldZoom = camera.zoom;
    camera.zoom *= scale;
    camera.zoom = Math.max(camera.minZoom, Math.min(camera.maxZoom, camera.zoom));

    // Adjust camera to keep pinch center stable
    const worldX = centerX / oldZoom + camera.x;
    const worldY = centerY / oldZoom + camera.y;
    camera.x = worldX - centerX / camera.zoom;
    camera.y = worldY - centerY / camera.zoom;
  },
});
```

## Tap to Select/Place

On mobile, tap replaces click. But there's no hover preview. Show the build preview at the last tapped position:

```typescript
// src/game/mobile-build.ts
export class MobileBuildMode {
  private previewVisible = false;
  private previewGridX = 0;
  private previewGridY = 0;

  onTap(gridX: number, gridY: number, buildMode: BuildMode, grid: GameGrid) {
    if (buildMode.state !== BuildState.Previewing) {
      // Not in build mode — select/inspect the tile
      return;
    }

    if (this.previewVisible &&
        this.previewGridX === gridX &&
        this.previewGridY === gridY) {
      // Second tap on same tile → confirm placement
      buildMode.updatePreview(gridX, gridY, grid);
      if (buildMode.isValidPlacement) {
        buildMode.confirmPlacement(grid);
        this.previewVisible = false;
      }
    } else {
      // First tap → show preview at this position
      this.previewGridX = gridX;
      this.previewGridY = gridY;
      this.previewVisible = true;
      buildMode.updatePreview(gridX, gridY, grid);
    }
  }
}
```

## Preventing Default Browser Gestures

Without prevention, the browser will try to scroll, zoom the page, or trigger pull-to-refresh:

```typescript
// src/engine/prevent-gestures.ts
export function preventDefaultGestures(canvas: HTMLCanvasElement) {
  // Prevent page scroll when touching the canvas
  canvas.style.touchAction = 'none';

  // Prevent iOS bounce scroll
  document.body.style.overflow = 'hidden';
  document.body.style.position = 'fixed';
  document.body.style.width = '100%';
  document.body.style.height = '100%';

  // Prevent double-tap zoom
  canvas.addEventListener('dblclick', (e) => e.preventDefault());

  // Prevent context menu on long press
  canvas.addEventListener('contextmenu', (e) => e.preventDefault());

  // Prevent pinch-zoom on the page level
  document.addEventListener('gesturestart', (e) => e.preventDefault());
  document.addEventListener('gesturechange', (e) => e.preventDefault());
}
```

The most important line: `touch-action: none` on the canvas. This tells the browser "I'm handling all touch gestures myself."

## Responsive Canvas Sizing

The canvas needs to fill the screen on any device:

```typescript
// src/engine/responsive.ts
export function setupResponsiveCanvas(canvas: HTMLCanvasElement, app?: Application) {
  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const width = window.innerWidth;
    const height = window.innerHeight;

    // Set display size
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    // Set actual resolution (accounting for device pixel ratio)
    canvas.width = width * dpr;
    canvas.height = height * dpr;

    // Scale context for DPR (Canvas 2D)
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.scale(dpr, dpr);
    }

    // If using PixiJS, resize the renderer
    if (app) {
      app.renderer.resize(width, height);
    }
  }

  window.addEventListener('resize', resize);
  window.addEventListener('orientationchange', () => {
    // Delay to let the browser finish rotating
    setTimeout(resize, 100);
  });

  resize(); // Initial size
}
```

## Unified Input Handler

Support both mouse and touch with a single interface:

```typescript
// src/engine/unified-input.ts
export interface InputEvent {
  type: 'tap' | 'pan' | 'zoom';
  screenX: number;
  screenY: number;
  deltaX?: number;
  deltaY?: number;
  zoomScale?: number;
}

export class UnifiedInput {
  private handlers: ((event: InputEvent) => void)[] = [];
  private isTouchDevice: boolean;

  constructor(canvas: HTMLCanvasElement, camera: Camera) {
    this.isTouchDevice = 'ontouchstart' in window;

    if (this.isTouchDevice) {
      new TouchInput(canvas, {
        onTap: (x, y) => this.emit({ type: 'tap', screenX: x, screenY: y }),
        onPan: (dx, dy) => this.emit({ type: 'pan', screenX: 0, screenY: 0, deltaX: dx, deltaY: dy }),
        onPinch: (scale, cx, cy) => this.emit({ type: 'zoom', screenX: cx, screenY: cy, zoomScale: scale }),
      });
    } else {
      // Mouse handlers (existing code)
      setupMouseInput(canvas, camera, (event) => this.emit(event));
    }
  }

  on(handler: (event: InputEvent) => void) {
    this.handlers.push(handler);
  }

  private emit(event: InputEvent) {
    for (const handler of this.handlers) {
      handler(event);
    }
  }
}
```

## Mobile Build Menu

The bottom toolbar needs bigger touch targets on mobile:

```typescript
// src/ui/mobile-menu.ts
export function adaptMenuForMobile(buildMenu: HTMLElement) {
  if (!('ontouchstart' in window)) return;

  // Bigger buttons for fat fingers
  const buttons = buildMenu.querySelectorAll('button');
  for (const btn of buttons) {
    btn.style.width = '64px';
    btn.style.height = '64px';
    btn.style.minWidth = '44px';  // Apple's minimum touch target
    btn.style.minHeight = '44px';
  }

  // Add a cancel button (no right-click on mobile)
  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = '✕';
  cancelBtn.style.cssText = `
    width: 64px; height: 64px;
    border: 2px solid #f55;
    border-radius: 6px;
    background: #411;
    color: #f55;
    font-size: 24px;
    cursor: pointer;
  `;
  cancelBtn.addEventListener('click', () => {
    buildMode.cancel();
  });
  buildMenu.appendChild(cancelBtn);
}
```

## Riku's Reaction

Riku opens TinyTown on his phone. One-finger pan glides smoothly. Pinch zooms in and out. Tap a building in the menu, tap the map to preview, tap again to place. The cancel button is right there.

Riku: "It works! This is actually playable on mobile. We're almost done. When do we ship?"

You: "Tomorrow. Let's do the production build, optimize assets, and deploy to itch.io."

## What You Built

- **Touch event handling** — touchstart, touchmove, touchend with gesture detection
- **Pinch-to-zoom** — two-finger distance tracking with center anchor
- **One-finger pan** — drag threshold to distinguish from tap
- **Tap to place** — two-tap flow (preview → confirm) replaces hover
- **Gesture prevention** — `touch-action: none`, no page scroll or browser zoom
- **Responsive canvas** — fills screen, handles DPR and orientation changes
- **Unified input** — single interface for mouse and touch
- **Mobile-friendly UI** — larger touch targets, explicit cancel button

The game works everywhere. Next: shipping it.

---

[← Chapter 18: Audio](chapter-18-audio.md) | [Chapter 20: Ship It →](chapter-20-ship-it.md)
