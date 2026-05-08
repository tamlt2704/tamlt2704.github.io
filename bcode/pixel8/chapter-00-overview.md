# Chapter 0: Overview — "Constraints Are Freedom"

[Chapter 1: Pixels & Shapes →](chapter-01-pixels-shapes.md)

---

## Mika's Challenge

Mika sends you a screenshot of a Game Boy boot screen — that iconic Nintendo logo scrolling down, rendered in four shades of green on a 160×144 display.

> "See that? 23,040 pixels. Four colors. No anti-aliasing. No gradients. And it's *iconic*. That's what constraints do — they force clarity. I want you to build something like that. But in React. In a browser. With a library called Pixel8."

She drops a GitHub link: [github.com/vsmode/pixel8](https://github.com/vsmode/pixel8)

> "It's a custom React renderer. You write JSX, it draws pixels to a Canvas using ArrayBuffers. Real 8-bit rendering. No faking it with CSS `image-rendering: pixelated`. The actual thing."

## What Is Pixel8?

Pixel8 is a React library for creating pixel art and low-resolution games. It provides:

- A custom React renderer (like React Native, but for pixel canvases)
- Built-in primitives: `<pixel>`, `<rect>`, `<circ>`, `<sprite>`, `<text>`, `<buffer>`
- Animation via `<transition>` and `<animation>` components
- Canvas rendering via ArrayBuffers for authentic 8-bit aesthetics
- No opinions about palettes, resolution, or constraints — you choose

The philosophy: **everything is data**. A sprite isn't a PNG file — it's an array of numbers. A color isn't a gradient — it's a hex string. A scene isn't layers in Photoshop — it's nested React components.

## Install

```bash
# New project
npx create-react-app bitforge
cd bitforge

# Install Pixel8 (use React 16 for compatibility)
npm install react@16 react-dom@16 pixel8

# Or with yarn
yarn add react@16 react-dom@16 pixel8
```

> **Note:** Pixel8 was built in 2017 for React 16. If you're using a newer React version, you may need to pin to React 16 or use a compatibility shim. The concepts transfer to any pixel framework — focus on the patterns.

### Alternative: Vite Setup

```bash
npm create vite@latest bitforge -- --template react
cd bitforge
npm install pixel8
npm run dev
```

Your project structure:

```
bitforge/
├── src/
│   ├── App.jsx          ← your Pixel8 scenes
│   ├── sprites.js       ← sprite data arrays
│   ├── palettes.js      ← color palette definitions
│   └── index.js         ← entry point
├── package.json
└── index.html
```

## Your First Stage

The `Stage` component is Pixel8's root — it creates the Canvas element and sets up the renderer. Everything inside it uses Pixel8's custom primitives.

Replace `src/App.jsx`:

```jsx
import React from 'react';
import { Stage } from 'pixel8';

const App = () => (
  <Stage
    width={64}
    height={64}
    scale={8}
    fps={0}
    background="#1a1a2e"
  />
);

export default App;
```

And `src/index.js`:

```jsx
import React from 'react';
import { render } from 'react-dom';
import App from './App';

render(<App />, document.getElementById('root'));
```

### What You Should See

A 512×512 pixel window (64 pixels × 8 scale) filled with a dark navy background (`#1a1a2e`). No content yet — just a blank canvas waiting for pixels.

## Stage Props Explained

| Prop | Type | Description |
|------|------|-------------|
| `width` | number | Canvas width in virtual pixels (e.g., 64) |
| `height` | number | Canvas height in virtual pixels (e.g., 64) |
| `scale` | number | How many screen pixels per virtual pixel (e.g., 8 = 512px display) |
| `fps` | number | Frames per second. `0` = static (no game loop). `60` = full speed. |
| `background` | string | Background color as hex string |
| `gridColor` | string | Optional grid overlay for debugging alignment |

The `width` and `height` define your *virtual resolution* — the actual pixel grid you work with. The `scale` blows it up for visibility. A 64×64 stage at scale 8 creates a 512×512 canvas on screen, but you only think in 64×64 coordinates.

## The Philosophy: Why Constraints Work

Mika explains over coffee:

> "When you have unlimited resolution, you procrastinate. 'Should this button be 3px or 4px rounded?' But at 64×64, there's no room for indecision. Every pixel matters. Every pixel is a choice. That's why pixel art is *designed*, not drawn."

Key principles:

1. **Low resolution forces intentionality** — you can't hide behind detail
2. **Limited palettes create cohesion** — 4 colors that work together beat 16 million that don't
3. **Data-as-art is portable** — a sprite array works anywhere, forever
4. **Iteration is instant** — change a number, see a pixel move

## Verify Your Setup

Add a single pixel to confirm everything works:

```jsx
import React from 'react';
import { Stage } from 'pixel8';

const App = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
    <pixel x={32} y={32} color="#ffffff" />
  </Stage>
);

export default App;
```

You should see a single white dot in the center of the dark canvas. That's your first pixel. Everything in BitForge starts here.

## Debugging: The Grid

Enable the grid overlay to see pixel boundaries:

```jsx
<Stage
  width={64}
  height={64}
  scale={8}
  fps={0}
  background="#1a1a2e"
  gridColor="rgba(255,255,255,0.1)"
>
  <pixel x={32} y={32} color="#ffffff" />
</Stage>
```

The grid shows every pixel cell — invaluable when positioning sprites and aligning shapes.

## Exercise

1. Change the background to `#0f380f` (Game Boy green) and the pixel to `#9bbc0f` (Game Boy light green)
2. Try different `scale` values: 4, 8, 12. Notice how the canvas size changes but the pixel grid stays 64×64
3. Set `width` and `height` to 128. You now have 4× the pixels to work with — does it feel more or less constrained?
4. Place pixels at all four corners: (0,0), (63,0), (0,63), (63,63)

## Quick Reference

```jsx
// Minimal Pixel8 app
import React from 'react';
import { render } from 'react-dom';
import { Stage } from 'pixel8';

const App = () => (
  <Stage width={W} height={H} scale={S} fps={F} background={COLOR}>
    {/* primitives here — no imports needed */}
  </Stage>
);

render(<App />, document.getElementById('root'));
```

| Concept | Value |
|---------|-------|
| Import | Only `Stage` from `'pixel8'` |
| Primitives | Available inside Stage without import |
| Coordinates | (0,0) is top-left |
| Colors | Hex strings: `"#ff0000"`, `"#1a1a2e"` |
| Static mode | `fps={0}` — renders once |
| Game mode | `fps={60}` — renders every frame |

---

Next up: Mika wants you to draw something real. Shapes, patterns, simple art — all from `<pixel>`, `<rect>`, and `<circ>`.

[Chapter 1: Pixels & Shapes →](chapter-01-pixels-shapes.md)
