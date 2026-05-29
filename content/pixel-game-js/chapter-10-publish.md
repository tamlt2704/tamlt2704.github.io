# Publishing

[prev: Polish](./chapter-09-polish.md) | [next: Overview](./chapter-00-overview.md)

Your game is done — now ship it. This chapter covers bundling, deploying to itch.io, mobile controls, PWA offline support, and performance optimization.

## Bundling with Vite

```bash
npm create vite@latest my-game -- --template vanilla-ts
cd my-game
npm install
```

`vite.config.ts`:

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  base: "./", // relative paths for itch.io
  build: {
    assetsInlineLimit: 0, // don't inline assets
    outDir: "dist",
  },
});
```

```bash
npm run build
# Output in dist/ — ready to deploy
```

## Deploying to itch.io

1. Run `npm run build`
2. Zip the `dist/` folder
3. Go to itch.io > Dashboard > Create new project
4. Set "Kind of project" to HTML
5. Upload the zip
6. Check "This file will be played in the browser"
7. Set viewport dimensions (e.g., 640x576 for 4x scale)

```
dist/
  index.html
  assets/
    player.png
    tileset.png
    index-abc123.js
```

## Embedding in a Website

```html
<iframe
  src="https://yourusername.itch.io/your-game"
  width="640"
  height="576"
  frameborder="0"
  allowfullscreen
>
</iframe>
```

Or self-host the dist folder:

```html
<iframe src="/games/my-game/index.html" width="640" height="576"></iframe>
```

## Mobile Controls (Virtual Joystick)

```typescript
class VirtualJoystick {
  active = false;
  baseX = 0;
  baseY = 0;
  stickX = 0;
  stickY = 0;
  dx = 0;
  dy = 0;
  radius = 20;

  constructor(private canvas: HTMLCanvasElement) {
    canvas.addEventListener("touchstart", (e) => this.onStart(e));
    canvas.addEventListener("touchmove", (e) => this.onMove(e));
    canvas.addEventListener("touchend", () => this.onEnd());
  }

  private getPos(e: TouchEvent) {
    const rect = this.canvas.getBoundingClientRect();
    const touch = e.touches[0];
    return {
      x: (touch.clientX - rect.left) * (this.canvas.width / rect.width),
      y: (touch.clientY - rect.top) * (this.canvas.height / rect.height),
    };
  }

  onStart(e: TouchEvent) {
    e.preventDefault();
    const p = this.getPos(e);
    this.active = true;
    this.baseX = p.x;
    this.baseY = p.y;
    this.stickX = p.x;
    this.stickY = p.y;
    this.dx = 0;
    this.dy = 0;
  }

  onMove(e: TouchEvent) {
    if (!this.active) return;
    e.preventDefault();
    const p = this.getPos(e);
    let ox = p.x - this.baseX;
    let oy = p.y - this.baseY;
    const dist = Math.hypot(ox, oy);
    if (dist > this.radius) {
      ox = (ox / dist) * this.radius;
      oy = (oy / dist) * this.radius;
    }
    this.stickX = this.baseX + ox;
    this.stickY = this.baseY + oy;
    this.dx = ox / this.radius; // -1 to 1
    this.dy = oy / this.radius;
  }

  onEnd() {
    this.active = false;
    this.dx = 0;
    this.dy = 0;
  }

