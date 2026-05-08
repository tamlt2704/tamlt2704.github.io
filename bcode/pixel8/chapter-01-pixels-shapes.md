# Chapter 1: Pixels & Shapes — "Draw Without Drawing"

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Sprites →](chapter-02-sprites.md)

---

## Mika's Challenge

Mika texts you a photo of graph paper covered in colored squares:

> "Draw me a house. A tree. A sun. Using only rectangles, circles, and individual pixels. No sprite data yet — just primitives. I want to see if you can *think* in pixels before we get fancy."

She adds:

> "Remember: at 64×64, a 'house' is maybe 12×10 pixels. A tree is a green circle on a brown stick. The sun is a yellow circle in the corner. Simple. Iconic. Readable."

## The Three Primitives

Pixel8 gives you three shape primitives inside any `<Stage>`:

### `<pixel>` — A Single Dot

```jsx
<pixel x={10} y={5} color="#ffffff" />
```

One pixel. One color. The atomic unit of pixel art. Use it for stars, sparkles, detail work, and single-pixel highlights.

### `<rect>` — A Rectangle

```jsx
<rect x={20} y={30} width={10} height={8} color="#e94560" />
```

Filled rectangle. No border, no radius — just solid color. Use it for buildings, ground, walls, UI boxes, and any blocky shape.

### `<circ>` — A Circle

```jsx
<circ x={50} y={12} radius={6} color="#ffd700" />
```

Filled circle centered at (x, y). At low resolution, circles become charmingly chunky — a radius-3 circle is only ~28 pixels. Use it for the sun, heads, coins, bubbles.

## Coordinate System

```
(0,0) ─────────────────── (63,0)
  │                           │
  │     x increases →         │
  │     y increases ↓         │
  │                           │
(0,63) ────────────────── (63,63)
```

- Origin (0,0) is the **top-left** corner
- x increases rightward
- y increases downward
- At 64×64, valid coordinates are 0–63

## Building a Scene: The Pixel House

Let's draw Mika's house scene:

```jsx
import React from 'react';
import { Stage } from 'pixel8';

const PixelHouse = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#87ceeb">
    {/* Sun */}
    <circ x={54} y={10} radius={5} color="#ffd700" />

    {/* Ground */}
    <rect x={0} y={50} width={64} height={14} color="#228b22" />

    {/* House body */}
    <rect x={20} y={35} width={16} height={15} color="#8b4513" />

    {/* Roof (triangle approximation with stacked rects) */}
    <rect x={18} y={33} width={20} height={2} color="#a0522d" />
    <rect x={20} y={31} width={16} height={2} color="#a0522d" />
    <rect x={22} y={29} width={12} height={2} color="#a0522d" />
    <rect x={24} y={27} width={8} height={2} color="#a0522d" />
    <rect x={26} y={25} width={4} height={2} color="#a0522d" />

    {/* Door */}
    <rect x={26} y={42} width={4} height={8} color="#4a2800" />

    {/* Window */}
    <rect x={22} y={38} width={3} height={3} color="#add8e6" />

    {/* Tree trunk */}
    <rect x={8} y={42} width={2} height={8} color="#4a2800" />

    {/* Tree foliage */}
    <circ x={9} y={39} radius={5} color="#006400" />

    {/* Chimney smoke (individual pixels) */}
    <pixel x={33} y={22} color="#cccccc" />
    <pixel x={34} y={20} color="#aaaaaa" />
    <pixel x={33} y={18} color="#888888" />
  </Stage>
);

export default PixelHouse;
```

### What You Should See

A charming pixel scene: blue sky, yellow sun in the top-right, green ground along the bottom, a brown house with a triangular roof (built from stacked rectangles), a door, a window, a tree with a round canopy, and three wisps of smoke rising from the chimney.

## Colors in Pixel8

Colors are hex strings. No named colors, no RGB objects — just strings:

```jsx
// Full hex
color="#ff0000"    // red
color="#00ff00"    // green
color="#0000ff"    // blue

// Short hex
color="#fff"       // white
color="#000"       // black

// With alpha (if supported)
color="#ff000080"  // semi-transparent red
```

### A Useful Starter Palette

