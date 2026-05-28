# Chapter 6: Advanced Demos

[← Chapter 5: Collisions](/blog/physics-matterjs/chapter-05-collisions) | [Overview](/blog/physics-matterjs/chapter-00-overview)

---

## The Goal

Build complete physics simulations: stacking towers, slingshots, ragdolls, and interactive playgrounds.

## Demo 1: Stacking Tower

A tower of boxes that can be knocked over:

```tsx
function createTower(x: number, y: number, cols: number, rows: number) {
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const bx = x + col * 42;
      const by = y - row * 42;
      Composite.add(
        engine.world,
        Bodies.rectangle(bx, by, 40, 40, {
          render: { fillStyle: `hsl(${row * 40 + col * 20}, 70%, 60%)` },
        }),
      );
    }
  }
}

// Wrecking ball to knock it down
const wreckingBall = Bodies.circle(100, 200, 35, {
  density: 0.01, // heavy!
  render: { fillStyle: "#e74c3c" },
});
```

Physics lesson: **center of mass** and **torque**. A tower falls when the center of mass moves outside the base.

## Demo 2: Slingshot

Elastic constraint + projectile:

```tsx
const anchor = { x: 200, y: 350 };
const ball = Bodies.circle(200, 350, 20, { density: 0.005 });

const elastic = Constraint.create({
  pointA: anchor,
  bodyB: ball,
  stiffness: 0.05,
  render: { strokeStyle: "#fff", lineWidth: 3 },
});

// Targets to hit
for (let i = 0; i < 5; i++) {
  Composite.add(
    engine.world,
    Bodies.rectangle(500, 450 - i * 45, 35, 35, {
      render: { fillStyle: `hsl(${i * 60}, 70%, 60%)` },
    }),
  );
}
```

Physics lesson: **elastic potential energy** converts to **kinetic energy**. Pull further = more energy = faster launch.

## Demo 3: Ragdoll

A human figure made of connected bodies:

```tsx
function createRagdoll(x: number, y: number) {
  const head = Bodies.circle(x, y, 15);
  const torso = Bodies.rectangle(x, y + 40, 30, 50);
  const armL = Bodies.rectangle(x - 30, y + 30, 10, 40);
  const armR = Bodies.rectangle(x + 30, y + 30, 10, 40);
  const legL = Bodies.rectangle(x - 10, y + 80, 10, 45);
  const legR = Bodies.rectangle(x + 10, y + 80, 10, 45);

  // Connect with constraints
  const joints = [
    Constraint.create({ bodyA: head, bodyB: torso, length: 20, stiffness: 0.6 }),
    Constraint.create({ bodyA: torso, bodyB: armL, pointA: { x: -15, y: -20 }, length: 5 }),
    Constraint.create({ bodyA: torso, bodyB: armR, pointA: { x: 15, y: -20 }, length: 5 }),
    Constraint.create({ bodyA: torso, bodyB: legL, pointA: { x: -8, y: 25 }, length: 5 }),
    Constraint.create({ bodyA: torso, bodyB: legR, pointA: { x: 8, y: 25 }, length: 5 }),
  ];

  Composite.add(engine.world, [head, torso, armL, armR, legL, legR, ...joints]);
}
```

Physics lesson: **rigid body dynamics** and **joint constraints**. Each limb has independent physics but is connected.

## Demo 4: Conveyor Belt

A surface that moves objects along it:

```tsx
const belt = Bodies.rectangle(350, 400, 400, 20, {
  isStatic: true,
  friction: 1,
  label: "belt",
});

// Move objects on the belt
Events.on(engine, "beforeUpdate", () => {
  engine.world.bodies
    .filter((b) => !b.isStatic && b.position.y < 400 && b.position.y > 380)
    .forEach((b) => {
      Body.setVelocity(b, { x: b.velocity.x + 0.5, y: b.velocity.y });
    });
});
```

## Demo 5: Soft Body (Pressure)

Approximate a soft body with circles and springs:

```tsx
function createSoftBody(x: number, y: number, cols: number, rows: number) {
  const particles: Matter.Body[] = [];
  const gap = 25;

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const p = Bodies.circle(x + col * gap, y + row * gap, 8, {
        render: { fillStyle: "#3498db" },
      });
      particles.push(p);
    }
  }

  // Connect neighbors with springs
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const i = row * cols + col;
      if (col < cols - 1) {
        Composite.add(
          engine.world,
          Constraint.create({
            bodyA: particles[i],
            bodyB: particles[i + 1],
            stiffness: 0.1,
            length: gap,
          }),
        );
      }
      if (row < rows - 1) {
        Composite.add(
          engine.world,
          Constraint.create({
            bodyA: particles[i],
            bodyB: particles[i + cols],
            stiffness: 0.1,
            length: gap,
          }),
        );
      }
    }
  }

  Composite.add(engine.world, particles);
}
```

## Putting It All Together: The Physics Lab

Our [Physics Lab](/games/physics) combines all these concepts:

```
PhysicsLab Component
├── Demo selector (7 simulations)
├── Gravity slider (real-time adjustment)
├── Canvas with Matter.js renderer
└── Mouse interaction (drag any object)
```

Each demo teaches a different physics concept:

- **Gravity** → free fall, mass independence
- **Bounce** → restitution, energy conservation
- **Friction** → surface interaction, ramps
- **Pendulum** → periodic motion, constraints
- **Newton's Cradle** → momentum conservation
- **Stacking** → center of mass, stability
- **Slingshot** → elastic energy, projectile motion

## What's Next?

Ideas to extend:

- Add a **car** with wheel constraints and motor
- Build a **bridge** that breaks under weight
- Create a **marble run** with ramps and funnels
- Make a **physics puzzle game** (get the ball to the goal)
- Add **fluid simulation** with many small particles

---

## The Full Journey

1. **Setup** — Engine, Render, Runner, ground
2. **Bodies** — Shapes, mass, restitution, friction
3. **Forces** — Gravity, applied forces, projectiles
4. **Constraints** — Pendulums, springs, chains
5. **Collisions** — Events, sensors, filtering
6. **Advanced** — Complex simulations combining everything

You now have the tools to simulate any 2D physics scenario. The math is handled by Matter.js — your job is to set up the world and let physics do the rest.

[← Overview](/blog/physics-matterjs/chapter-00-overview)