  render(ctx: CanvasRenderingContext2D) {
    if (!this.active) return;
    ctx.globalAlpha = 0.3;
    ctx.beginPath();
    ctx.arc(this.baseX, this.baseY, this.radius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(this.stickX, this.stickY, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}

// Usage in update:
const joystick = new VirtualJoystick(canvas);
function update(dt: number) {
  player.vx = joystick.dx * player.speed;
  player.vy = joystick.dy * player.speed;
}
```

## PWA for Offline Play

`manifest.json`:

```json
{
  "name": "My Pixel Game",
  "short_name": "PixelGame",
  "start_url": "./index.html",
  "display": "fullscreen",
  "orientation": "landscape",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "icons": [{ "src": "icon-192.png", "sizes": "192x192", "type": "image/png" }]
}
```

`sw.js` (service worker):

```javascript
const CACHE = "game-v1";
const ASSETS = ["./index.html", "./assets/index.js", "./assets/player.png", "./assets/tileset.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
});

self.addEventListener("fetch", (e) => {
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
```

Register in `index.html`:

```html
<link rel="manifest" href="manifest.json" />
<script>
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
</script>
```

## Performance Tips

### Object Pooling

Avoid garbage collection spikes by reusing objects:

```typescript
class Pool<T> {
  private items: T[] = [];
  private active: T[] = [];

  constructor(
    private create: () => T,
    private reset: (item: T) => void,
    size: number,
  ) {
    for (let i = 0; i < size; i++) this.items.push(create());
  }

  get(): T | undefined {
    const item = this.items.pop();
    if (item) this.active.push(item);
    return item;
  }

  release(item: T) {
    const idx = this.active.indexOf(item);
    if (idx !== -1) {
      this.active.splice(idx, 1);
      this.reset(item);
      this.items.push(item);
    }
  }

  getActive(): T[] {
    return this.active;
  }
}

// Particle pool
const particlePool = new Pool<Particle>(
  () => ({ x: 0, y: 0, vx: 0, vy: 0, life: 0, maxLife: 0, color: "", size: 1 }),
  (p) => {
    p.life = 0;
  },
  200,
);
```

### Spatial Hashing

Fast collision detection for many objects:

```typescript
class SpatialHash {
  private cells = new Map<string, any[]>();
  private cellSize: number;

  constructor(cellSize: number) {
    this.cellSize = cellSize;
  }

  clear() {
    this.cells.clear();
  }

  private key(x: number, y: number): string {
    return `${Math.floor(x / this.cellSize)},${Math.floor(y / this.cellSize)}`;
  }

  insert(obj: { x: number; y: number; width: number; height: number }) {
    const x1 = Math.floor(obj.x / this.cellSize);
    const y1 = Math.floor(obj.y / this.cellSize);
    const x2 = Math.floor((obj.x + obj.width) / this.cellSize);
    const y2 = Math.floor((obj.y + obj.height) / this.cellSize);
    for (let x = x1; x <= x2; x++) {
      for (let y = y1; y <= y2; y++) {
        const k = `${x},${y}`;
        if (!this.cells.has(k)) this.cells.set(k, []);
        this.cells.get(k)!.push(obj);
      }
    }
  }

  query(obj: { x: number; y: number; width: number; height: number }): any[] {
    const results = new Set<any>();
    const x1 = Math.floor(obj.x / this.cellSize);
    const y1 = Math.floor(obj.y / this.cellSize);
    const x2 = Math.floor((obj.x + obj.width) / this.cellSize);
    const y2 = Math.floor((obj.y + obj.height) / this.cellSize);
    for (let x = x1; x <= x2; x++) {
      for (let y = y1; y <= y2; y++) {
        const cell = this.cells.get(`${x},${y}`);
        if (cell)
          cell.forEach((o) => {
            if (o !== obj) results.add(o);
          });
      }
    }
    return [...results];
  }
}

// Usage each frame:
const hash = new SpatialHash(32);
hash.clear();
entities.forEach((e) => hash.insert(e));
const nearby = hash.query(player);
// Only check collision with nearby entities
```

### Other Tips

- **Offscreen canvas**: Pre-render static backgrounds to a buffer canvas
- **Dirty rectangles**: Only redraw changed regions
- **Reduce draw calls**: Batch similar sprites
- **Avoid allocations in the loop**: Reuse vectors, arrays
- **Use `requestAnimationFrame`**: Never `setInterval` for rendering
- **Profile**: Use Chrome DevTools Performance tab to find bottlenecks

```typescript
// Offscreen buffer for static background
const bgCanvas = document.createElement("canvas");
bgCanvas.width = mapWidth;
bgCanvas.height = mapHeight;
const bgCtx = bgCanvas.getContext("2d")!;
// Draw map once to bgCanvas
renderMapTo(bgCtx);

// In game loop, just blit the buffer:
ctx.drawImage(bgCanvas, -camera.x, -camera.y);
```

## Checklist Before Publishing

- Test on multiple browsers (Chrome, Firefox, Safari)
- Test on mobile (touch controls work?)
- Assets load correctly with relative paths
- No console errors
- Game pauses when tab is hidden
- Audio starts on user interaction (browser policy)
- Performance is smooth (60fps on target hardware)
- Add a loading screen for large assets

[prev: Polish](./chapter-09-polish.md) | [next: Overview](./chapter-00-overview.md)
