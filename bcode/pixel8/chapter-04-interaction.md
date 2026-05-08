# Chapter 4: Interaction — "Let the Player In"

[← Chapter 3: Animation](chapter-03-animation.md) | [Chapter 5: Game Loop →](chapter-05-game-loop.md)

---

## Mika's Challenge

Mika watches your animated coin spin and nods:

> "Cool. But I can't *do* anything. A game isn't a screensaver. I need to move something. Press a key, see a pixel respond. That's the moment it becomes interactive — the moment it becomes a *game*."

She holds up her phone:

> "Arrow keys to move. Click to place. That's all you need for now. React already knows how to handle events and state. Use what you know."

## The Key Insight: React State Drives Pixel8

Pixel8 is a React renderer. That means:
- Component props control what's drawn
- React state controls those props
- Event handlers update state
- State changes trigger re-renders
- Re-renders update the canvas

It's the same React data flow you already know — just rendering to pixels instead of DOM.

## Keyboard Input: Moving a Sprite

```jsx
import React, { useState, useEffect } from 'react';
import { Stage } from 'pixel8';

const knight = [
  0,0,1,1,1,0,0,0,
  0,1,2,2,2,1,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,0,1,0,0,0,
  0,0,1,0,1,0,0,0,
  0,0,0,0,0,0,0,0,
];
const knightPalette = ['transparent', '#c0c0c0', '#333333'];

const Game = () => {
  const [pos, setPos] = useState({ x: 28, y: 28 });

  useEffect(() => {
    const handleKey = (e) => {
      setPos(prev => {
        switch (e.key) {
          case 'ArrowUp':    return { ...prev, y: Math.max(0, prev.y - 1) };
          case 'ArrowDown':  return { ...prev, y: Math.min(56, prev.y + 1) };
          case 'ArrowLeft':  return { ...prev, x: Math.max(0, prev.x - 1) };
          case 'ArrowRight': return { ...prev, x: Math.min(56, prev.x + 1) };
          default: return prev;
        }
      });
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
      <sprite x={pos.x} y={pos.y} data={knight} palette={knightPalette} />
    </Stage>
  );
};

export default Game;
```

### What You Should See

A knight sprite that moves one pixel per arrow key press. The `Math.max`/`Math.min` calls keep it within bounds.

## Continuous Movement: Holding Keys

One pixel per keypress feels choppy. For smooth movement, track which keys are *held*:

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { Stage } from 'pixel8';

const SmoothMovement = () => {
  const [pos, setPos] = useState({ x: 28, y: 28 });
  const keys = useRef(new Set());

  useEffect(() => {
    const down = (e) => keys.current.add(e.key);
    const up = (e) => keys.current.delete(e.key);

    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => {
      window.removeEventListener('keydown', down);
      window.removeEventListener('keyup', up);
    };
  }, []);

  useEffect(() => {
    const loop = setInterval(() => {
      setPos(prev => {
        let { x, y } = prev;
        if (keys.current.has('ArrowUp'))    y = Math.max(0, y - 1);
        if (keys.current.has('ArrowDown'))  y = Math.min(56, y + 1);
        if (keys.current.has('ArrowLeft'))  x = Math.max(0, x - 1);
        if (keys.current.has('ArrowRight')) x = Math.min(56, x + 1);
        return { x, y };
      });
    }, 50); // 20 updates per second

    return () => clearInterval(loop);
  }, []);

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
      <sprite x={pos.x} y={pos.y} data={knight} palette={knightPalette} />
    </Stage>
  );
};
```

Now holding an arrow key moves the sprite continuously at a steady pace.

## Custom Hook: useKeyboard

Extract the pattern into a reusable hook:

```jsx
// hooks/useKeyboard.js
import { useState, useEffect, useRef } from 'react';

export function useKeyboard() {
  const keys = useRef(new Set());

  useEffect(() => {
    const down = (e) => {
      e.preventDefault();
      keys.current.add(e.key);
    };
    const up = (e) => keys.current.delete(e.key);

    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => {
      window.removeEventListener('keydown', down);
      window.removeEventListener('keyup', up);
    };
  }, []);

  return {
    isDown: (key) => keys.current.has(key),
    pressed: keys.current,
  };
}
```

Usage:

```jsx
const Game = () => {
  const { isDown } = useKeyboard();
  const [pos, setPos] = useState({ x: 28, y: 28 });

  // Update position based on held keys (in game loop — see Chapter 5)
  // ...
};
```

## Mouse/Touch Input: Click to Place

```jsx
import React, { useState } from 'react';
import { Stage } from 'pixel8';

