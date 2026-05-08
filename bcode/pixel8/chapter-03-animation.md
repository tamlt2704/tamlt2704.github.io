# Chapter 3: Animation — "Make It Breathe"

[← Chapter 2: Sprites](chapter-02-sprites.md) | [Chapter 4: Interaction →](chapter-04-interaction.md)

---

## Mika's Challenge

Mika watches your sprite showcase and nods approvingly. Then:

> "It's dead. Everything's frozen. In the old games, even idle characters *breathed*. Coins rotated. Torches flickered. The world felt alive because things moved — even just 2 pixels back and forth. Make your sprites move."

She pulls up a GIF of a coin spinning in Super Mario Bros:

> "Four frames. That's it. Four frames and it looks like it's spinning in 3D. Animation at low resolution is about *suggestion*, not simulation."

## Two Animation Approaches

Pixel8 provides two animation components:

1. **`<transition>`** — smoothly interpolate props over time (position, size, color)
2. **`<animation>`** — cycle through discrete frames (sprite animation)

## Transitions: Smooth Movement

The `<transition>` component wraps a child and animates its props from one value to another:

```jsx
<transition from={{ x: 0 }} to={{ x: 50 }} duration={1000} easing="linear">
  <rect y={30} width={4} height={4} color="#fff" />
</transition>
```

This moves a white square from x=0 to x=50 over 1 second, linearly.

### Full Transition Example

```jsx
import React from 'react';
import { Stage } from 'pixel8';

const BouncingBall = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
    {/* Ball moves right */}
    <transition from={{ x: 5 }} to={{ x: 55 }} duration={2000} easing="easeInOut">
      <circ y={32} radius={3} color="#e94560" />
    </transition>
  </Stage>
);

export default BouncingBall;
```

**Important:** Set `fps` to a non-zero value for animations to play. `fps={0}` means static — no updates.

### What You Should See

A red circle gliding smoothly from left to right across the canvas, easing in and out over 2 seconds.

## Transition Props

| Prop | Type | Description |
|------|------|-------------|
| `from` | object | Starting prop values: `{ x: 0, y: 0 }` |
| `to` | object | Ending prop values: `{ x: 50, y: 10 }` |
| `duration` | number | Time in milliseconds |
| `easing` | string | Easing function name |

### Available Easings

| Easing | Effect |
|--------|--------|
| `"linear"` | Constant speed |
| `"easeIn"` | Starts slow, accelerates |
| `"easeOut"` | Starts fast, decelerates |
| `"easeInOut"` | Slow start and end, fast middle |

## Multi-Property Transitions

Animate multiple props simultaneously:

```jsx
<transition
  from={{ x: 5, y: 5 }}
  to={{ x: 55, y: 55 }}
  duration={1500}
  easing="easeInOut"
>
  <rect width={4} height={4} color="#ffd700" />
</transition>
```

The square moves diagonally from top-left to bottom-right.

## Looping Animations

For continuous animation, you can combine transitions or use React state to restart them. A common pattern:

```jsx
import React, { useState, useEffect } from 'react';
import { Stage } from 'pixel8';

const PulsingHeart = () => {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhase(p => (p + 1) % 2);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  const y = phase === 0 ? 28 : 26;

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
      <sprite x={28} y={y} data={heart} palette={['transparent', '#ff0000']} />
    </Stage>
  );
};
```

The heart bobs up and down — a 2-pixel shift that suggests breathing.

## Frame-Based Animation: `<animation>`

For sprite animation (walk cycles, coin spins, explosions), use `<animation>` with multiple frames:

```jsx
// Coin spin — 4 frames showing the coin from different angles
const coinFrames = [
  // Frame 0: full face
  [
    0,0,1,1,1,1,0,0,
    0,1,1,1,1,1,1,0,
    1,1,1,2,2,1,1,1,
    1,1,1,2,2,1,1,1,
    1,1,1,2,2,1,1,1,
    1,1,1,1,1,1,1,1,
    0,1,1,1,1,1,1,0,
    0,0,1,1,1,1,0,0,
  ],
  // Frame 1: slightly turned
  [
    0,0,0,1,1,0,0,0,
    0,0,1,1,1,1,0,0,
    0,1,1,2,2,1,0,0,
    0,1,1,2,2,1,0,0,
    0,1,1,2,2,1,0,0,
    0,1,1,1,1,1,0,0,
    0,0,1,1,1,1,0,0,
    0,0,0,1,1,0,0,0,
  ],
  // Frame 2: edge-on (thin line)
  [
    0,0,0,0,1,0,0,0,
    0,0,0,0,1,0,0,0,
    0,0,0,1,1,0,0,0,
    0,0,0,1,1,0,0,0,
    0,0,0,1,1,0,0,0,
    0,0,0,1,1,0,0,0,
    0,0,0,0,1,0,0,0,
    0,0,0,0,1,0,0,0,
  ],
  // Frame 3: slightly turned (other side)
  [
    0,0,0,1,1,0,0,0,
    0,0,1,1,1,1,0,0,
    0,0,1,2,2,1,1,0,
    0,0,1,2,2,1,1,0,
    0,0,1,2,2,1,1,0,
    0,0,1,1,1,1,1,0,
    0,0,1,1,1,1,0,0,
    0,0,0,1,1,0,0,0,
  ],
];

const coinPalette = ['transparent', '#daa520', '#ffd700'];
```

