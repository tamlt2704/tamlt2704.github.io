# Chapter 3: Forces & Gravity

[← Chapter 2: Bodies](/blog/physics-matterjs/chapter-02-bodies) | [Chapter 4: Constraints →](/blog/physics-matterjs/chapter-04-constraints)

---

## The Goal

Understand how forces work in Matter.js — gravity, applied forces, velocity, and acceleration.

## Gravity

Gravity is a force applied to every body every frame:

```tsx
const engine = Engine.create({
  gravity: { x: 0, y: 1 }, // default: downward
});
```

| Setting           | Effect                           |
| ----------------- | -------------------------------- |
| `{ x: 0, y: 1 }`  | Normal Earth gravity             |
| `{ x: 0, y: 0 }`  | Zero gravity (space)             |
| `{ x: 0, y: 2 }`  | Double gravity (heavy planet)    |
| `{ x: 0, y: -1 }` | Reverse gravity (things fall up) |
| `{ x: 1, y: 0 }`  | Sideways gravity                 |

Change gravity at runtime:

```tsx
engine.gravity.y = 0.5; // half gravity
```

## Applying Forces

Push a body with `Body.applyForce`:

```tsx
import Matter from "matter-js";
const { Body } = Matter;

// Apply force at the body's center
Body.applyForce(ball, ball.position, { x: 0.05, y: -0.05 });
```

Parameters:

1. The body to push
2. The point where force is applied (affects rotation)
3. The force vector `{ x, y }`

### Force at an Offset (Causes Spin)

```tsx
// Push the top-right corner — body will spin
const offset = { x: ball.position.x + 20, y: ball.position.y - 20 };
Body.applyForce(ball, offset, { x: 0.01, y: 0 });
```

## Setting Velocity Directly

Skip the force math — just set speed:

```tsx
// Launch upward
Body.setVelocity(ball, { x: 0, y: -10 });

// Launch at 45 degrees
Body.setVelocity(ball, { x: 7, y: -7 });
```

Velocity is in pixels per frame (at 60fps).

## The Physics: F = ma

Matter.js uses Newton's second law internally:

```
Force = mass × acceleration
acceleration = Force / mass

Each frame:
  velocity += acceleration
  position += velocity
```

That's why heavier objects need more force to accelerate, but gravity accelerates everything equally (because gravitational force scales with mass).

## Air Resistance

`frictionAir` simulates drag:

```tsx
// Feather (high air resistance)
Bodies.circle(200, 50, 20, { frictionAir: 0.05 });

// Bowling ball (low air resistance)
Bodies.circle(400, 50, 20, { frictionAir: 0.001 });
```

Without `frictionAir`, objects accelerate forever. With it, they reach a terminal velocity.

## Projectile Motion

Classic physics problem — launch at an angle:

```tsx
const projectile = Bodies.circle(100, 400, 10, {
  frictionAir: 0.001,
  render: { fillStyle: "#e74c3c" },
});

// Launch at 45 degrees, speed 12
const angle = -Math.PI / 4; // negative = upward
const speed = 12;
Body.setVelocity(projectile, {
  x: Math.cos(angle) * speed,
  y: Math.sin(angle) * speed,
});
```

The path is a parabola — horizontal velocity stays constant, vertical velocity increases due to gravity.

## Continuous Force (Thrust)

Apply force every frame for continuous acceleration:

```tsx
Events.on(engine, "beforeUpdate", () => {
  if (isThrusting) {
    Body.applyForce(rocket, rocket.position, { x: 0, y: -0.005 });
  }
});
```

## Experiment

Use the [Gravity slider](/games/physics) in the Physics Lab to see how changing gravity affects all objects simultaneously. Try setting it to 0 for space physics.

---

[Chapter 4: Constraints & Joints →](/blog/physics-matterjs/chapter-04-constraints)