const PixelPainter = () => {
  const [pixels, setPixels] = useState([]);

  const handleClick = (e) => {
    const canvas = e.target;
    const rect = canvas.getBoundingClientRect();
    const scale = 8;

    // Convert screen coordinates to pixel coordinates
    const x = Math.floor((e.clientX - rect.left) / scale);
    const y = Math.floor((e.clientY - rect.top) / scale);

    setPixels(prev => [...prev, { x, y, color: '#e94560' }]);
  };

  return (
    <div onClick={handleClick}>
      <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
        {pixels.map((p, i) => (
          <pixel key={i} x={p.x} y={p.y} color={p.color} />
        ))}
      </Stage>
    </div>
  );
};
```

### What You Should See

Click anywhere on the canvas and a red pixel appears at that position. Click more — you're painting with pixels.

## Coordinate Conversion

The critical math for mouse input: convert screen pixels to virtual pixels.

```jsx
// Screen position → Pixel8 coordinate
const toPixelCoord = (screenX, screenY, canvasRect, scale) => ({
  x: Math.floor((screenX - canvasRect.left) / scale),
  y: Math.floor((screenY - canvasRect.top) / scale),
});
```

If your Stage is 64×64 at scale 8, the canvas is 512×512 on screen. A click at screen position (256, 256) maps to pixel (32, 32).

## Pattern: Color Picker + Painter

```jsx
const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#ffffff'];

const PaintApp = () => {
  const [pixels, setPixels] = useState([]);
  const [currentColor, setCurrentColor] = useState('#ffffff');

  useEffect(() => {
    const handleKey = (e) => {
      const idx = parseInt(e.key) - 1;
      if (idx >= 0 && idx < colors.length) {
        setCurrentColor(colors[idx]);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const handleClick = (e) => {
    const rect = e.target.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / 8);
    const y = Math.floor((e.clientY - rect.top) / 8);
    setPixels(prev => [...prev, { x, y, color: currentColor }]);
  };

  return (
    <div onClick={handleClick}>
      <Stage width={64} height={64} scale={8} fps={0} background="#1a1a2e">
        {pixels.map((p, i) => (
          <pixel key={i} x={p.x} y={p.y} color={p.color} />
        ))}
        {/* Color indicator */}
        <rect x={0} y={0} width={3} height={3} color={currentColor} />
      </Stage>
    </div>
  );
};
```

Press 1-6 to switch colors, click to paint. A tiny square in the corner shows the active color.

## Pattern: Click Detection on Sprites

Check if a click lands within a sprite's bounding box:

```jsx
const isClickOnSprite = (clickX, clickY, spriteX, spriteY, spriteSize = 8) => {
  return (
    clickX >= spriteX &&
    clickX < spriteX + spriteSize &&
    clickY >= spriteY &&
    clickY < spriteY + spriteSize
  );
};

// In your click handler:
const handleClick = (e) => {
  const rect = e.target.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / 8);
  const y = Math.floor((e.clientY - rect.top) / 8);

  if (isClickOnSprite(x, y, coinX, coinY)) {
    setScore(s => s + 1);
    spawnNewCoin();
  }
};
```

## Tips: Input at Low Resolution

1. **1 pixel = 1 unit of movement** — don't move in sub-pixel amounts
2. **Bound your movement** — always clamp to canvas bounds (0 to width - spriteSize)
3. **Debounce if needed** — at 64×64, moving too fast makes sprites teleport
4. **Visual feedback** — change sprite color or flash on input to confirm the player's action registered
5. **Touch = click** — for mobile, `touchstart` events work the same way with coordinate conversion

## Exercise

1. Add **WASD controls** alongside arrow keys in the keyboard handler
2. Create a **pixel eraser** — right-click removes the pixel at that position
3. Build a **sprite selector** — click on one of 3 sprites to "pick it up", then click to place it
4. Implement **boundary wrapping** — when the sprite goes off the right edge, it appears on the left

## Quick Reference

```jsx
// Keyboard: track held keys
useEffect(() => {
  const down = (e) => keys.current.add(e.key);
  const up = (e) => keys.current.delete(e.key);
  window.addEventListener('keydown', down);
  window.addEventListener('keyup', up);
  return () => { /* cleanup */ };
}, []);

// Mouse: convert to pixel coords
const x = Math.floor((e.clientX - rect.left) / scale);
const y = Math.floor((e.clientY - rect.top) / scale);

// Bounds clamping
Math.max(0, Math.min(maxX, newX))
```

| Pattern | Use |
|---------|-----|
| `keydown` + state | Single press actions (jump, shoot) |
| `keydown`/`keyup` + Set | Held keys for continuous movement |
| Click + coord conversion | Placing pixels, selecting sprites |
| Bounding box check | Click detection on sprites |

---

Next: We have input, but we're using `setInterval` for movement. That's fragile. Time for a proper game loop with the `fps` prop.

[← Chapter 3: Animation](chapter-03-animation.md) | [Chapter 5: Game Loop →](chapter-05-game-loop.md)
