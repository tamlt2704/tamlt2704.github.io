# Chapter 2: Sprites — "Art Is Just Numbers"

[← Chapter 1: Pixels & Shapes](chapter-01-pixels-shapes.md) | [Chapter 3: Animation →](chapter-03-animation.md)

---

## Mika's Challenge

Mika slides her phone across the table. On screen: a tiny 8×8 heart, a sword, a potion bottle, and a skull — all drawn on graph paper with colored pencils.

> "These are your game's items. But here's the rule: no image files. Encode them as arrays of numbers. Each number maps to a color in a palette. That's how the old consoles did it — the NES stored sprites as indices into a color table. Pure data."

She grins:

> "If your art is just numbers, you can generate it, transform it, animate it, and version-control it. Try doing that with a PNG."

## The Sprite Data Model

A Pixel8 sprite is:
1. A **flat array** of numbers (palette indices)
2. A **palette** array mapping indices to color strings
3. A **width** (implied by the data length and display size)

The data array is read left-to-right, top-to-bottom — like reading a book. For an 8×8 sprite, the array has 64 elements.

```jsx
// An 8×8 heart sprite
// 0 = transparent, 1 = red
const heart = [
  0,1,1,0,0,1,1,0,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,1,1,1,0,0,
  0,0,0,1,1,0,0,0,
  0,0,0,0,0,0,0,0,
];

const heartPalette = ['transparent', '#ff0000'];
```

Render it:

```jsx
<sprite x={28} y={28} data={heart} palette={heartPalette} />
```

## Your First Sprite: The Heart

```jsx
import React from 'react';
import { Stage } from 'pixel8';

const heart = [
  0,1,1,0,0,1,1,0,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,1,1,1,0,0,
  0,0,0,1,1,0,0,0,
  0,0,0,0,0,0,0,0,
];

const App = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
    <sprite x={28} y={28} data={heart} palette={['transparent', '#ff0000']} />
  </Stage>
);

export default App;
```

### What You Should See

A red heart shape centered on the dark canvas. 8×8 pixels of pure data-driven art.

## Multi-Color Sprites

Use more palette indices for complex sprites:

```jsx
// A potion bottle — 4 colors
// 0 = transparent, 1 = glass (light blue), 2 = liquid (purple), 3 = cork (brown)
const potion = [
  0,0,0,3,3,0,0,0,
  0,0,0,3,3,0,0,0,
  0,0,1,1,1,1,0,0,
  0,1,1,2,2,1,1,0,
  0,1,2,2,2,2,1,0,
  0,1,2,2,2,2,1,0,
  0,1,2,2,2,2,1,0,
  0,0,1,1,1,1,0,0,
];

const potionPalette = [
  'transparent',  // 0
  '#add8e6',      // 1 — glass
  '#8b00ff',      // 2 — liquid
  '#8b4513',      // 3 — cork
];

<sprite x={10} y={10} data={potion} palette={potionPalette} />
```

## The Sprite Workflow

Mika's process for creating sprites:

```
1. Sketch on graph paper (or spreadsheet)
   ┌─┬─┬─┬─┬─┬─┬─┬─┐
   │ │█│█│ │ │█│█│ │  ← row 0
   ├─┼─┼─┼─┼─┼─┼─┼─┤
   │█│█│█│█│█│█│█│█│  ← row 1
   └─┴─┴─┴─┴─┴─┴─┴─┘

2. Assign numbers to colors
   empty = 0, filled = 1

3. Read left-to-right, top-to-bottom
   [0,1,1,0,0,1,1,0, 1,1,1,1,1,1,1,1, ...]

4. Define palette
   ['transparent', '#ff0000']

5. Render with <sprite>
```

## Building a Character: The Knight

```jsx
// 8×8 knight character
// 0=transparent, 1=armor(silver), 2=visor(dark), 3=plume(red), 4=skin
const knight = [
  0,0,3,3,3,0,0,0,
  0,0,1,1,1,0,0,0,
  0,1,2,2,2,1,0,0,
  0,1,4,4,4,1,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,0,1,0,0,0,
  0,0,1,0,1,0,0,0,
];

const knightPalette = [
  'transparent',  // 0
  '#c0c0c0',      // 1 — armor
  '#333333',      // 2 — visor
  '#ff0000',      // 3 — plume
  '#ffcc99',      // 4 — skin
];
```

## An Item Set for BitForge

