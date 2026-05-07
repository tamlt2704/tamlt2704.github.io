# Isometric 2D in JavaScript

A game jam. 4 weeks. No engine. Just Canvas, math, and pixel art. Build an isometric city builder from scratch.

## The Story

You and **Riku** (pixel artist) are building **TinyTown** — an isometric city builder in the browser. No Unity, no Godot. Just HTML5 Canvas, JavaScript, and the two functions that make flat grids look 3D. Start with raw Canvas to understand the math, then optionally scale with PixiJS.

## Chapters

### Part 1: Draw the Grid

| # | The Task | What You Learn |
|---|---------|----------------|
| 01 | Draw a flat grid on canvas | Canvas basics, game loop, tile grid |
| 02 | Make it look isometric | Isometric projection math, cartesian → iso |
| 03 | Place Riku's tile sprites | Image loading, sprite positioning |
| 04 | Click a tile, highlight it | Screen → iso conversion, mouse picking |
| 05 | Scroll around the map | Camera panning, viewport, world vs screen |

### Part 2: Fill the Grid

| # | The Task | What You Learn |
|---|---------|----------------|
| 06 | Buildings overlap wrong | Depth sorting, painter's algorithm, Z-order |
| 07 | Tall buildings, multiple tiles | Multi-tile objects, footprints, anchors |
| 08 | Load map from a file | Tile maps, Tiled editor, JSON import |
| 09 | Terrain: grass, water, elevation | Tile types, auto-tiling, transitions |
| 10 | Animate water and smoke | Sprite sheets, frame timing |

### Part 3: Play the Game

| # | The Task | What You Learn |
|---|---------|----------------|
| 11 | Place buildings with drag & drop | Build mode, ghost preview, snap to grid |
| 12 | Slow with 500 buildings | PixiJS, sprite batching, culling |
| 13 | Characters walk between buildings | A* pathfinding on iso grid |
| 14 | Zoom in and out | Camera zoom, scale, anchor point |
| 15 | Day/night cycle, weather | Tint overlays, particles, ambiance |

### Part 4: Ship the Game

| # | The Task | What You Learn |
|---|---------|----------------|
| 16 | UI overlay: resources, menus | HUD, HTML overlay vs canvas UI |
| 17 | Save and load the city | Serialization, localStorage |
| 18 | Sound effects and music | Web Audio API, spatial sound |
| 19 | Mobile touch controls | Pinch zoom, tap to place, gestures |
| 20 | Game jam submission | Build, deploy, optimize, itch.io |

## The Core Math

```javascript
// Cartesian → Isometric
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

Two functions. The entire engine is built on these.

## Prerequisites

```bash
npm init -y && npm install -D vite typescript
# Optional (Chapter 12+): npm install pixi.js
npx vite
```
