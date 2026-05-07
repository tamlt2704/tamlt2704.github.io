# Chapter 5: Spritesheet Animation — "Animate the Character"

[← Chapter 4: Animation & Tick](chapter-04-animation-tick.md) | [Chapter 6: Input & Controls →](chapter-06-input-controls.md)

---

## The Crisis

Kai sends a spritesheet: `knight_sheet.png` — a grid of 16×16 frames. Four frames for walking down, four for walking up, four for left, four for right. Plus an idle frame and an attack frame.

"Just cycle through the frames," Kai says. "Like a flip book."

You can't just load one image anymore. You need to slice the spritesheet into individual frames and play them in sequence.

## Spritesheet Anatomy

Kai's spritesheet is a single PNG with frames arranged in a grid:

```
knight_sheet.png (64×80 pixels)
┌────┬────┬────┬────┐
│ D1 │ D2 │ D3 │ D4 │  Row 0: Walk Down
├────┼────┼────┼────┤
│ U1 │ U2 │ U3 │ U4 │  Row 1: Walk Up
├────┼────┼────┼────┤
│ L1 │ L2 │ L3 │ L4 │  Row 2: Walk Left
├────┼────┼────┼────┤
│ R1 │ R2 │ R3 │ R4 │  Row 3: Walk Right
├────┼────┼────┼────┤
│ I1 │ A1 │ A2 │ A3 │  Row 4: Idle + Attack
└────┴────┴────┴────┘
Each cell: 16×16 pixels
```

## The JSON Atlas Format

PixiJS loads spritesheets using a JSON descriptor that maps frame names to regions in the image. Create `public/sprites/knight_sheet.json`:

```json
{
  "frames": {
    "walk_down_0": { "frame": { "x": 0, "y": 0, "w": 16, "h": 16 } },
    "walk_down_1": { "frame": { "x": 16, "y": 0, "w": 16, "h": 16 } },
    "walk_down_2": { "frame": { "x": 32, "y": 0, "w": 16, "h": 16 } },
    "walk_down_3": { "frame": { "x": 48, "y": 0, "w": 16, "h": 16 } },
    "walk_up_0": { "frame": { "x": 0, "y": 16, "w": 16, "h": 16 } },
    "walk_up_1": { "frame": { "x": 16, "y": 16, "w": 16, "h": 16 } },
    "walk_up_2": { "frame": { "x": 32, "y": 16, "w": 16, "h": 16 } },
    "walk_up_3": { "frame": { "x": 48, "y": 16, "w": 16, "h": 16 } },
    "walk_left_0": { "frame": { "x": 0, "y": 32, "w": 16, "h": 16 } },
    "walk_left_1": { "frame": { "x": 16, "y": 32, "w": 16, "h": 16 } },
    "walk_left_2": { "frame": { "x": 32, "y": 32, "w": 16, "h": 16 } },
    "walk_left_3": { "frame": { "x": 48, "y": 32, "w": 16, "h": 16 } },
    "walk_right_0": { "frame": { "x": 0, "y": 48, "w": 16, "h": 16 } },
    "walk_right_1": { "frame": { "x": 16, "y": 48, "w": 16, "h": 16 } },
    "walk_right_2": { "frame": { "x": 32, "y": 48, "w": 16, "h": 16 } },
    "walk_right_3": { "frame": { "x": 48, "y": 48, "w": 16, "h": 16 } },
    "idle_0": { "frame": { "x": 0, "y": 64, "w": 16, "h": 16 } },
    "attack_0": { "frame": { "x": 16, "y": 64, "w": 16, "h": 16 } },
    "attack_1": { "frame": { "x": 32, "y": 64, "w": 16, "h": 16 } },
    "attack_2": { "frame": { "x": 48, "y": 64, "w": 16, "h": 16 } }
  },
  "meta": {
    "image": "knight_sheet.png",
    "format": "RGBA8888",
    "size": { "w": 64, "h": 80 },
    "scale": "1"
  }
}
```