```jsx
// sprites.js — BitForge item sprites

export const sword = [
  0,0,0,0,0,0,1,0,
  0,0,0,0,0,1,1,0,
  0,0,0,0,1,1,0,0,
  0,0,0,1,1,0,0,0,
  0,2,1,1,0,0,0,0,
  0,0,2,0,0,0,0,0,
  0,2,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,
];

export const coin = [
  0,0,1,1,1,1,0,0,
  0,1,2,2,2,2,1,0,
  1,2,2,1,1,2,2,1,
  1,2,2,1,1,2,2,1,
  1,2,2,1,1,2,2,1,
  1,2,2,2,2,2,2,1,
  0,1,2,2,2,2,1,0,
  0,0,1,1,1,1,0,0,
];

export const skull = [
  0,0,1,1,1,1,0,0,
  0,1,1,1,1,1,1,0,
  1,1,2,1,1,2,1,1,
  1,1,2,1,1,2,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,2,2,1,0,0,
  0,0,2,1,1,2,0,0,
  0,0,0,0,0,0,0,0,
];

export const palettes = {
  sword: ['transparent', '#c0c0c0', '#8b4513'],
  coin:  ['transparent', '#daa520', '#ffd700'],
  skull: ['transparent', '#f5f5dc', '#333333'],
};
```

Render the full set:

```jsx
import React from 'react';
import { Stage } from 'pixel8';
import { sword, coin, skull, palettes } from './sprites';

const ItemShowcase = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
    <sprite x={8}  y={28} data={sword} palette={palettes.sword} />
    <sprite x={28} y={28} data={coin}  palette={palettes.coin} />
    <sprite x={48} y={28} data={skull} palette={palettes.skull} />
  </Stage>
);
```

### What You Should See

Three items in a row: a silver diagonal sword, a golden coin with a center detail, and a cream-colored skull. All from pure number arrays.

## Tips: Designing Sprites

1. **Start with silhouette** — fill the shape with one color first, then add detail
2. **Use odd dimensions** — 7×7 or 5×5 gives you a center pixel for symmetry
3. **Outline with index 1** — many retro games use palette index 1 as a dark outline
4. **Leave row 0 and col 0 empty** — gives visual breathing room
5. **Test at 1:1 scale** — zoom out to see if the shape reads at actual size
6. **Limit to 3-4 colors per sprite** — more than that gets muddy at 8×8

## Pattern: Sprite as React Component

Wrap sprites in components for reuse:

```jsx
const Heart = ({ x, y, color = '#ff0000' }) => (
  <sprite
    x={x}
    y={y}
    data={heart}
    palette={['transparent', color]}
  />
);

// Use it multiple times
<Heart x={10} y={5} />
<Heart x={20} y={5} color="#ff69b4" />
<Heart x={30} y={5} color="#8b0000" />
```

## Pattern: Generating Sprite Data

You can compute sprite data programmatically:

```jsx
// Generate a gradient square
const gradientSquare = Array.from({ length: 64 }, (_, i) => {
  const row = Math.floor(i / 8);
  return row; // palette index = row number
});

const gradientPalette = [
  '#000000', '#1a1a1a', '#333333', '#4d4d4d',
  '#666666', '#808080', '#999999', '#b3b3b3',
];
```

## Exercise

1. Create a **tree sprite** (8×8) with trunk (brown) and foliage (two shades of green)
2. Design a **player character** facing right — helmet, body, legs, using 4 palette colors
3. Build an **inventory display**: render 4 different item sprites in a 2×2 grid with 2px spacing
4. Create a sprite that uses **all 8 palette slots** — maybe a tiny landscape or a colorful gem

## Quick Reference

| Component | Props | Notes |
|-----------|-------|-------|
| `<sprite>` | `x`, `y`, `data`, `palette` | Renders data array as pixels using palette colors |

| Concept | Detail |
|---------|--------|
| Data format | Flat array, left-to-right, top-to-bottom |
| Palette index 0 | Typically `'transparent'` |
| 8×8 sprite | 64 elements in the data array |
| 16×16 sprite | 256 elements in the data array |
| Palette | Array of color strings: `['transparent', '#ff0000', ...]` |
| Reuse | Wrap in React components with props for position/color |

---

Next: Those sprites are static. Mika wants them to *move*. Time for animation.

[← Chapter 1: Pixels & Shapes](chapter-01-pixels-shapes.md) | [Chapter 3: Animation →](chapter-03-animation.md)
