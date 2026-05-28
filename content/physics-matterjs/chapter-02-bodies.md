# Chapter 2: Bodies & Properties

[← Chapter 1: Setup](/blog/physics-matterjs/chapter-01-setup) | [Chapter 3: Forces →](/blog/physics-matterjs/chapter-03-forces)

---

## The Goal

Understand body shapes, mass, density, restitution, and friction — the properties that make physics feel real.

## Body Shapes

```tsx
// Circle: x, y, radius
Bodies.circle(300, 100, 30);

// Rectangle: x, y, width, height
Bodies.rectangle(400, 100, 60, 40);

// Polygon: x, y, sides, radius
Bodies.polygon(500, 100, 6, 30); // hexagon

// Trapezoid: x, y, width, height, slope
Bodies.trapezoid(200, 100, 60, 40, 0.3);
```

The `x, y` is always the **center** of the body.

## Mass & Density

Mass = density × area. You set one, Matter.js calculates the other:

```tsx
// Heavy ball (high density)
Bodies.circle(200, 50, 25, { density: 0.01 });

// Light ball (low density)
Bodies.circle(400, 50, 25, { density: 0.001 });
```

Heavier objects push lighter ones aside in collisions, but **fall at the same speed** (just like real physics — Galileo was right).

## Restitution (Bounciness)

```tsx
// Dead ball — no bounce
Bodies.circle(150, 50, 20, { restitution: 0 });

// Normal bounce
Bodies.circle(300, 50, 20, { restitution: 0.5 });

// Super bouncy — almost perfect elastic collision
Bodies.circle(450, 50, 20, { restitution: 0.95 });
```

| Value | Behavior                            |
| ----- | ----------------------------------- |
| 0     | No bounce (clay)                    |
| 0.3   | Low bounce (wood)                   |
| 0.7   | Good bounce (rubber ball)           |
| 1.0   | Perfect bounce (never loses energy) |

## Friction

Three types of friction:

```tsx
Bodies.rectangle(300, 200, 50, 50, {
  friction: 0.1, // surface friction (sliding)
  frictionAir: 0.01, // air resistance (drag)
  frictionStatic: 0.5, // force needed to START moving
});
```

| Property         | What it does                                    |
| ---------------- | ----------------------------------------------- |
| `friction`       | Resistance when sliding against another surface |
| `frictionAir`    | Slows objects moving through "air"              |
| `frictionStatic` | How hard to push before it starts moving        |

### Demo: Ice vs Rubber Ramp

```tsx
// Ramp (tilted static body)
const ramp = Bodies.rectangle(350, 300, 500, 20, {
  isStatic: true,
  angle: Math.PI * 0.1, // ~18 degrees
});

// Ice block — slides easily
const ice = Bodies.rectangle(180, 200, 40, 40, {
  friction: 0.001,
  render: { fillStyle: "#63b3ed" },
});

// Rubber block — grips the surface
const rubber = Bodies.rectangle(250, 200, 40, 40, {
  friction: 0.8,
  render: { fillStyle: "#e74c3c" },
});
```

## Angle & Angular Velocity

Bodies can rotate:

```tsx
// Start at 45 degrees
Bodies.rectangle(300, 100, 80, 30, {
  angle: Math.PI / 4,
});

// Spinning
const spinner = Bodies.rectangle(300, 100, 80, 30);
Matter.Body.setAngularVelocity(spinner, 0.1);
```

## Render Options

Customize how bodies look:

```tsx
Bodies.circle(300, 100, 30, {
  render: {
    fillStyle: "#e74c3c",
    strokeStyle: "#c0392b",
    lineWidth: 3,
    opacity: 0.8,
  },
});
```

## Body Options Summary

```tsx
Bodies.circle(x, y, radius, {
  // Physics
  density: 0.001, // mass per area
  restitution: 0.5, // bounciness
  friction: 0.1, // surface friction
  frictionAir: 0.01, // air drag
  frictionStatic: 0.5, // static friction

  // State
  isStatic: false, // true = immovable
  isSensor: false, // true = detects collision but doesn't react
  angle: 0, // initial rotation (radians)

  // Visual
  render: {
    fillStyle: "#e74c3c",
    visible: true,
  },
});
```

## Experiment

Try the [Bounce demo](/games/physics) — watch how restitution changes behavior. Then try [Friction](/games/physics) to see ice vs rubber on a ramp.

---

[Chapter 3: Forces & Gravity →](/blog/physics-matterjs/chapter-03-forces)