The JSON tells PixiJS where each frame lives in the image. The `meta.image` field points to the PNG (relative to the JSON file).

## Loading the Spritesheet

Load the spritesheet before using it. Use PixiJS's asset loader:

```jsx
import { Stage, Container, Sprite } from '@pixi/react';
import * as PIXI from 'pixi.js';
import { useState, useEffect } from 'react';

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function App() {
  const [sheet, setSheet] = useState(null);

  useEffect(() => {
    PIXI.Assets.load('./sprites/knight_sheet.json').then((loaded) => {
      setSheet(loaded);
    });
  }, []);

  if (!sheet) return <Stage width={480} height={320} options={{ background: 0x1a1a2e }} />;

  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      <Player sheet={sheet} />
    </Stage>
  );
}
```

Once loaded, `sheet.textures` contains all named frames as `PIXI.Texture` objects.

## AnimatedSprite Component

@pixi/react provides an `AnimatedSprite` component for frame-based animation:

```jsx
import { AnimatedSprite } from '@pixi/react';

function Player({ sheet }) {
  // Get the walk-down frames as an array of textures
  const walkDownFrames = [
    sheet.textures['walk_down_0'],
    sheet.textures['walk_down_1'],
    sheet.textures['walk_down_2'],
    sheet.textures['walk_down_3'],
  ];

  return (
    <AnimatedSprite
      textures={walkDownFrames}
      isPlaying={true}
      animationSpeed={0.1}
      x={240}
      y={160}
      anchor={0.5}
      scale={3}
    />
  );
}
```

The knight walks in place. Four frames cycling at `animationSpeed={0.1}` (10% of 60fps = ~6 frames per second).

## AnimatedSprite Props

| Prop | Type | Description |
|---|---|---|
| `textures` | PIXI.Texture[] | Array of frame textures |
| `isPlaying` | boolean | Whether animation is playing |
| `animationSpeed` | number | Speed multiplier (0.1 = slow, 1.0 = 60fps) |
| `loop` | boolean | Loop the animation (default: true) |
| `initialFrame` | number | Starting frame index |
| `onComplete` | function | Callback when non-looping animation ends |
| `onFrameChange` | function | Callback on each frame change |

## Switching Animations Based on State

The player has multiple animations: idle, walk_down, walk_up, walk_left, walk_right, attack. Switch between them based on game state:

```jsx
import { AnimatedSprite } from '@pixi/react';
import { useMemo } from 'react';

function Player({ sheet, direction, isMoving, isAttacking }) {
  // Build animation sets from the spritesheet
  const animations = useMemo(() => ({
    idle: [sheet.textures['idle_0']],
    walk_down: [
      sheet.textures['walk_down_0'],
      sheet.textures['walk_down_1'],
      sheet.textures['walk_down_2'],
      sheet.textures['walk_down_3'],
    ],
    walk_up: [
      sheet.textures['walk_up_0'],
      sheet.textures['walk_up_1'],
      sheet.textures['walk_up_2'],
      sheet.textures['walk_up_3'],
    ],
    walk_left: [
      sheet.textures['walk_left_0'],
      sheet.textures['walk_left_1'],
      sheet.textures['walk_left_2'],
      sheet.textures['walk_left_3'],
    ],
    walk_right: [
      sheet.textures['walk_right_0'],
      sheet.textures['walk_right_1'],
      sheet.textures['walk_right_2'],
      sheet.textures['walk_right_3'],
    ],
    attack: [
      sheet.textures['attack_0'],
      sheet.textures['attack_1'],
      sheet.textures['attack_2'],
    ],
  }), [sheet]);

  // Determine current animation
  let currentAnim = 'idle';
  if (isAttacking) {
    currentAnim = 'attack';
  } else if (isMoving) {
    currentAnim = `walk_${direction}`;
  }

  return (
    <AnimatedSprite
      textures={animations[currentAnim]}
      isPlaying={isMoving || isAttacking}
      animationSpeed={isAttacking ? 0.2 : 0.12}
      loop={!isAttacking}
      x={240}
      y={160}
      anchor={0.5}
      scale={3}
    />
  );
}
```

