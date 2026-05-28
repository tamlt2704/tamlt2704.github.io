# Chapter 1: Setup & First World

[← Overview](/blog/physics-matterjs/chapter-00-overview) | [Chapter 2: Bodies →](/blog/physics-matterjs/chapter-02-bodies)

---

## The Goal

Create a physics world with gravity, a ground, and falling objects — in under 30 lines.

## Step 1: Install

```bash
npm install matter-js
npm install -D @types/matter-js
```

## Step 2: Import the Modules

Matter.js is modular. You import what you need:

```tsx
import Matter from "matter-js";

const { Engine, Render, Runner, Bodies, Composite } = Matter;
```

| Module      | Purpose                          |
| ----------- | -------------------------------- |
| `Engine`    | Runs the physics simulation      |
| `Render`    | Draws bodies to a canvas         |
| `Runner`    | Calls `Engine.update()` at 60fps |
| `Bodies`    | Factory for creating shapes      |
| `Composite` | Add/remove bodies from the world |

## Step 3: Create the Engine

```tsx
const engine = Engine.create({
  gravity: { x: 0, y: 1 }, // Earth-like gravity (downward)
});
```

The engine is the brain. It calculates positions, velocities, and collisions every frame.

## Step 4: Create the Renderer

```tsx
const render = Render.create({
  element: document.getElementById("canvas-container"),
  engine: engine,
  options: {
    width: 700,
    height: 500,
    wireframes: false, // solid shapes (not wireframe)
    background: "#1a1a2e", // dark background
  },
});
```

The renderer reads body positions from the engine and draws them.

## Step 5: Add a Ground

```tsx
const ground = Bodies.rectangle(350, 525, 700, 50, {
  isStatic: true, // doesn't move, doesn't fall
  render: { fillStyle: "#4a5568" },
});

Composite.add(engine.world, ground);
```

`isStatic: true` means this body is fixed — other objects collide with it but it never moves.

## Step 6: Add Falling Objects

```tsx
const ball = Bodies.circle(350, 50, 25, {
  restitution: 0.7, // bounciness (0 = no bounce, 1 = perfect bounce)
  render: { fillStyle: "#e74c3c" },
});

const box = Bodies.rectangle(250, 80, 40, 40, {
  render: { fillStyle: "#3498db" },
});

Composite.add(engine.world, [ball, box]);
```

## Step 7: Run It

```tsx
Render.run(render);
const runner = Runner.create();
Runner.run(runner, engine);
```

That's it. Objects fall, hit the ground, and bounce.

## The Complete Minimal Example

```tsx
"use client";
import { useEffect, useRef } from "react";
import Matter from "matter-js";

const { Engine, Render, Runner, Bodies, Composite } = Matter;

export default function PhysicsDemo() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const engine = Engine.create();
    const render = Render.create({
      element: ref.current,
      engine,
      options: { width: 700, height: 500, wireframes: false, background: "#1a1a2e" },
    });

    const ground = Bodies.rectangle(350, 525, 700, 50, { isStatic: true });
    const ball = Bodies.circle(350, 50, 25, { restitution: 0.7 });

    Composite.add(engine.world, [ground, ball]);
    Render.run(render);
    Runner.run(Runner.create(), engine);

    return () => {
      Render.stop(render);
      Engine.clear(engine);
      render.canvas.remove();
    };
  }, []);

  return <div ref={ref} />;
}
```

## Key Concepts

- **Engine** = physics calculator (runs at 60fps)
- **Render** = visual output (canvas)
- **Runner** = clock that ticks the engine
- **Static bodies** = immovable (floors, walls)
- **Dynamic bodies** = affected by gravity and forces

## Cleanup in React

Always clean up in the `useEffect` return:

1. Stop the renderer
2. Clear the engine
3. Remove the canvas element

Without this, you'll get memory leaks and duplicate canvases on re-renders.

---

[Chapter 2: Bodies & Properties →](/blog/physics-matterjs/chapter-02-bodies)
