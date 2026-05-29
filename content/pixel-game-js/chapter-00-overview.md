# Building Pixel Art Games with JavaScript

[next: Canvas Basics](./chapter-01-canvas-basics.md)

This course teaches you to build pixel art games using JavaScript and TypeScript. You'll learn three approaches — raw Canvas API for full control, Kaboom.js for simplicity, and Phaser 3 for production-ready games.

## What You'll Build

```
+-------------------+    +-------------------+
|   PLATFORMER      |    |    TOP-DOWN RPG   |
|                   |    |                   |
|    @              |    |   [NPC] "Hello!"  |
|   /|\  ___        |    |     @-->          |
|   / \ |___|       |    |   [chest] [door]  |
|  ========###===   |    |   ####  ####      |
+-------------------+    +-------------------+
```

## Chapters

1. [Canvas Basics](./chapter-01-canvas-basics.md) — Raw pixel drawing, the foundation
2. [Game Loop](./chapter-02-game-loop.md) — Fixed timestep, input, game states
3. [Sprites](./chapter-03-sprites.md) — Sprite sheets, animation, collision
4. [Tilemaps](./chapter-04-tilemap.md) — Tile-based worlds, camera, layers
5. [Phaser 3](./chapter-05-phaser.md) — Full-featured framework, build a platformer
6. [Kaboom.js](./chapter-06-kaboom.md) — Simplest framework, build an RPG
7. [Platformer Project](./chapter-07-platformer.md) — Complete platformer from scratch
8. [RPG Project](./chapter-08-rpg.md) — Complete top-down RPG
9. [Polish](./chapter-09-polish.md) — Juice, particles, shaders, sound
10. [Publishing](./chapter-10-publish.md) — Bundle, deploy, mobile, PWA

## Framework Comparison

| Feature         | Raw Canvas | Pixi.js | Kaboom.js       | Phaser 3   |
| --------------- | ---------- | ------- | --------------- | ---------- |
| Learning curve  | Steep      | Medium  | Easy            | Medium     |
| Bundle size     | 0 KB       | ~200 KB | ~80 KB          | ~1 MB      |
| Physics         | DIY        | DIY     | Built-in        | Built-in   |
| Tilemap support | DIY        | Plugin  | Built-in        | Built-in   |
| WebGL           | No         | Yes     | Yes             | Yes        |
| Community       | N/A        | Large   | Small           | Large      |
| Best for        | Learning   | Visuals | Jams/Prototypes | Production |

## When to Use Each

**Raw Canvas API** — Use when you want to understand how everything works under the hood, or when your game is simple enough that a framework adds unnecessary weight.

**Pixi.js** — Use when you need high-performance 2D rendering (thousands of sprites) but want to build your own game logic. It's a renderer, not a game framework.

**Kaboom.js** — Use for game jams, prototypes, or if you're a beginner. The API is fun and expressive. You can build a game in under 100 lines.

**Phaser 3** — Use for production games. It has everything: physics, tilemaps, animations, audio, input, cameras, particles. Large community and plugin ecosystem.

## Prerequisites

- JavaScript/TypeScript basics
- HTML and CSS fundamentals
- A code editor (VS Code recommended)
- Node.js installed (for bundling later)

## Quick Start

Create a minimal pixel game canvas:

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
canvas.width = 128;
canvas.height = 128;
ctx.imageSmoothingEnabled = false;

// Draw a pixel character
ctx.fillStyle = "#e94560";
ctx.fillRect(4, 4, 2, 2); // head
ctx.fillRect(3, 6, 4, 4); // body
ctx.fillRect(3, 10, 1, 3); // left leg
ctx.fillRect(6, 10, 1, 3); // right leg
```

Style the canvas in CSS to scale up without blur:

```css
canvas {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  width: 512px;
  height: 512px;
  background: #1a1a2e;
}
```

The key trick: render to a small canvas (128x128) and scale it up with CSS. The `image-rendering: pixelated` property keeps pixels sharp instead of blurry.

[next: Canvas Basics](./chapter-01-canvas-basics.md)