## One-Shot Animations (Attack)

For attack animations that play once and stop:

```jsx
function Player({ sheet, direction, isMoving, isAttacking, onAttackEnd }) {
  const animations = useMemo(() => ({
    // ... same as above
  }), [sheet]);

  let currentAnim = 'idle';
  if (isAttacking) currentAnim = 'attack';
  else if (isMoving) currentAnim = `walk_${direction}`;

  return (
    <AnimatedSprite
      textures={animations[currentAnim]}
      isPlaying={isMoving || isAttacking}
      animationSpeed={isAttacking ? 0.25 : 0.12}
      loop={!isAttacking}
      onComplete={isAttacking ? onAttackEnd : undefined}
      x={240}
      y={160}
      anchor={0.5}
      scale={3}
    />
  );
}
```

`onComplete` fires when a non-looping animation reaches its last frame. Use it to transition back to idle.

## Helper: Extract Frames from Sheet

A utility to avoid repetitive frame extraction:

```jsx
function getFrames(sheet, prefix, count) {
  const frames = [];
  for (let i = 0; i < count; i++) {
    frames.push(sheet.textures[`${prefix}_${i}`]);
  }
  return frames;
}

// Usage
const animations = useMemo(() => ({
  idle: getFrames(sheet, 'idle', 1),
  walk_down: getFrames(sheet, 'walk_down', 4),
  walk_up: getFrames(sheet, 'walk_up', 4),
  walk_left: getFrames(sheet, 'walk_left', 4),
  walk_right: getFrames(sheet, 'walk_right', 4),
  attack: getFrames(sheet, 'attack', 3),
}), [sheet]);
```

## Animated Enemies

The same pattern works for enemies. Kai sends `slime_sheet.json` with bounce frames:

```jsx
function Slime({ sheet, x, y }) {
  const frames = useMemo(() => getFrames(sheet, 'slime_bounce', 4), [sheet]);

  return (
    <AnimatedSprite
      textures={frames}
      isPlaying={true}
      animationSpeed={0.08}
      x={x}
      y={y}
      anchor={{ x: 0.5, y: 1 }}
      scale={3}
    />
  );
}
```

## Loading Multiple Spritesheets

For a real game, you'll have multiple sheets. Load them all before rendering:

```jsx
function App() {
  const [assets, setAssets] = useState(null);

  useEffect(() => {
    async function loadAssets() {
      const knight = await PIXI.Assets.load('./sprites/knight_sheet.json');
      const slime = await PIXI.Assets.load('./sprites/slime_sheet.json');
      const tiles = await PIXI.Assets.load('./sprites/tiles_sheet.json');
      setAssets({ knight, slime, tiles });
    }
    loadAssets();
  }, []);

  if (!assets) {
    return <Stage width={480} height={320} options={{ background: 0x1a1a2e }}>
      {/* Loading screen */}
    </Stage>;
  }

  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      <Game assets={assets} />
    </Stage>
  );
}
```

## Verify

- [ ] Spritesheet JSON loads without errors
- [ ] AnimatedSprite cycles through frames
- [ ] Animation speed is controllable
- [ ] Switching between animations works (idle → walk → attack)
- [ ] One-shot animations fire `onComplete`
- [ ] Multiple animated sprites run independently

Kai watches the knight walk in place. "Beautiful. Now let me actually control him. Arrow keys. WASD. Something."

Input handling. That's Chapter 6.

---

[← Chapter 4: Animation & Tick](chapter-04-animation-tick.md) | [Chapter 6: Input & Controls →](chapter-06-input-controls.md)
