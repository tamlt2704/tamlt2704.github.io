# Isometric 2D in JavaScript: A Game World Survival Story

You and your friend **Riku** are building an indie game for a game jam — **TinyTown** — a city builder where players place buildings, roads, and parks on an isometric grid. Think SimCity meets Stardew Valley, but in the browser.

The deadline is 4 weeks. You have no game engine. No Unity. No Godot. Just a `<canvas>` element, JavaScript, and a dream.

Riku handles art — pixel-perfect isometric tiles in Aseprite. You handle code. The first question:

> "How do I take a flat 2D grid and make it look 3D? How do I click on a tile and know which one it is? How do I draw things in the right order so buildings don't float behind the ground?"

You Google "isometric JavaScript." You find math. Lots of math. Rotation matrices. Coordinate transforms. Depth sorting. Tile maps. Camera systems.

It's not "just rotate 45 degrees."

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Game Programmer | "I can draw a rectangle on canvas. That's basically a game, right?" |
| **Riku** | Pixel Artist | Delivers beautiful tiles. Expects them placed perfectly. |
| **The Z-Order Bug** | That one glitch | A tree renders in front of a building that's behind it. |
| **The Click Bug** | That other glitch | You click a tile but the wrong one highlights. |
| **The Camera** | Movement system | Panning works until you zoom. Then everything breaks. |
| **The Game Jam Judge** | Deadline | "Does it run in the browser? Does it feel polished?" |

---

## The Stack

| Tool | What It Does |
|---|---|
| **HTML5 Canvas** | 2D rendering context |
| **PixiJS** | WebGL-accelerated 2D renderer (optional, Ch 12+) |
| **JavaScript/TypeScript** | Game logic |
| **Aseprite / Tiled** | Tile creation and map editing |
| **Vite** | Dev server, hot reload |

We start with raw Canvas (understand the math), then optionally move to PixiJS (performance at scale).

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Riku delivers new art assets and expects them working in-game
   │
   ▼
  🤔 You learn the isometric concept needed to place them correctly
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 Something renders wrong — Z-order, click detection, camera drift
   │
   ▼
  🧠 You understand the math and fix it
   │
   ▼
  📋 Next feature
```

No concept shows up before you need it. You won't hear about depth sorting until buildings overlap wrong. You won't touch camera zoom until panning alone isn't enough. You won't learn about tile atlases until individual image loads kill performance.

The visual bugs come first. The math follows.

---

## The Roadmap

### Part 1: Foundations — "Draw the Grid"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Draw a flat grid on canvas"           │ Canvas basics, game loop, tile grid
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Make it look isometric"               │ Isometric projection — the math, cartesian → iso
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Place Riku's tile sprites"            │ Tile rendering — image loading, sprite positioning
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Click a tile, highlight it"           │ Screen → iso conversion, mouse picking, hit detection
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Scroll around the map"                │ Camera — panning, viewport, world vs screen coords
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: World Building — "Fill the Grid"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Buildings overlap wrong"              │ Depth sorting — painter's algorithm, Z-order
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Tall buildings need multiple tiles"   │ Multi-tile objects — footprints, anchor points, height
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Load the map from a file"             │ Tile maps — 2D arrays, Tiled editor, JSON import
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Terrain: grass, water, elevation"     │ Tile types — terrain layers, auto-tiling, transitions
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Animate water and smoke"              │ Animated tiles — sprite sheets, frame timing
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Interaction — "Play the Game"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Place buildings with drag & drop"     │ Build mode — ghost preview, valid placement, snap to grid
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "It's slow with 500 buildings"         │ Performance — PixiJS, sprite batching, culling, dirty rects
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Characters walk between buildings"    │ Pathfinding — A* on isometric grid, movement animation
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Zoom in and out"                      │ Camera zoom — scale, anchor point, scroll wheel
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Day/night cycle, weather"             │ Lighting — tint overlays, particle effects, ambiance
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Polish — "Ship the Game"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "UI overlay: resources, menus"         │ HUD — HTML overlay vs canvas UI, layering
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Save and load the city"               │ Serialization — map state, localStorage, export/import
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Sound effects and music"              │ Audio — Web Audio API, spatial sound, triggers
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Mobile touch controls"                │ Touch — pinch zoom, tap to place, gesture handling
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Game jam submission day                │ Build, deploy, optimize — bundle, lazy load, itch.io
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Core Math (Preview)

Isometric projection transforms a flat (x, y) grid into a diamond-shaped view that looks 3D:

```
Cartesian (flat):              Isometric (projected):

  0,0  1,0  2,0                        ◇
  0,1  1,1  2,1                      ◇   ◇
  0,2  1,2  2,2                    ◇   ◇   ◇
                                     ◇   ◇
                                       ◇
```

The transform:

```javascript
// Cartesian → Isometric (screen position)
function toIso(x, y) {
  return {
    screenX: (x - y) * (TILE_WIDTH / 2),
    screenY: (x + y) * (TILE_HEIGHT / 2),
  };
}

