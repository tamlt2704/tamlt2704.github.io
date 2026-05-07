# Chapter 1: First Sprite — "Put Kai's Art on Screen"

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Containers & Layout →](chapter-02-containers-layout.md)

---

## The Crisis

Kai sends `knight.png` — a 16×16 pixel knight on a transparent background. "Put it on screen. Make it big and crispy. No blur."

You drop it in `public/sprites/knight.png`. In normal React, you'd write `<img src="/sprites/knight.png" />`. But you're inside a `<Stage>` now. DOM elements don't exist here.

## The Sprite Component

In @pixi/react, images are rendered with `<Sprite>`:

```jsx
import { Stage, Sprite } from '@pixi/react';

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e, antialias: false }}
    >
      <Sprite image="./sprites/knight.png" x={240} y={160} />
    </Stage>
  );
}
```

The `image` prop takes a URL path (relative to `public/`). The sprite loads asynchronously — PixiJS handles the texture loading for you.

## The Problem: Blurry Pixels

You refresh the browser. The knight is there... but it's blurry. A 16×16 image rendered at 16×16 pixels on a WebGL canvas uses bilinear filtering by default. That smooths the edges. For photo-realistic games, great. For pixel art, terrible.

Kai looks over your shoulder: "That's not crispy. Fix it."

## The Fix: SCALE_MODES.NEAREST

PixiJS textures default to `LINEAR` scaling (smooth interpolation). For pixel art, you need `NEAREST` (nearest-neighbor — no interpolation, hard pixel edges).

Set it globally before anything renders:

```jsx
import { Stage, Sprite } from '@pixi/react';
import * as PIXI from 'pixi.js';

// Set default scale mode for ALL textures
PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e, antialias: false }}
    >
      <Sprite image="./sprites/knight.png" x={240} y={160} />
    </Stage>
  );
}
```

Refresh. The knight is now sharp. Every pixel is a perfect square. Kai approves.

## Positioning: x, y, anchor

Sprites position from their **anchor point** — by default, the top-left corner (0, 0).

```jsx
<Sprite
  image="./sprites/knight.png"
  x={240}       // pixels from left edge of Stage
  y={160}       // pixels from top edge of Stage
/>
```

