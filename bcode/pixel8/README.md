# Pixel Art & Games with Pixel8 — The BitForge Story

Build retro pixel art and games using only code — no image files, no Photoshop. Everything is drawn with primitives and sprite data arrays.

## The Story

Your friend **Mika** is a retro game enthusiast who grew up modding Game Boy ROMs and drawing sprites on graph paper. One evening she sends you a challenge:

> "I bet you can't recreate classic 8-bit visuals using *only code*. No PNGs. No sprite sheets. No asset pipeline. Just numbers and colors. Pure data."

You accept. The tool: **Pixel8** — a React library that renders pixel art to a Canvas via ArrayBuffers. It gives you a custom React renderer with built-in primitives like `<rect>`, `<circ>`, `<pixel>`, `<sprite>`, and `<text>`. You write JSX. It draws pixels.

Over 11 chapters, you'll build **BitForge** — a tiny pixel art game/toy that runs in the browser. You'll start with a single colored pixel and end with a complete playable mini-game, all rendered at true 8-bit resolution.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The Coder | React dev who's never drawn pixel art |
| **Mika** | The Challenger | Retro enthusiast, pixel purist, "constraints are freedom" |
| **Pixel8** | The Renderer | Custom React renderer → Canvas via ArrayBuffers |
| **BitForge** | The Project | Your pixel art game, built from nothing but numbers |

## Chapters

| # | Chapter | What You Build |
|---|---------|----------------|
| 00 | [Overview](chapter-00-overview.md) | Install Pixel8, first Stage, philosophy of constraints |
| 01 | [Pixels & Shapes](chapter-01-pixels-shapes.md) | Drawing with `<pixel>`, `<rect>`, `<circ>` primitives |
| 02 | [Sprites](chapter-02-sprites.md) | Encoding pixel art as number arrays with palette mapping |
| 03 | [Animation](chapter-03-animation.md) | Motion with `<transition>` and `<animation>` |
| 04 | [Interaction](chapter-04-interaction.md) | Keyboard/mouse input with React state |
| 05 | [Game Loop](chapter-05-game-loop.md) | The `fps` prop, per-frame updates, collision detection |
| 06 | [Buffers](chapter-06-buffers.md) | Raw pixel manipulation with `<buffer>` |
| 07 | [Text & UI](chapter-07-text-ui.md) | Pixel font text, HUD, menus, game over screens |
| 08 | [Palettes](chapter-08-palettes.md) | Retro color palettes, palette swapping, mood |
| 09 | [Composition](chapter-09-composition.md) | Layering sprites, scene management, complex scenes |
| 10 | [Mini-Game](chapter-10-mini-game.md) | Complete playable game combining everything |

## Prerequisites

- Node.js 8+ and npm/yarn
- Basic React knowledge (components, props, state, hooks)
- A text editor and terminal
- That's it — no image editor, no asset tools

## Install

```bash
# Create a new project
npx create-react-app bitforge
cd bitforge

# Install Pixel8
npm install pixel8

# Start dev server
npm start
```

> **Compatibility Note:** Pixel8 was created in 2017 and targets React 16. It may not work with React 18+ out of the box. For best results, use React 16 or pin your React version:
>
> ```bash
> npm install react@16 react-dom@16 pixel8
> ```
>
> The concepts and API patterns in this course transfer directly to any pixel art framework (PICO-8, TIC-80, canvas2d, WebGL). Focus on the *ideas* — they're timeless even if the library evolves.

## Why Pixel8

- **Pure React** — JSX components, props, state, hooks. Your existing mental model works.
- **No assets needed** — sprites are just number arrays. Colors are hex strings. Everything is code.
- **True 8-bit rendering** — Canvas via ArrayBuffers, not scaled-up CSS. Authentic pixel grid.
- **Constraints breed creativity** — 64×64 pixels forces you to think like a retro artist.
- **Instant feedback** — hot reload shows every pixel change immediately.

## The BitForge Concept

BitForge is a pixel art playground that evolves into a game:

```
Ch 0-2:  Static pixel art (shapes, sprites, characters)
Ch 3-5:  Motion and interaction (animation, input, game loop)
Ch 6-8:  Polish (buffers, text, palettes)
Ch 9-10: Full game (composition, mini-game)
```

## How to Use This Course

Each chapter follows the same pattern:

1. **Mika's challenge** — what she dares you to create
2. **The concept** — how Pixel8 handles it
3. **Working code** — copy, paste, see pixels
4. **Visual result** — what you should see on screen
5. **Tips** — pixel art design wisdom
6. **Exercise** — push yourself further
7. **Quick reference** — the API at a glance

## Key Code Pattern

```jsx
import React from 'react';
import { render } from 'react-dom';
import { Stage } from 'pixel8';

const App = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
    {/* Pixel8 primitives go here — no imports needed */}
    <rect x={10} y={10} width={8} height={8} color="#e94560" />
    <circ x={32} y={32} radius={5} color="#0f3460" />
    <pixel x={5} y={5} color="#ffffff" />
  </Stage>
);

render(<App />, document.getElementById('root'));
```

Only `Stage` needs to be imported. Everything inside it — `<rect>`, `<circ>`, `<pixel>`, `<sprite>`, `<text>`, `<buffer>`, `<transition>`, `<animation>` — is provided by Pixel8's custom renderer.

---

*"The first computer artists didn't have Photoshop. They had grids and numbers. That's all you need."*
— Mika
