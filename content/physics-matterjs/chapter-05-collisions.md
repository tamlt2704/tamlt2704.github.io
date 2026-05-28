# Chapter 5: Collisions & Events

[← Chapter 4: Constraints](/blog/physics-matterjs/chapter-04-constraints) | [Chapter 6: Advanced →](/blog/physics-matterjs/chapter-06-advanced)

---

## The Goal

Detect collisions, respond to events, and control which bodies can interact.

## Collision Events

Matter.js fires events when bodies collide:

```tsx
const { Events } = Matter;

Events.on(engine, "collisionStart", (event) => {
  event.pairs.forEach((pair) => {
    console.log("Collision:", pair.bodyA.label, "hit", pair.bodyB.label);
  });
});
```

Three collision events:

| Event             | When                     |
| ----------------- | ------------------------ |
| `collisionStart`  | Bodies first touch       |
| `collisionActive` | Bodies still overlapping |
| `collisionEnd`    | Bodies separate          |

## Labeling Bodies

Use labels to identify bodies in collision handlers:

```tsx
const player = Bodies.circle(100, 100, 20, { label: "player" });
const coin = Bodies.circle(300, 100, 10, { label: "coin" });

Events.on(engine, "collisionStart", (event) => {
  event.pairs.forEach(({ bodyA, bodyB }) => {
    const labels = [bodyA.label, bodyB.label];
    if (labels.includes("player") && labels.includes("coin")) {
      // Player collected a coin!
      Composite.remove(engine.world, bodyA.label === "coin" ? bodyA : bodyB);
    }
  });
});
```

## Sensors (Trigger Zones)

A sensor detects overlap but doesn't physically block:

```tsx
const trigger = Bodies.rectangle(400, 400, 100, 100, {
  isSensor: true, // passes through other bodies
  isStatic: true,
  label: "goal",
  render: { fillStyle: "rgba(0, 255, 0, 0.3)" },
});
```

Use sensors for:

- Goal zones
- Damage areas
- Proximity detection

## Collision Filtering

Control which bodies can collide using categories:

```tsx
// Define categories (powers of 2)
const CATEGORY_PLAYER = 0x0001;
const CATEGORY_ENEMY = 0x0002;
const CATEGORY_BULLET = 0x0004;

// Player collides with enemies but not own bullets
const player = Bodies.circle(100, 100, 20, {
  collisionFilter: {
    category: CATEGORY_PLAYER,
    mask: CATEGORY_ENEMY, // only collide with enemies
  },
});

// Bullet collides with enemies only
const bullet = Bodies.circle(100, 100, 5, {
  collisionFilter: {
    category: CATEGORY_BULLET,
    mask: CATEGORY_ENEMY,
  },
});
```

## Engine Events

Beyond collisions, the engine fires timing events:

```tsx
// Runs before each physics step
Events.on(engine, "beforeUpdate", () => {
  // Apply custom forces, check positions, etc.
});

// Runs after each physics step
Events.on(engine, "afterUpdate", () => {
  // Check win conditions, update score, etc.
});
```

## Mouse Events

Track mouse interaction:

```tsx
const mouse = Mouse.create(render.canvas);
const mc = MouseConstraint.create(engine, { mouse });

Events.on(mc, "mousedown", (event) => {
  console.log("Clicked at:", event.mouse.position);
});

Events.on(mc, "startdrag", (event) => {
  console.log("Started dragging:", event.body.label);
});
```

## Removing Bodies

Remove bodies on collision (e.g., destroying objects):

```tsx
Events.on(engine, "collisionStart", (event) => {
  event.pairs.forEach(({ bodyA, bodyB }) => {
    // Remove bodies marked for destruction
    if (bodyA.label === "destructible") {
      Composite.remove(engine.world, bodyA);
    }
    if (bodyB.label === "destructible") {
      Composite.remove(engine.world, bodyB);
    }
  });
});
```

## Practical Example: Breakout Game Logic

```tsx
const ball = Bodies.circle(350, 400, 10, { label: "ball", restitution: 1 });
const paddle = Bodies.rectangle(350, 480, 100, 15, { isStatic: true, label: "paddle" });

// Create bricks
for (let row = 0; row < 4; row++) {
  for (let col = 0; col < 8; col++) {
    Composite.add(
      engine.world,
      Bodies.rectangle(90 + col * 80, 60 + row * 30, 70, 20, {
        isStatic: true,
        label: "brick",
        render: { fillStyle: `hsl(${row * 60}, 70%, 60%)` },
      }),
    );
  }
}

// Destroy bricks on hit
Events.on(engine, "collisionStart", (event) => {
  event.pairs.forEach(({ bodyA, bodyB }) => {
    const brick = [bodyA, bodyB].find((b) => b.label === "brick");
    if (brick) Composite.remove(engine.world, brick);
  });
});
```

## Experiment

Try the [Stacking demo](/games/physics) — throw the wrecking ball at the tower and watch collision cascades.

---

[Chapter 6: Advanced Demos →](/blog/physics-matterjs/chapter-06-advanced)
