# Chapter 20: Ship It

[← Chapter 19: Mobile Touch](chapter-19-mobile-touch.md)

---

## The Task

It's game jam submission day. The game works locally. Riku's art is in. Sound effects play. Touch controls work. But "works on my machine" isn't a submission.

You need: a production build, optimized assets, and a URL the judges can click.

## Production Build with Vite

Vite's production build bundles, minifies, and tree-shakes your code:

```bash
npm run build
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',  // Relative paths (important for itch.io)
  build: {
    outDir: 'dist',
    assetsInlineLimit: 4096,  // Inline small assets as base64
    rollupOptions: {
      output: {
        manualChunks: {
          pixi: ['pixi.js'],  // Separate chunk for PixiJS
        },
      },
    },
  },
});
```

The `base: './'` is critical. itch.io serves your game from a subdirectory — absolute paths (`/assets/...`) won't work.

## Asset Optimization

### Texture Packing

Instead of 30 individual PNG files, pack all sprites into one atlas:

```bash
# Using free-tex-packer-cli
npx free-tex-packer-cli --input ./assets/sprites --output ./public/assets/atlas
```

This produces:
- `atlas.png` — one image with all sprites packed tightly
- `atlas.json` — coordinates of each sprite in the atlas

```typescript
// Loading the packed atlas
import { Assets, Spritesheet } from 'pixi.js';

async function loadAtlas() {
  const sheet = await Assets.load('/assets/atlas/atlas.json');
  // All textures available: sheet.textures['house.png'], sheet.textures['tree.png'], etc.
  return sheet;
}
```

One texture = one draw call for the entire game. Maximum batching.

### Image Compression

PNGs from Aseprite are uncompressed. Optimize them:

```bash
# Lossless PNG optimization
npx imagemin-cli ./public/assets/**/*.png --out-dir=./public/assets --plugin=pngquant

# Or use oxipng for better compression
npx oxipng -o 4 ./public/assets/**/*.png
```

### Audio Compression

WAV files are huge. Convert to OGG Vorbis (smaller, widely supported):

```bash
# Convert WAV to OGG (requires ffmpeg)
ffmpeg -i place.wav -c:a libvorbis -q:a 4 place.ogg
ffmpeg -i music.wav -c:a libvorbis -q:a 3 music.ogg
```

Provide both OGG and MP3 for maximum browser compatibility:

```typescript
// src/engine/audio.ts (updated)
async loadSound(name: string, basePath: string) {
  const formats = ['ogg', 'mp3'];
  for (const fmt of formats) {
    try {
      const response = await fetch(`${basePath}.${fmt}`);
      if (response.ok) {
        const buffer = await response.arrayBuffer();
        const audioBuffer = await this.ctx!.decodeAudioData(buffer);
        this.buffers.set(name, audioBuffer);
        return;
      }
    } catch { /* try next format */ }
  }
  console.warn(`Could not load audio: ${name}`);
}
```

## Bundle Size Analysis

See what's taking up space:

```bash
npx vite-bundle-visualizer
```

Typical breakdown for TinyTown:

```
dist/
├── index.html              0.5 KB
├── assets/
│   ├── index-[hash].js    45 KB  (game code, minified)
│   ├── pixi-[hash].js    180 KB  (PixiJS, separate chunk)
│   ├── atlas.png          120 KB  (all sprites, packed)
│   ├── atlas.json           3 KB  (sprite coordinates)
│   ├── sfx-sprite.ogg      35 KB  (all sound effects)
│   └── music.ogg          800 KB  (background music)
└── Total:                ~1.2 MB
```

Under 2 MB is excellent for a browser game. The judges won't wait for a 50 MB download.

### Reducing PixiJS Bundle Size

PixiJS is modular. Import only what you use:

```typescript
// BEFORE: imports everything (500KB+)
import * as PIXI from 'pixi.js';

// AFTER: import only needed modules
import { Application, Sprite, Container, Texture, Assets } from 'pixi.js';
```

Vite's tree-shaking removes unused PixiJS modules automatically when you use named imports.

## Deploying to itch.io

itch.io hosts HTML5 games for free. The process:

1. **Zip the dist folder:**

```bash
cd dist
zip -r ../tinytown.zip .
```

2. **Upload to itch.io:**
   - Create a new project at itch.io/game/new
   - Set "Kind of project" to "HTML"
   - Upload `tinytown.zip`
   - Set viewport dimensions (960×640 or "auto")
   - Check "Mobile friendly" (you earned it)
   - Enable "Fullscreen button"

3. **Or use butler (itch.io CLI) for automated deploys:**

```bash
# Install butler
npm install -g itchio/butler

# Push build
butler push dist yourname/tinytown:html5
```

