# Chapter 0: Overview — "How Do I Even Set This Up?"

[Chapter 1: First Sprite →](chapter-01-first-sprite.md)

---

## The Crisis

It's Friday night. The jam theme just dropped: **"Dungeon."** Kai is already sketching a knight character — 16×16 pixels, four frames of walk animation. You open your terminal. You know React. You know Vite. But you've never rendered a game loop in a browser.

Kai says: "Use PixiJS. There's a React wrapper. You'll feel at home."

You Google it. There are two versions of @pixi/react — v7 (stable, React 18) and v8 (bleeding edge, React 19 only). You're on React 18. v7 it is.

## Install

```bash
npm create vite@latest dungeonbit -- --template react
cd dungeonbit
npm install pixi.js@7 @pixi/react
npm install -D @types/pixi.js  # optional, for TS users
npm run dev
```

Your project structure:

```
dungeonbit/
├── public/
│   └── sprites/          ← Kai's pixel art goes here
│       ├── knight.png
│       ├── slime.png
│       └── tiles.png
├── src/
│   ├── components/       ← game components (Player, Enemy, Map)
│   ├── hooks/            ← custom hooks (useKeyboard, useGameState)
│   ├── scenes/           ← scene components (TitleScreen, Gameplay)
│   ├── data/             ← level data, constants
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── vite.config.js
└── package.json
```

## The Key Insight: React Renders to a Canvas

In normal React, you render to the DOM. With @pixi/react, you render to a WebGL canvas. Same mental model — components, props, children — but instead of `<div>` and `<span>`, you get `<Sprite>` and `<Container>`.

```
Normal React:          @pixi/react:
─────────────          ────────────
<div>                  <Stage>
  <img>                  <Sprite>
  <p>                    <Text>
  <canvas>               <Graphics>
  <div>                  <Container>
    <img>                  <Sprite>
```

The `<Stage>` component is your root — it creates the PixiJS Application and the WebGL canvas. Everything inside it is rendered by PixiJS, not the DOM.

## Your First Stage

Replace `src/App.jsx`:

```jsx
import { Stage } from '@pixi/react';

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e }}
    >
      {/* Game goes here */}
    </Stage>
  );
}

export default App;
```

Run `npm run dev`. You see a dark blue rectangle. That's your game canvas. 480×320 pixels — a classic retro resolution.

## Understanding the Stage

The `<Stage>` component:
- Creates a `PIXI.Application` under the hood
- Mounts a `<canvas>` element in the DOM
- Starts the game loop (60fps ticker)
- Provides the PixiJS app context to all children

```jsx
<Stage
  width={480}           // canvas width in pixels
  height={320}          // canvas height in pixels
  options={{
    background: 0x1a1a2e,  // hex color (no # prefix, use 0x)
    antialias: false,       // OFF for pixel art (we want crispy pixels)
    resolution: 1,          // device pixel ratio (1 for pixel art)
  }}
>
```

**Important for pixel art:** Set `antialias: false`. Anti-aliasing blurs pixel edges. We want hard, crispy pixels.

## Scaling the Canvas with CSS

The canvas is 480×320 logical pixels, but you probably want it bigger on screen. Use CSS to scale it up without blurring:

```css
/* src/index.css */
body {
  margin: 0;
  background: #0a0a0a;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

canvas {
  image-rendering: pixelated;        /* Chrome, Edge */
  image-rendering: crisp-edges;      /* Firefox */
  width: 960px !important;           /* 2x scale */
  height: 640px !important;
}
```

`image-rendering: pixelated` tells the browser to use nearest-neighbor scaling when the canvas is stretched. No blur. Crispy pixels.

## The v7 API at a Glance

Here's what you'll use throughout this course:

```jsx
// Components (JSX elements)
import { Stage, Container, Sprite, Text, Graphics } from '@pixi/react';

// Hooks
import { useTick, useApp } from '@pixi/react';

// PixiJS core (for types, constants, utilities)
import * as PIXI from 'pixi.js';
```

| Component | What it does | Web equivalent |
|---|---|---|
| `<Stage>` | Root canvas + app | `<div id="root">` |
| `<Container>` | Groups children, has transform | `<div>` |
| `<Sprite>` | Displays an image/texture | `<img>` |
| `<Text>` | Renders text | `<p>` |
| `<Graphics>` | Draws shapes programmatically | `<canvas>` 2D context |

| Hook | What it does |
|---|---|
| `useTick(callback)` | Runs callback every frame (game loop) |
| `useApp()` | Access the PIXI.Application instance |

## Quick Verify: A Colored Box

Let's prove everything works. Add a simple colored rectangle to the stage:

```jsx
import { Stage, Graphics } from '@pixi/react';
import { useCallback } from 'react';

function ColorBox() {
  const draw = useCallback((g) => {
    g.clear();
    g.beginFill(0xe74c3c);
    g.drawRect(100, 100, 64, 64);
    g.endFill();
  }, []);

  return <Graphics draw={draw} />;
}

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e, antialias: false }}
    >
      <ColorBox />
    </Stage>
  );
}

export default App;
```

You should see a red square on a dark blue background. If you see that, your setup is working.

## Why @pixi/react v7?

| | v7 (this course) | v8 |
|---|---|---|
| React version | 18 (stable) | 19 only |
| API style | `<Sprite>`, `<Container>` | `<pixiSprite>`, `<pixiContainer>` |
| Stability | Battle-tested | New, evolving |
| Docs/examples | Plenty | Sparse |
| Install | `pixi.js@7 @pixi/react` | `pixi.js@8 @pixi/react@8` |

v8 uses a custom JSX pragma with `pixi` prefixes. It's the future, but v7 is what you ship a game jam with today.

## Project Conventions

For the rest of this course:

- All sprites live in `public/sprites/`
- Game components go in `src/components/`
- Custom hooks go in `src/hooks/`
- Scene components go in `src/scenes/`
- Level data (tile maps, enemy positions) goes in `src/data/`
- We use plain `.jsx` files (TypeScript is optional)

## Verify Checklist

- [ ] `npm run dev` starts without errors
- [ ] You see a dark blue canvas (480×320)
- [ ] The red square renders at (100, 100)
- [ ] The canvas scales up crispy (no blur) with the CSS
- [ ] Browser console shows no warnings

Kai texts: "Knight sprite is done. 16×16, transparent background. Where do I put it?"

That's Chapter 1.

---

[Chapter 1: First Sprite →](chapter-01-first-sprite.md)