// Isometric → Cartesian (mouse picking)
function toCart(screenX, screenY) {
  return {
    x: Math.floor((screenX / (TILE_WIDTH / 2) + screenY / (TILE_HEIGHT / 2)) / 2),
    y: Math.floor((screenY / (TILE_HEIGHT / 2) - screenX / (TILE_WIDTH / 2)) / 2),
  };
}
```

That's it. Two functions. The entire isometric engine is built on these transforms. Chapter 2 derives them from scratch so you understand *why* they work.

---

## What You'll Build

By Chapter 20:

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│              ◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇                             │
│            ◇  🌳  🏠  🏢  🌳  ◇                             │
│          ◇  🛣️  🛣️  🛣️  🛣️  ◇                              │
│        ◇  🌳  🏪  🏠  🌲  ◇                                │
│          ◇  🛣️  🛣️  🛣️  ◇                                  │
│            ◇  🌊  🌊  🌊  ◇                                 │
│              ◇◇◇◇◇◇◇◇◇◇◇                                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  💰 1,250  👥 342  🏠 28  ⚡ 87%                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

A playable isometric city builder with:
- Tile-based terrain (grass, water, roads)
- Placeable buildings with correct depth sorting
- Camera pan + zoom
- Click-to-select and drag-to-place
- Animated tiles (water, smoke, characters)
- A* pathfinding for NPCs
- Day/night cycle
- Save/load
- Mobile touch support

---

## Isometric vs. Other Projections

```
Top-down (Zelda):          Isometric (SimCity):        Side-scroll (Mario):
─────────────────          ────────────────────        ────────────────────
Camera looks straight      Camera at ~30° angle        Camera looks from side
down                       (actually 2:1 ratio)
No depth illusion          Fake 3D depth               No depth (parallax only)
Simple math                Moderate math                Simplest math
Good for: RPGs, roguelikes Good for: builders, tactics Good for: platformers
```

True isometric is 30° rotation. Game isometric (what we use) is a **2:1 ratio** — tile width is 2× tile height. This makes pixel art easier and math cleaner.

```
True isometric:    Game isometric (2:1):
  30° angle          ~26.57° angle
  √3:1 ratio         2:1 ratio (cleaner pixels)
```

---

## The Tile Anatomy

```
        ╱╲          ← top edge
       ╱  ╲         
      ╱    ╲        TILE_WIDTH = 64px
     ╱      ╲       TILE_HEIGHT = 32px
    ╱        ╲      
    ╲        ╱      (2:1 ratio)
     ╲      ╱       
      ╲    ╱        
       ╲  ╱         
        ╲╱          ← bottom edge
```

A standard isometric tile is a diamond. Common sizes:
- 64×32 (small, retro)
- 128×64 (medium, detailed)
- 256×128 (large, HD)

Riku is drawing at 64×32. Each tile is a PNG with transparent corners.

---

## Prerequisites

### Node.js + Vite

```bash
mkdir tinytowm && cd tinytown
npm init -y
npm install -D vite typescript
```

### Project Structure

```
tinytown/
├── index.html
├── src/
│   ├── main.ts
│   ├── engine/
│   │   ├── camera.ts
│   │   ├── grid.ts
│   │   ├── renderer.ts
│   │   └── input.ts
│   ├── game/
│   │   ├── tiles.ts
│   │   ├── buildings.ts
│   │   └── world.ts
│   └── assets/
│       └── tiles/
│           ├── grass.png
│           ├── water.png
│           └── road.png
├── package.json
└── tsconfig.json
```

### Starter HTML

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>TinyTown</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #1a1a2e; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
  <canvas id="game"></canvas>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

### Verify: Draw a Diamond

```typescript
// src/main.ts
const canvas = document.getElementById('game') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const TILE_W = 64;
const TILE_H = 32;

// Draw one isometric tile (diamond)
function drawTile(screenX: number, screenY: number, color: string) {
  ctx.beginPath();
  ctx.moveTo(screenX, screenY - TILE_H / 2);           // top
  ctx.lineTo(screenX + TILE_W / 2, screenY);           // right
  ctx.lineTo(screenX, screenY + TILE_H / 2);           // bottom
  ctx.lineTo(screenX - TILE_W / 2, screenY);           // left
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
  ctx.strokeStyle = '#333';
  ctx.stroke();
}

// Draw a 5x5 grid
for (let x = 0; x < 5; x++) {
  for (let y = 0; y < 5; y++) {
    const screenX = canvas.width / 2 + (x - y) * (TILE_W / 2);
    const screenY = 200 + (x + y) * (TILE_H / 2);
    drawTile(screenX, screenY, '#2d5a27');
  }
}
```

```bash
npx vite
```

If you see a diamond-shaped grid of green tiles — you're ready to build a city.

---

## Optional: PixiJS (Chapter 12+)

For performance at scale (500+ tiles, animations, particles), we'll introduce PixiJS:

```bash
npm install pixi.js
```

But we start with raw Canvas. Understanding the math matters more than the renderer. Once you know how isometric projection works, switching renderers is trivial.

---

## Optional: Tiled Map Editor (Chapter 8+)

For designing maps visually instead of in code:

- Download from [mapeditor.org](https://www.mapeditor.org/)
- Free, open source
- Exports JSON that we'll parse directly

---

[Next: Chapter 1 — The Canvas & Game Loop →](chapter-01-canvas-game-loop.md)
