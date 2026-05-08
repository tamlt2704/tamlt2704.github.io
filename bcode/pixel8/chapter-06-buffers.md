# Chapter 6: Buffers — "Every Pixel Under Your Control"

[← Chapter 5: Game Loop](chapter-05-game-loop.md) | [Chapter 7: Text & UI →](chapter-07-text-ui.md)

---

## Mika's Challenge

Mika leans back and says:

> "Sprites and shapes are great for objects. But what about *backgrounds*? Starfields. Water. Fire. Noise. You can't draw those with individual `<pixel>` components — you'd need thousands of them. That's where buffers come in."

She pulls up a demo of an old DOS fire effect:

> "This is raw pixel manipulation. You write color values directly into a flat array — like painting into video memory. It's how the demoscene did everything. One array. Every pixel. Total control."

## The `<buffer>` Component

The `<buffer>` component renders a raw pixel array directly to the canvas:

```jsx
<buffer x={0} y={0} data={pixelData} width={64} height={64} />
```

The `data` array contains color values for every pixel in the buffer, read left-to-right, top-to-bottom — similar to ImageData in the Canvas API.

## Buffer Data Format

Each pixel in the buffer is represented by its color value. The exact format depends on the implementation, but conceptually:

```jsx
// A 4×4 buffer with direct color values
// Each element = one pixel's color (as a palette index or direct value)
const data = new Array(4 * 4).fill(0);

// Set pixel at (2, 1) — index = y * width + x
data[1 * 4 + 2] = 1; // row 1, column 2
```

The index formula: `index = y * width + x`

## Pattern: Gradient Background

```jsx
import React, { useMemo } from 'react';
import { Stage } from 'pixel8';

const GradientBackground = () => {
  const data = useMemo(() => {
    const width = 64;
    const height = 64;
    const buf = new Array(width * height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        // Map y position to palette index (0-7)
        buf[y * width + x] = Math.floor((y / height) * 8);
      }
    }
    return buf;
  }, []);

  const palette = [
    '#000033', '#000066', '#000099', '#0000cc',
    '#0033ff', '#0066ff', '#0099ff', '#00ccff',
  ];

  return (
    <Stage width={64} height={64} scale={8} fps={0} background="#000000">
      <buffer x={0} y={0} data={data} width={64} height={64} palette={palette} />
    </Stage>
  );
};
```

### What You Should See

A smooth vertical gradient from dark navy at the top to bright cyan at the bottom — a sky or ocean background.

## Pattern: Noise Texture

```jsx
const NoiseTexture = () => {
  const data = useMemo(() => {
    const width = 64;
    const height = 64;
    const buf = new Array(width * height);

    for (let i = 0; i < buf.length; i++) {
      // Random palette index 0-3
      buf[i] = Math.floor(Math.random() * 4);
    }
    return buf;
  }, []);

  const palette = ['#1a1a2e', '#2a2a3e', '#3a3a4e', '#4a4a5e'];

  return (
    <Stage width={64} height={64} scale={8} fps={0} background="#000000">
      <buffer x={0} y={0} data={data} width={64} height={64} palette={palette} />
    </Stage>
  );
};
```

A subtle noise pattern — great for cave walls, stone textures, or TV static.

## Pattern: Animated Fire Effect

The classic demoscene fire: each pixel's heat is the average of its neighbors below, minus a cooling factor.

```jsx
import React, { useState, useRef } from 'react';
import { Stage } from 'pixel8';
import { useGameLoop } from './hooks/useGameLoop';

const FireEffect = () => {
  const width = 64;
  const height = 64;
  const bufferRef = useRef(new Array(width * height).fill(0));
  const [data, setData] = useState(bufferRef.current);

  useGameLoop(() => {
    const buf = [...bufferRef.current];

    // Seed the bottom row with random heat
    for (let x = 0; x < width; x++) {
      buf[(height - 1) * width + x] = Math.random() > 0.4 ? 7 : 0;
    }

    // Propagate heat upward
    for (let y = 0; y < height - 1; y++) {
      for (let x = 0; x < width; x++) {
        const below = buf[(y + 1) * width + x];
        const belowLeft = buf[(y + 1) * width + Math.max(0, x - 1)];
        const belowRight = buf[(y + 1) * width + Math.min(width - 1, x + 1)];
        const twoBelow = y + 2 < height ? buf[(y + 2) * width + x] : 0;

        const avg = (below + belowLeft + belowRight + twoBelow) / 4;
        buf[y * width + x] = Math.max(0, Math.floor(avg - 0.2));
      }
    }

    bufferRef.current = buf;
    setData(buf);
  });

  const firePalette = [
    '#000000', '#1a0000', '#330000', '#660000',
    '#993300', '#cc6600', '#ff9900', '#ffcc00',
  ];

  return (
    <Stage width={64} height={64} scale={8} fps={30} background="#000000">
      <buffer x={0} y={0} data={data} width={width} height={height} palette={firePalette} />
    </Stage>
  );
};
```