## Performance Checklist

Before submitting, verify:

```typescript
// src/debug/perf-check.ts
export function runPerfCheck() {
  const checks = [
    { name: 'FPS > 55', pass: avgFPS > 55 },
    { name: 'Draw calls < 10', pass: drawCalls < 10 },
    { name: 'No memory leaks', pass: heapDelta < 1_000_000 },
    { name: 'Load time < 3s', pass: loadTime < 3000 },
    { name: 'Bundle < 2MB', pass: true }, // Checked at build time
  ];

  console.table(checks);
}
```

Manual checklist:

- [ ] 60 FPS with 200+ buildings
- [ ] No console errors
- [ ] Works in Chrome, Firefox, Safari
- [ ] Works on mobile (iOS Safari, Android Chrome)
- [ ] Audio plays after first interaction
- [ ] Save/load works after deploy (relative paths)
- [ ] No CORS errors (all assets bundled)
- [ ] Zoom works at all levels
- [ ] Touch controls responsive

## Loading Screen

Don't show a blank screen while assets load:

```typescript
// src/ui/loading-screen.ts
export class LoadingScreen {
  private element: HTMLElement;
  private progressBar: HTMLElement;

  constructor() {
    this.element = document.createElement('div');
    this.element.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: #1a1a2e; display: flex; flex-direction: column;
      align-items: center; justify-content: center; z-index: 9999;
    `;

    this.element.innerHTML = `
      <h1 style="color: #fff; font-family: monospace; margin-bottom: 20px;">TinyTown</h1>
      <div style="width: 200px; height: 4px; background: #333; border-radius: 2px;">
        <div id="load-progress" style="width: 0%; height: 100%; background: #4f4; border-radius: 2px; transition: width 0.2s;"></div>
      </div>
      <p style="color: #888; font-family: monospace; font-size: 12px; margin-top: 10px;">Loading assets...</p>
    `;

    document.body.appendChild(this.element);
    this.progressBar = this.element.querySelector('#load-progress')!;
  }

  setProgress(percent: number) {
    this.progressBar.style.width = `${percent}%`;
  }

  hide() {
    this.element.style.opacity = '0';
    this.element.style.transition = 'opacity 0.5s';
    setTimeout(() => this.element.remove(), 500);
  }
}

// Usage:
const loading = new LoadingScreen();

async function init() {
  loading.setProgress(10);
  await loadAtlas();

  loading.setProgress(40);
  await initAudio();

  loading.setProgress(70);
  await loadMap();

  loading.setProgress(100);
  loading.hide();

  startGameLoop();
}
```

## What We Built: The Full TinyTown Game

Twenty chapters. Four weeks of game jam. Here's what TinyTown became:

| Chapter | Feature |
|---------|---------|
| 1 | Canvas game loop (requestAnimationFrame, delta time) |
| 2 | Isometric projection (cartToIso, isoToCart) |
| 3 | Tile sprites and atlases |
| 4 | Mouse picking (click → grid cell) |
| 5 | Camera panning |
| 6 | Depth sorting (painter's algorithm) |
| 7 | Multi-tile buildings |
| 8 | Tile maps (Tiled editor integration) |
| 9 | Terrain (auto-tiling, elevation) |
| 10 | Animated tiles (water, smoke particles) |
| 11 | Build mode (ghost preview, validation, roads) |
| 12 | Performance (PixiJS, batching, culling) |
| 13 | Pathfinding (A*, NPC movement) |
| 14 | Camera zoom (anchor math, scroll wheel) |
| 15 | Lighting (day/night, point lights, rain) |
| 16 | HUD (resources, build menu, tooltips) |
| 17 | Save/load (JSON, localStorage, file export) |
| 18 | Audio (Web Audio, spatial, sprites) |
| 19 | Mobile (touch, pinch-zoom, responsive) |
| 20 | Ship it (build, optimize, deploy) |

From a blank `<canvas>` to a playable isometric city builder running in the browser, on desktop and mobile, with sound, lighting, persistence, and pathfinding.

## Riku's Reaction

You hit "Publish" on itch.io. The game is live. Riku shares the link.

Riku: "We actually did it. A city builder. In the browser. In four weeks."

You: "No engine. No Unity. Just math, a canvas, and a lot of `drawImage` calls."

Riku: "Well, PixiJS does the `drawImage` calls now."

You: "Fair. But we *understood* them first."

The game jam judges play TinyTown on their phones during lunch. Buildings snap to the grid. NPCs wander the streets. Rain falls at night. The city glows.

You ship it. 🏙️

---

[← Chapter 19: Mobile Touch](chapter-19-mobile-touch.md)
