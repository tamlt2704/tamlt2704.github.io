# Chapter 3: Graphics & Shapes — "Draw Health Bars and Borders"

[← Chapter 2: Containers & Layout](chapter-02-containers-layout.md) | [Chapter 4: Animation & Tick →](chapter-04-animation-tick.md)

---

## The Crisis

Kai refuses to draw a health bar sprite. "It's a rectangle. A green rectangle that gets shorter. Just draw it in code."

Fair point. You don't need a PNG for every UI element. PixiJS has a `Graphics` object for drawing shapes programmatically — rectangles, circles, lines, polygons. In @pixi/react, it's the `<Graphics>` component.

## The Graphics Component

Unlike `<Sprite>` which displays an image, `<Graphics>` draws shapes using a callback function:

```jsx
import { Graphics } from '@pixi/react';
import { useCallback } from 'react';

function HealthBar() {
  const draw = useCallback((g) => {
    g.clear();

    // Background (dark red)
    g.beginFill(0x3d0000);
    g.drawRect(0, 0, 100, 12);
    g.endFill();

    // Foreground (green, represents current health)
    g.beginFill(0x44ff44);
    g.drawRect(0, 0, 75, 12);  // 75% health
    g.endFill();
  }, []);

  return <Graphics draw={draw} x={10} y={10} />;
}
```

The `draw` prop receives a `PIXI.Graphics` instance. You call drawing methods on it — same API as the raw PixiJS Graphics class.

## The Draw Callback Pattern

**Critical:** The `draw` callback runs every time the component re-renders. If you don't wrap it in `useCallback`, it creates a new function every render, which redraws the graphics every frame. Wasteful.

```jsx
// ❌ Bad — redraws every render
function HealthBar() {
  return <Graphics draw={(g) => { /* ... */ }} />;
}

// ✅ Good — stable reference, only redraws when deps change
function HealthBar({ health, maxHealth }) {
  const draw = useCallback((g) => {
    g.clear();
    const width = (health / maxHealth) * 100;
    g.beginFill(0x3d0000);
    g.drawRect(0, 0, 100, 12);
    g.endFill();
    g.beginFill(0x44ff44);
    g.drawRect(0, 0, width, 12);
    g.endFill();
  }, [health, maxHealth]);  // only redraws when health changes

  return <Graphics draw={draw} x={10} y={10} />;
}
```

When `health` changes, the callback reference changes, and the Graphics redraws. When it doesn't change, no redraw. React optimization at work.

## Drawing Primitives

### Rectangles

```jsx
const draw = useCallback((g) => {
  g.clear();
  g.beginFill(0xe74c3c);       // fill color
  g.drawRect(0, 0, 64, 32);   // x, y, width, height
  g.endFill();
}, []);
```

### Rounded Rectangles

```jsx
g.beginFill(0x3498db);
g.drawRoundedRect(0, 0, 100, 40, 8);  // x, y, w, h, radius
g.endFill();
```

### Circles

```jsx
g.beginFill(0xf1c40f);
g.drawCircle(32, 32, 24);  // centerX, centerY, radius
g.endFill();
```

### Lines

```jsx
g.lineStyle(2, 0xffffff, 1);  // width, color, alpha
g.moveTo(0, 0);
g.lineTo(100, 50);
```

### Polygons

```jsx
g.beginFill(0x9b59b6);
g.drawPolygon([
  0, 0,      // point 1
  50, -20,   // point 2
  100, 0,    // point 3
  80, 40,    // point 4
  20, 40,    // point 5
]);
g.endFill();
```

### Outlines (Stroke Only)

```jsx
g.lineStyle(2, 0xffffff, 1);  // 2px white border
g.beginFill(0, 0);            // transparent fill (color, alpha=0)
g.drawRect(0, 0, 64, 64);
g.endFill();
```

## Building the Health Bar

Here's a proper health bar component with border, background, and dynamic fill:

```jsx
import { Container, Graphics } from '@pixi/react';
import { useCallback } from 'react';

function HealthBar({ x, y, health, maxHealth }) {
  const barWidth = 80;
  const barHeight = 8;
  const fillWidth = (health / maxHealth) * barWidth;

  // Color changes based on health percentage
  const pct = health / maxHealth;
  const color = pct > 0.5 ? 0x44ff44 : pct > 0.25 ? 0xffaa00 : 0xff4444;

  const draw = useCallback((g) => {
    g.clear();

    // Border
    g.lineStyle(1, 0xffffff, 0.8);
    g.drawRect(-1, -1, barWidth + 2, barHeight + 2);

    // Background
    g.lineStyle(0);
    g.beginFill(0x1a1a1a);
    g.drawRect(0, 0, barWidth, barHeight);
    g.endFill();

    // Health fill
    g.beginFill(color);
    g.drawRect(0, 0, fillWidth, barHeight);
    g.endFill();
  }, [fillWidth, color]);

  return <Graphics draw={draw} x={x} y={y} />;
}

// Usage
<HealthBar x={10} y={10} health={6} maxHealth={10} />
```

## Debug Overlays