### What You Should See

Flames rising from the bottom of the screen — dark red at the base, orange in the middle, yellow at the tips. The classic DOS fire effect, running in React.

## Pattern: Scrolling Starfield

```jsx
const ScrollingStars = () => {
  const width = 64;
  const height = 64;
  const starsRef = useRef(
    Array.from({ length: 40 }, () => ({
      x: Math.floor(Math.random() * width),
      y: Math.floor(Math.random() * height),
      speed: 1 + Math.floor(Math.random() * 3),
    }))
  );
  const [data, setData] = useState(new Array(width * height).fill(0));

  useGameLoop((dt) => {
    const buf = new Array(width * height).fill(0);
    const stars = starsRef.current;

    for (const star of stars) {
      star.y = (star.y + star.speed) % height;
      const idx = Math.floor(star.y) * width + Math.floor(star.x);
      buf[idx] = star.speed; // brighter = faster
    }

    starsRef.current = stars;
    setData(buf);
  });

  const starPalette = ['#0a0a1a', '#555555', '#aaaaaa', '#ffffff'];

  return (
    <Stage width={64} height={64} scale={8} fps={30} background="#0a0a1a">
      <buffer x={0} y={0} data={data} width={width} height={height} palette={starPalette} />
    </Stage>
  );
};
```

Stars scroll downward at different speeds — a parallax starfield for a space game.

## Pattern: Checkerboard Floor (Perspective)

```jsx
const PerspectiveFloor = () => {
  const data = useMemo(() => {
    const width = 64;
    const height = 32;
    const buf = new Array(width * height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        // Fake perspective: tile size increases with y
        const tileSize = Math.max(2, Math.floor(y / 4));
        const tileX = Math.floor(x / tileSize);
        const tileY = Math.floor(y / tileSize);
        buf[y * width + x] = (tileX + tileY) % 2;
      }
    }
    return buf;
  }, []);

  return (
    <Stage width={64} height={64} scale={8} fps={0} background="#87ceeb">
      <buffer x={0} y={32} data={data} width={64} height={32} palette={['#228b22', '#1a6b1a']} />
    </Stage>
  );
};
```

## Performance: useMemo and useRef

Buffers can be expensive — 64×64 = 4,096 pixels to compute every frame. Optimize:

```jsx
// ✅ Static buffers: compute once with useMemo
const staticBg = useMemo(() => generateNoise(64, 64), []);

// ✅ Animated buffers: mutate with useRef, copy to state for render
const bufRef = useRef(new Array(4096).fill(0));
useGameLoop(() => {
  updateBuffer(bufRef.current); // mutate in place
  setData([...bufRef.current]); // trigger render with copy
});

// ❌ Don't allocate new arrays every frame without reason
useGameLoop(() => {
  const buf = new Array(4096); // allocation every frame = GC pressure
});
```

## Tips: Buffer Design

1. **Use palettes** — store indices (0-7) not full colors. Cheaper to compute, easy to restyle.
2. **Smaller buffers for effects** — a 32×32 fire effect at the bottom is half the work of 64×64.
3. **Layer buffers behind sprites** — render the buffer first, sprites on top.
4. **Pre-compute static parts** — only animate what changes.
5. **Integer math** — `Math.floor` is your friend. No sub-pixel buffers.

## Exercise

1. Create a **water ripple** effect — sine wave distortion that animates over time
2. Build a **plasma** pattern — combine two sine waves at different frequencies for a colorful animated texture
3. Make a **rain** effect — vertical streaks that fall and reset, with random spacing
4. Generate a **terrain heightmap** — use the buffer to visualize elevation with a green-to-brown palette

## Quick Reference

```jsx
// Static buffer
<buffer x={0} y={0} data={pixelArray} width={W} height={H} palette={colors} />

// Index formula
index = y * width + x

// Generate buffer
const buf = new Array(width * height);
for (let y = 0; y < height; y++) {
  for (let x = 0; x < width; x++) {
    buf[y * width + x] = computeColor(x, y);
  }
}
```

| Concept | Detail |
|---------|--------|
| Data size | `width × height` elements |
| Index | `y * width + x` |
| Values | Palette indices (integers) |
| Static | `useMemo(() => generate(), [])` |
| Animated | `useRef` + copy to state each frame |
| Performance | Smaller buffers, integer math, pre-compute |

---

Next: Your game needs a score display, menus, and game-over text. Time for pixel fonts.

[← Chapter 5: Game Loop](chapter-05-game-loop.md) | [Chapter 7: Text & UI →](chapter-07-text-ui.md)
