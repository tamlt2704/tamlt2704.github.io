# Chapter 4: Constraints & Joints

[← Chapter 3: Forces](/blog/physics-matterjs/chapter-03-forces) | [Chapter 5: Collisions →](/blog/physics-matterjs/chapter-05-collisions)

---

## The Goal

Connect bodies together with constraints — build pendulums, springs, ropes, and chains.

## What is a Constraint?

A constraint connects two points with a "spring". It tries to maintain a fixed distance between them.

```tsx
const { Constraint } = Matter;
```

## Pin Constraint (Pendulum)

Attach a body to a fixed point in space:

```tsx
const bob = Bodies.circle(400, 300, 25);

const pendulum = Constraint.create({
  pointA: { x: 350, y: 50 }, // fixed anchor point
  bodyB: bob, // the swinging body
  length: 250, // rope length
  stiffness: 1, // 1 = rigid rod, <1 = elastic
});

Composite.add(engine.world, [bob, pendulum]);
```

Drag the bob and release — it swings like a pendulum.

## Spring Constraint

Lower stiffness = stretchy spring:

```tsx
const spring = Constraint.create({
  pointA: { x: 350, y: 100 },
  bodyB: ball,
  length: 100,
  stiffness: 0.01, // very stretchy
  damping: 0.05, // reduces oscillation over time
});
```

| Stiffness | Behavior                  |
| --------- | ------------------------- |
| 1.0       | Rigid rod (no stretch)    |
| 0.1       | Stiff spring              |
| 0.01      | Soft spring (bungee cord) |
| 0.001     | Very elastic              |

## Body-to-Body Constraint

Connect two bodies together:

```tsx
const bodyA = Bodies.circle(200, 100, 20);
const bodyB = Bodies.circle(400, 100, 20);

const link = Constraint.create({
  bodyA: bodyA,
  bodyB: bodyB,
  length: 200,
  stiffness: 0.5,
});

Composite.add(engine.world, [bodyA, bodyB, link]);
```

## Chain (Multiple Links)

Build a rope by chaining constraints:

```tsx
function createChain(x: number, y: number, links: number) {
  let prev: Matter.Body | null = null;

  for (let i = 0; i < links; i++) {
    const link = Bodies.circle(x, y + i * 30, 8, {
      density: 0.001,
      render: { fillStyle: "#ccc" },
    });
    Composite.add(engine.world, link);

    if (prev) {
      Composite.add(
        engine.world,
        Constraint.create({
          bodyA: prev,
          bodyB: link,
          length: 30,
          stiffness: 0.8,
        }),
      );
    } else {
      // First link pinned to ceiling
      Composite.add(
        engine.world,
        Constraint.create({
          pointA: { x, y },
          bodyB: link,
          length: 0,
          stiffness: 1,
        }),
      );
    }
    prev = link;
  }
}
```

## Newton's Cradle

The classic desk toy — conservation of momentum:

```tsx
const num = 5,
  size = 20,
  sep = size * 2.05;

for (let i = 0; i < num; i++) {
  const x = 250 + i * sep;
  const ball = Bodies.circle(x, 300, size, {
    restitution: 1, // perfect bounce
    friction: 0, // no energy loss
    frictionAir: 0.0001, // minimal air drag
  });

  const string = Constraint.create({
    pointA: { x, y: 50 },
    bodyB: ball,
    length: 250,
    stiffness: 1,
  });

  Composite.add(engine.world, [ball, string]);
}
```

Pull the first ball to the side and release — energy transfers through the chain.

## Slingshot (Elastic + Release)

```tsx
const anchor = { x: 200, y: 350 };
const ball = Bodies.circle(200, 350, 20);

const elastic = Constraint.create({
  pointA: anchor,
  bodyB: ball,
  stiffness: 0.05, // stretchy
});

Composite.add(engine.world, [ball, elastic]);
```

The mouse constraint lets you pull the ball back. When released, the elastic snaps it forward.

## Constraint Options Summary

```tsx
Constraint.create({
  // Connection points (pick one pair)
  pointA: { x, y }, // fixed point in world
  bodyA: someBody, // or attach to a body
  pointB: { x, y }, // offset on bodyB (default: center)
  bodyB: someBody, // the other body

  // Physics
  length: 200, // rest length
  stiffness: 1, // 0-1 (1 = rigid)
  damping: 0, // 0-1 (reduces oscillation)

  // Visual
  render: {
    strokeStyle: "#fff",
    lineWidth: 2,
    visible: true,
  },
});
```

## Experiment

Try the [Pendulum](/games/physics) and [Newton's Cradle](/games/physics) demos. Drag the pendulum bob to different heights and observe the period stays roughly constant (for small angles).

---

[Chapter 5: Collisions & Events →](/blog/physics-matterjs/chapter-05-collisions)