During development, it's useful to draw collision boxes and hit areas. Graphics is perfect for this:

```jsx
function DebugBox({ x, y, width, height, visible = true }) {
  const draw = useCallback((g) => {
    g.clear();
    g.lineStyle(1, 0x00ff00, 0.5);  // green, semi-transparent
    g.drawRect(0, 0, width, height);
  }, [width, height]);

  if (!visible) return null;
  return <Graphics draw={draw} x={x} y={y} />;
}
```

Toggle debug overlays with a state flag:

```jsx
function Game() {
  const [debug, setDebug] = useState(false);

  return (
    <>
      <Sprite image="./sprites/knight.png" x={100} y={100} scale={3} />
      <DebugBox x={100} y={100} width={48} height={48} visible={debug} />
    </>
  );
}
```

## Borders and Panels

A dialog box border for the dungeon UI:

```jsx
function Panel({ x, y, width, height }) {
  const draw = useCallback((g) => {
    g.clear();

    // Dark background
    g.beginFill(0x1a1a2e, 0.9);
    g.drawRect(0, 0, width, height);
    g.endFill();

    // Pixel-style border (double line)
    g.lineStyle(2, 0x8b7355);  // outer border (brown)
    g.drawRect(0, 0, width, height);
    g.lineStyle(1, 0xd4a574);  // inner border (light brown)
    g.drawRect(3, 3, width - 6, height - 6);
  }, [width, height]);

  return <Graphics draw={draw} x={x} y={y} />;
}
```

## Combining Graphics with Sprites and Text

```jsx
import { Container, Graphics, Sprite, Text } from '@pixi/react';
import * as PIXI from 'pixi.js';

function HUD({ health, maxHealth, score }) {
  const scoreStyle = new PIXI.TextStyle({
    fontFamily: 'monospace',
    fontSize: 14,
    fill: 0xffffff,
  });

  return (
    <Container x={10} y={10}>
      {/* Health bar */}
      <HealthBar x={0} y={0} health={health} maxHealth={maxHealth} />

      {/* Heart icon next to health bar */}
      <Sprite image="./sprites/heart.png" x={-14} y={-2} scale={1.5} />

      {/* Score */}
      <Text text={`Score: ${score}`} style={scoreStyle} x={0} y={16} />
    </Container>
  );
}
```

## Performance: useMemo for Complex Draws

If your draw callback does heavy computation (calculating polygon points, generating patterns), memoize the data:

```jsx
function MiniMap({ tiles }) {
  // Memoize the tile data processing
  const tileColors = useMemo(() => {
    return tiles.flat().map(tile => {
      if (tile === 1) return 0x666666;  // wall
      if (tile === 2) return 0x3d3d00;  // floor
      return 0x000000;                   // void
    });
  }, [tiles]);

  const draw = useCallback((g) => {
    g.clear();
    const size = 3;  // 3px per tile on minimap
    tileColors.forEach((color, i) => {
      const col = i % tiles[0].length;
      const row = Math.floor(i / tiles[0].length);
      g.beginFill(color);
      g.drawRect(col * size, row * size, size, size);
      g.endFill();
    });
  }, [tileColors, tiles]);

  return <Graphics draw={draw} x={380} y={10} />;
}
```

## Common Patterns

### XP Bar (with gradient feel)

```jsx
function XPBar({ xp, maxXP, x, y }) {
  const draw = useCallback((g) => {
    g.clear();
    const width = 120;
    const height = 6;
    const fill = (xp / maxXP) * width;

    g.beginFill(0x1a1a1a);
    g.drawRect(0, 0, width, height);
    g.endFill();

    g.beginFill(0x6644ff);
    g.drawRect(0, 0, fill, height);
    g.endFill();
  }, [xp, maxXP]);

  return <Graphics draw={draw} x={x} y={y} />;
}
```

### Selection Highlight

```jsx
function SelectionBox({ x, y, width, height }) {
  const draw = useCallback((g) => {
    g.clear();
    g.lineStyle(1, 0xffff00, 0.8);
    g.drawRect(0, 0, width, height);
    // Corner dots
    g.beginFill(0xffff00);
    g.drawCircle(0, 0, 2);
    g.drawCircle(width, 0, 2);
    g.drawCircle(0, height, 2);
    g.drawCircle(width, height, 2);
    g.endFill();
  }, [width, height]);

  return <Graphics draw={draw} x={x} y={y} />;
}
```

## Verify

- [ ] `<Graphics draw={callback}>` renders shapes
- [ ] `useCallback` prevents unnecessary redraws
- [ ] Health bar updates when `health` prop changes
- [ ] Rectangles, circles, lines, and polygons all work
- [ ] Graphics combines with Sprites and Text in the same Container

Kai says: "The health bar looks great. But everything is still frozen. Can you make the torches flicker? Or the slime bounce?"

Static scenes are boring. Time to make things move.

That's Chapter 4.

---

[← Chapter 2: Containers & Layout](chapter-02-containers-layout.md) | [Chapter 4: Animation & Tick →](chapter-04-animation-tick.md)
