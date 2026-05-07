# Chapter 4: Animation & Tick — "Make Things Move"

[← Chapter 3: Graphics & Shapes](chapter-03-graphics-shapes.md) | [Chapter 5: Spritesheet Animation →](chapter-05-spritesheet-animation.md)

---

## The Crisis

The dungeon is static. Sprites sit there like a screenshot. Kai says: "The slime should bounce. The torches should flicker. It needs to feel alive."

In web dev, you'd use `requestAnimationFrame` or CSS animations. In @pixi/react, you use the `useTick` hook — it runs a callback every frame, 60 times per second.

## useTick: The Game Loop

```jsx
import { Sprite } from '@pixi/react';
import { useTick } from '@pixi/react';
import { useState } from 'react';

function BouncingSlime() {
  const [y, setY] = useState(200);

  useTick((delta) => {
    // delta is the frame time multiplier (1.0 at 60fps)
    setY(200 + Math.sin(Date.now() / 300) * 10);
  });

  return <Sprite image="./sprites/slime.png" x={240} y={y} scale={3} anchor={0.5} />;
}
```

The slime bobs up and down. `useTick` fires every frame. `delta` is a multiplier — at 60fps it's ~1.0, at 30fps it's ~2.0. Use it to keep animations frame-rate independent.

## The Problem with useState in Game Loops

That `setY` call triggers a React re-render every frame. 60 re-renders per second. For one sprite, it's fine. For 50 sprites, it's a performance disaster.

```jsx
// ❌ Bad — triggers React re-render every frame
function BouncingSlime() {
  const [y, setY] = useState(200);
  useTick(() => setY(200 + Math.sin(Date.now() / 300) * 10));
  return <Sprite image="./sprites/slime.png" y={y} />;
}
```

## The Fix: useRef for Frame-by-Frame Updates

Use `useRef` to hold a reference to the PixiJS display object, then mutate it directly — bypassing React's render cycle:

```jsx
import { Sprite } from '@pixi/react';
import { useTick } from '@pixi/react';
import { useRef } from 'react';

function BouncingSlime() {
  const spriteRef = useRef(null);

  useTick((delta) => {
    if (!spriteRef.current) return;
    spriteRef.current.y = 200 + Math.sin(Date.now() / 300) * 10;
  });

  return (
    <Sprite
      ref={spriteRef}
      image="./sprites/slime.png"
      x={240}
      y={200}
      scale={3}
      anchor={0.5}
    />
  );
}
```

No re-renders. The sprite's `y` property is mutated directly on the PixiJS object. The GPU draws the new position next frame. This is how game loops work — direct mutation, not immutable state updates.

## When to Use useState vs useRef

| Use `useState` when... | Use `useRef` when... |
|---|---|
| Value changes infrequently | Value changes every frame |
| Other components need to react to it | Only the PixiJS object needs it |
| It's game state (health, score) | It's visual state (position, rotation) |
| It triggers UI updates | It's purely cosmetic animation |

Rule of thumb: **If it changes every frame, use useRef. If it changes on events, use useState.**

## Delta Time: Frame-Rate Independence

`delta` normalizes animation speed across different frame rates:

```jsx
function MovingSprite() {
  const ref = useRef(null);
  const speed = 2; // pixels per frame at 60fps

  useTick((delta) => {
    if (!ref.current) return;
    ref.current.x += speed * delta;
  });

  return <Sprite ref={ref} image="./sprites/knight.png" x={0} y={160} scale={3} />;
}
```

At 60fps: `delta ≈ 1.0`, moves 2px/frame → 120px/sec
At 30fps: `delta ≈ 2.0`, moves 4px/frame → 120px/sec

Same speed regardless of frame rate. Always multiply movement by `delta`.

## Animation Patterns

### Bobbing (Sine Wave)

```jsx
function Bobbing({ children }) {
  const ref = useRef(null);
  const startTime = useRef(Date.now());

  useTick(() => {
    if (!ref.current) return;
    const elapsed = (Date.now() - startTime.current) / 1000;
    ref.current.y = Math.sin(elapsed * 3) * 5;  // 5px amplitude, 3 cycles/sec
  });

  return <Container ref={ref}>{children}</Container>;
}

// Usage
<Bobbing>
  <Sprite image="./sprites/chest.png" x={200} y={150} scale={3} anchor={0.5} />
</Bobbing>
```

### Rotation

```jsx
function SpinningCoin() {
  const ref = useRef(null);

  useTick((delta) => {
    if (!ref.current) return;
    ref.current.rotation += 0.05 * delta;
  });

  return <Sprite ref={ref} image="./sprites/coin.png" x={300} y={100} scale={3} anchor={0.5} />;
}
```

### Pulsing (Scale)

```jsx
function PulsingItem() {
  const ref = useRef(null);

  useTick(() => {
    if (!ref.current) return;
    const pulse = 1 + Math.sin(Date.now() / 200) * 0.1;  // scale between 0.9 and 1.1
    ref.current.scale.set(3 * pulse);
  });

  return <Sprite ref={ref} image="./sprites/key.png" x={150} y={200} scale={3} anchor={0.5} />;
}
```