The coordinate system:
- (0, 0) is the **top-left** corner of the Stage
- x increases to the right
- y increases **downward** (not up — this isn't math class)

### Centering with Anchor

To position from the sprite's center instead of its top-left:

```jsx
<Sprite
  image="./sprites/knight.png"
  x={240}
  y={160}
  anchor={0.5}   // anchor at center (0.5, 0.5)
/>
```

`anchor` values:
- `0` = top-left (default)
- `0.5` = center
- `1` = bottom-right
- You can also pass an object: `anchor={{ x: 0.5, y: 1 }}` (center-bottom, useful for characters standing on ground)

## Scaling Up Pixel Art

A 16×16 sprite is tiny on a 480×320 canvas. Scale it up:

```jsx
<Sprite
  image="./sprites/knight.png"
  x={240}
  y={160}
  anchor={0.5}
  scale={3}       // 3x size → 48×48 pixels on screen
/>
```

Because we set `SCALE_MODES.NEAREST`, scaling up preserves the pixel grid. No blur. A 16×16 sprite at 3x scale looks like a 48×48 sprite with perfectly sharp pixels.

## Multiple Sprites

Kai sends more art: `slime.png`, `chest.png`, `torch.png`. All 16×16.

```jsx
import { Stage, Sprite } from '@pixi/react';
import * as PIXI from 'pixi.js';

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function Game() {
  return (
    <>
      <Sprite image="./sprites/knight.png" x={240} y={200} anchor={0.5} scale={3} />
      <Sprite image="./sprites/slime.png" x={350} y={220} anchor={0.5} scale={3} />
      <Sprite image="./sprites/chest.png" x={100} y={180} anchor={0.5} scale={3} />
      <Sprite image="./sprites/torch.png" x={50} y={80} anchor={0.5} scale={2} />
    </>
  );
}

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e, antialias: false }}
    >
      <Game />
    </Stage>
  );
}

export default App;
```

Fragments (`<>...</>`) work inside Stage just like in normal React. You can compose game elements from multiple components.

## Sprite Props Reference

| Prop | Type | Description |
|---|---|---|
| `image` | string | URL to the image file |
| `texture` | PIXI.Texture | Pre-loaded texture (alternative to `image`) |
| `x` | number | X position in pixels |
| `y` | number | Y position in pixels |
| `anchor` | number or {x, y} | Origin point (0–1) |
| `scale` | number or {x, y} | Scale multiplier |
| `rotation` | number | Rotation in radians |
| `alpha` | number | Opacity (0–1) |
| `tint` | number | Color tint (hex, e.g., `0xff0000` for red) |
| `visible` | boolean | Show/hide |
| `interactive` | boolean | Enable pointer events |

## Tinting: Recolor Without New Art

Kai only drew one slime. But you need green slimes and red slimes. Use `tint`:

```jsx
<Sprite image="./sprites/slime.png" x={300} y={200} scale={3} tint={0x44ff44} />
<Sprite image="./sprites/slime.png" x={350} y={200} scale={3} tint={0xff4444} />
```

`tint` multiplies the sprite's colors by the tint color. White pixels become the tint color. Dark pixels stay dark. One sprite asset, infinite color variants.

## Rotation

Rotation is in **radians**, not degrees:

```jsx
<Sprite
  image="./sprites/torch.png"
  x={50}
  y={80}
  rotation={Math.PI / 4}   // 45 degrees
  anchor={0.5}              // rotate around center
  scale={2}
/>
```

Rotation happens around the anchor point. If anchor is (0, 0), it rotates around the top-left corner. Set anchor to 0.5 to rotate around the center.

## Alpha: Fade Effects

```jsx
<Sprite
  image="./sprites/chest.png"
  x={100}
  y={180}
  alpha={0.5}    // 50% transparent
  scale={3}
/>
```

Useful for ghost enemies, fade-in effects, or indicating something is inactive.

## The Full Scene So Far

```jsx
import { Stage, Sprite } from '@pixi/react';
import * as PIXI from 'pixi.js';

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function DungeonScene() {
  return (
    <>
      {/* Background torches */}
      <Sprite image="./sprites/torch.png" x={32} y={48} scale={2} anchor={0.5} />
      <Sprite image="./sprites/torch.png" x={448} y={48} scale={2} anchor={0.5} />

      {/* Player */}
      <Sprite image="./sprites/knight.png" x={240} y={200} scale={3} anchor={0.5} />

      {/* Enemies */}
      <Sprite image="./sprites/slime.png" x={350} y={220} scale={3} anchor={0.5} tint={0x44ff44} />
      <Sprite image="./sprites/slime.png" x={120} y={240} scale={3} anchor={0.5} tint={0xff4444} />

      {/* Loot */}
      <Sprite image="./sprites/chest.png" x={400} y={280} scale={3} anchor={0.5} />
    </>
  );
}

function App() {
  return (
    <Stage
      width={480}
      height={320}
      options={{ background: 0x1a1a2e, antialias: false }}
    >
      <DungeonScene />
    </Stage>
  );
}

export default App;
```

## Verify

- [ ] Knight sprite renders sharp (no blur)
- [ ] Sprites position correctly (x, y from top-left of canvas)
- [ ] Scale makes sprites bigger without blurring
- [ ] Tint recolors the slime sprites
- [ ] Multiple sprites render without errors

Kai looks at the screen. Six sprites, all crispy, all positioned. "Nice. But they're all just floating in space. Can you organize them into layers? Like, a floor layer and a character layer?"

That's Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Containers & Layout →](chapter-02-containers-layout.md)