Render the animation:

```jsx
<animation frames={coinFrames} speed={200} x={28} y={28} palette={coinPalette} />
```

### Animation Props

| Prop | Type | Description |
|------|------|-------------|
| `frames` | array | Array of sprite data arrays (one per frame) |
| `speed` | number | Milliseconds per frame |
| `x`, `y` | number | Position on stage |
| `palette` | array | Color palette (shared across all frames) |

## Combining Transition + Sprite

Move a sprite while it animates:

```jsx
<transition from={{ x: 0 }} to={{ x: 56 }} duration={3000} easing="linear">
  <animation frames={coinFrames} speed={150} y={28} palette={coinPalette} />
</transition>
```

The coin spins *and* moves across the screen — like a coin bouncing after being dropped.

## Pattern: Flickering Torch

```jsx
const torchFrames = [
  // Frame 0: flame left
  [
    0,0,1,0,0,0,0,0,
    0,1,2,1,0,0,0,0,
    0,1,2,2,1,0,0,0,
    0,0,1,2,1,0,0,0,
    0,0,0,1,0,0,0,0,
    0,0,3,3,3,0,0,0,
    0,0,0,3,0,0,0,0,
    0,0,0,3,0,0,0,0,
  ],
  // Frame 1: flame right
  [
    0,0,0,0,1,0,0,0,
    0,0,0,1,2,1,0,0,
    0,0,1,2,2,1,0,0,
    0,0,1,2,1,0,0,0,
    0,0,0,1,0,0,0,0,
    0,0,3,3,3,0,0,0,
    0,0,0,3,0,0,0,0,
    0,0,0,3,0,0,0,0,
  ],
];

const torchPalette = ['transparent', '#ff4500', '#ffd700', '#8b4513'];

// Renders a flickering torch
<animation frames={torchFrames} speed={300} x={10} y={20} palette={torchPalette} />
```

## Tips: Animation at Low Resolution

1. **2 pixels of movement is enough** — at 64×64, moving 2px is like moving 30px at 1080p
2. **3-4 frames suffice** — retro games rarely used more than 4 frames per animation
3. **Speed matters more than frames** — a 2-frame animation at the right speed looks great
4. **Ease everything** — linear motion looks robotic; easeInOut feels natural
5. **Idle animations sell life** — a 1px bob every 2 seconds makes characters feel alive

## Pattern: Breathing Idle Animation

```jsx
const IdleCharacter = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
    {/* Shadow stays still */}
    <rect x={27} y={45} width={10} height={2} color="#111122" />

    {/* Character bobs up and down */}
    <transition from={{ y: 20 }} to={{ y: 22 }} duration={1000} easing="easeInOut">
      <sprite x={28} data={knight} palette={knightPalette} />
    </transition>
  </Stage>
);
```

## Exercise

1. Create a **blinking eye** — a sprite that alternates between open (2 frames) every 3 seconds
2. Animate a `<circ>` moving in a **square path** (hint: chain 4 transitions or use state + timer)
3. Build a **walking character** with 2 frames — legs together, legs apart — cycling at 200ms
4. Make a **shooting star** — a pixel that moves diagonally from top-right to bottom-left with easeIn

## Quick Reference

```jsx
// Smooth property animation
<transition from={{ x: 0 }} to={{ x: 50 }} duration={1000} easing="easeInOut">
  <rect y={30} width={4} height={4} color="#fff" />
</transition>

// Frame-based sprite animation
<animation frames={[frame0, frame1, frame2]} speed={200} x={10} y={10} palette={pal} />
```

| Component | Use Case |
|-----------|----------|
| `<transition>` | Moving, scaling, fading — smooth interpolation |
| `<animation>` | Walk cycles, spinning coins, flickering — discrete frames |

| Easing | Feel |
|--------|------|
| `linear` | Mechanical, constant |
| `easeIn` | Starts slow (falling) |
| `easeOut` | Ends slow (landing) |
| `easeInOut` | Natural, breathing |

---

Next: The sprites move, but you can't control them. Time to add keyboard and mouse input.

[← Chapter 2: Sprites](chapter-02-sprites.md) | [Chapter 4: Interaction →](chapter-04-interaction.md)