### Flickering (Alpha)

```jsx
function FlickeringTorch() {
  const ref = useRef(null);

  useTick(() => {
    if (!ref.current) return;
    // Random flicker between 0.6 and 1.0
    ref.current.alpha = 0.6 + Math.random() * 0.4;
  });

  return <Sprite ref={ref} image="./sprites/torch.png" x={32} y={48} scale={2} anchor={0.5} />;
}
```

## Combining Multiple Animations

A slime that bobs AND squishes:

```jsx
function AnimatedSlime({ x, y }) {
  const ref = useRef(null);

  useTick(() => {
    if (!ref.current) return;
    const t = Date.now() / 400;

    // Bob up and down
    ref.current.y = y + Math.sin(t) * 4;

    // Squish (wider when at bottom, taller when at top)
    const squish = Math.sin(t);
    ref.current.scale.x = 3 * (1 + squish * 0.1);
    ref.current.scale.y = 3 * (1 - squish * 0.1);
  });

  return (
    <Sprite
      ref={ref}
      image="./sprites/slime.png"
      x={x}
      y={y}
      scale={3}
      anchor={{ x: 0.5, y: 1 }}  // anchor at bottom so it squishes "into" the ground
    />
  );
}
```

## Conditional Tick (Pause/Resume)

`useTick` accepts a second argument to enable/disable:

```jsx
function Player({ paused }) {
  const ref = useRef(null);

  useTick((delta) => {
    if (!ref.current) return;
    ref.current.x += 1 * delta;
  }, !paused);  // only ticks when not paused

  return <Sprite ref={ref} image="./sprites/knight.png" x={0} y={160} scale={3} />;
}
```

When `paused` is `true`, the tick callback stops firing. Useful for pause menus, cutscenes, or game over states.

## useApp: Access the PixiJS Application

Sometimes you need the raw PixiJS app (for screen dimensions, renderer info, etc.):

```jsx
import { useApp } from '@pixi/react';

function ScreenInfo() {
  const app = useApp();

  console.log(app.screen.width);   // Stage width
  console.log(app.screen.height);  // Stage height
  console.log(app.ticker.FPS);     // Current FPS

  return null;
}
```

`useApp()` returns the `PIXI.Application` instance. Use it sparingly — most things can be done with props and `useTick`.

## Putting It All Together

```jsx
import { Stage, Container, Sprite } from '@pixi/react';
import { useTick } from '@pixi/react';
import * as PIXI from 'pixi.js';
import { useRef } from 'react';

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function FlickeringTorch({ x, y }) {
  const ref = useRef(null);
  useTick(() => {
    if (!ref.current) return;
    ref.current.alpha = 0.7 + Math.random() * 0.3;
  });
  return <Sprite ref={ref} image="./sprites/torch.png" x={x} y={y} scale={2} anchor={0.5} />;
}

function AnimatedSlime({ x, y }) {
  const ref = useRef(null);
  useTick(() => {
    if (!ref.current) return;
    const t = Date.now() / 400;
    ref.current.y = y + Math.sin(t) * 4;
    ref.current.scale.x = 3 * (1 + Math.sin(t) * 0.1);
    ref.current.scale.y = 3 * (1 - Math.sin(t) * 0.1);
  });
  return <Sprite ref={ref} image="./sprites/slime.png" x={x} y={y} scale={3} anchor={{ x: 0.5, y: 1 }} />;
}

function PulsingKey({ x, y }) {
  const ref = useRef(null);
  useTick(() => {
    if (!ref.current) return;
    ref.current.scale.set(3 * (1 + Math.sin(Date.now() / 200) * 0.1));
  });
  return <Sprite ref={ref} image="./sprites/key.png" x={x} y={y} scale={3} anchor={0.5} />;
}

function Game() {
  return (
    <>
      <FlickeringTorch x={32} y={48} />
      <FlickeringTorch x={448} y={48} />
      <Sprite image="./sprites/knight.png" x={240} y={200} scale={3} anchor={0.5} />
      <AnimatedSlime x={350} y={240} />
      <AnimatedSlime x={120} y={260} />
      <PulsingKey x={400} y={100} />
    </>
  );
}

function App() {
  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      <Game />
    </Stage>
  );
}

export default App;
```

## Verify

- [ ] `useTick` fires every frame
- [ ] Sprites move/rotate/scale smoothly
- [ ] `useRef` avoids re-renders (check React DevTools — no flashing)
- [ ] `delta` keeps animation speed consistent
- [ ] Multiple animated objects run simultaneously without lag

Kai watches the screen. Torches flicker. Slimes bounce. The key pulses. "Now it feels alive. But the knight just stands there. I drew a walk cycle — four frames. Can you make him actually walk?"

Frame-by-frame animation. That's Chapter 5.

---

[← Chapter 3: Graphics & Shapes](chapter-03-graphics-shapes.md) | [Chapter 5: Spritesheet Animation →](chapter-05-spritesheet-animation.md)