```jsx
const colors = {
  black:     '#1a1a2e',
  darkBlue:  '#16213e',
  navy:      '#0f3460',
  crimson:   '#e94560',
  white:     '#ffffff',
  gold:      '#ffd700',
  green:     '#228b22',
  sky:       '#87ceeb',
  brown:     '#8b4513',
  gray:      '#888888',
};
```

## Layering: Painter's Algorithm

Pixel8 renders components in order — later elements draw on top of earlier ones. This is the **painter's algorithm**: draw back-to-front.

```jsx
{/* This rect is behind... */}
<rect x={10} y={10} width={20} height={20} color="#ff0000" />

{/* ...this rect is in front */}
<rect x={15} y={15} width={20} height={20} color="#0000ff" />
```

The blue rect partially covers the red one. Order matters.

## Pattern: Pixel Art Checkerboard

```jsx
const Checkerboard = () => {
  const pixels = [];
  for (let y = 0; y < 8; y++) {
    for (let x = 0; x < 8; x++) {
      const isLight = (x + y) % 2 === 0;
      pixels.push(
        <pixel
          key={`${x}-${y}`}
          x={x + 28}
          y={y + 28}
          color={isLight ? '#ffffff' : '#333333'}
        />
      );
    }
  }
  return pixels;
};
```

You can generate primitives programmatically — it's just React. Map over arrays, use loops, compute positions with math.

## Pattern: Starfield Background

```jsx
const Starfield = () => {
  // Deterministic "random" stars using a simple hash
  const stars = [];
  for (let i = 0; i < 30; i++) {
    const x = (i * 17 + 7) % 64;
    const y = (i * 31 + 13) % 64;
    const brightness = i % 3 === 0 ? '#ffffff' : '#888888';
    stars.push(<pixel key={i} x={x} y={y} color={brightness} />);
  }
  return stars;
};

const SpaceScene = () => (
  <Stage width={64} height={64} scale={8} fps={0} background="#0a0a1a">
    <Starfield />
    <circ x={45} y={20} radius={8} color="#4a4a8a" />
    <circ x={47} y={18} radius={3} color="#6a6aaa" />
  </Stage>
);
```

## Tips: Thinking in Pixels

1. **Sketch on graph paper first** — or use a spreadsheet. Each cell = one pixel.
2. **Triangles don't exist** — approximate with stacked rectangles (1px shorter each row).
3. **Outlines = multiple rects** — draw a larger rect behind a smaller one for a border effect.
4. **Symmetry reads well** — center your subjects. Odd widths (3, 5, 7) have a natural center pixel.
5. **Contrast is king** — at low resolution, shapes need strong color contrast to be readable.

## Anti-Pattern: Too Much Detail

```jsx
// ❌ Don't try to draw a detailed face at 64×64
// You have maybe 8×8 pixels for a head — that's 64 pixels total

// ✅ Instead, suggest features with minimal pixels:
// Two eyes = 2 pixels. Mouth = 3 pixels. Done.
<pixel x={30} y={20} color="#000" />  {/* left eye */}
<pixel x={34} y={20} color="#000" />  {/* right eye */}
<rect x={30} y={23} width={5} height={1} color="#000" />  {/* mouth */}
```

## Exercise

1. Draw a **pixel art flag** — any country or fictional. Use only `<rect>` components.
2. Create a **night sky** with a crescent moon (hint: two overlapping circles — one moon-colored, one background-colored).
3. Build a **simple face** using the minimal approach: circle for head, pixels for eyes, rect for mouth.
4. Make a **rainbow** using 7 stacked `<rect>` components, each 1px tall, in ROYGBIV colors.

## Quick Reference

| Primitive | Props | Notes |
|-----------|-------|-------|
| `<pixel>` | `x`, `y`, `color` | Single pixel at exact position |
| `<rect>` | `x`, `y`, `width`, `height`, `color` | Filled rectangle, top-left origin |
| `<circ>` | `x`, `y`, `radius`, `color` | Filled circle, centered at (x,y) |

| Concept | Rule |
|---------|------|
| Coordinates | (0,0) = top-left, x→ right, y→ down |
| Colors | Hex strings only: `"#rrggbb"` or `"#rgb"` |
| Layering | Later in JSX = drawn on top |
| No imports | Primitives work inside `<Stage>` without importing |

---

Next: Mika wants characters. Real pixel art. That means sprite data arrays — encoding art as numbers.

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Sprites →](chapter-02-sprites.md)
