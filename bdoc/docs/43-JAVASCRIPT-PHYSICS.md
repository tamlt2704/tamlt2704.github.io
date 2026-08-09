# Chapter 43: JavaScript Physics Simulation — Particles, Gravity, and Collisions

## What you'll learn

- Which library to use for physics (D3, Matter.js, Cannon.js, or raw code)
- The physics loop: forces → acceleration → velocity → position
- Verlet integration (stable, simple, powerful)
- Gravity, springs, friction, and constraints
- Collision detection and response (circles, rectangles, polygons)
- Build: particle systems, cloth simulation, bouncing balls, planetary orbits
- Rendering with Canvas 2D (fastest for 2D physics)

---

## PART 1: Choosing Your Tool

## 43.1 Library comparison

| Library | Type | Best for | Physics quality |
|---------|------|----------|----------------|
| **Raw JS + Canvas** | DIY | Learning, full control, custom physics | You decide |
| **D3-force** | Layout | Node positioning, graph layouts | Simplified (not real physics) |
| **Matter.js** | 2D rigid body | Games, interactive demos, realistic 2D | Excellent |
| **p5.js** | Creative coding | Art, generative visuals, teaching | Basic (you build physics) |
| **Cannon-es** | 3D rigid body | 3D games with Three.js | Excellent |
| **Rapier** | 2D/3D (WASM) | High-performance, deterministic | Professional |

**Verdict:**
- **Learning physics concepts** → Raw JS + Canvas (this chapter)
- **Quick 2D physics demos** → Matter.js (ready-made engine)
- **D3-force** → Only for graph layouts (simplified physics, not general simulation)
- **3D physics** → Cannon-es (with Three.js) or Rapier

**Why NOT D3 for physics?** D3-force is a force-directed graph layout tool — it simulates repulsion between nodes and spring forces on edges to find pleasing positions. It's NOT a general physics engine:
- No collision detection (nodes overlap)
- No rigid bodies (no rotation, no shape)
- No realistic gravity (it uses artificial centering force)
- No constraints (joints, ropes, cloth)

D3-force is great for what it does (position graph nodes). For real physics, use raw code or Matter.js.

## 43.2 The physics loop

Every physics simulation follows this structure:

```javascript
const FIXED_DT = 1 / 60; // 60 physics steps per second

function physicsLoop() {
  // 1. Apply forces (gravity, springs, user input)
  applyForces();

  // 2. Integrate (update velocity and position)
  integrate(FIXED_DT);

  // 3. Detect collisions
  const collisions = detectCollisions();

  // 4. Resolve collisions (push objects apart, bounce)
  resolveCollisions(collisions);

  // 5. Apply constraints (ropes, joints, boundaries)
  applyConstraints();
}

function renderLoop() {
  // Runs at screen refresh rate (requestAnimationFrame)
  clearCanvas();
  drawAllObjects();
  requestAnimationFrame(renderLoop);
}
```

**Why separate physics and render?** Physics needs a fixed timestep (for stability). Rendering should match the monitor refresh rate (for smoothness). Decouple them.

## 43.3 Vector math — the foundation

```javascript
class Vec2 {
  constructor(x = 0, y = 0) {
    this.x = x;
    this.y = y;
  }

  add(v) { return new Vec2(this.x + v.x, this.y + v.y); }
  sub(v) { return new Vec2(this.x - v.x, this.y - v.y); }
  mul(s) { return new Vec2(this.x * s, this.y * s); }
  div(s) { return new Vec2(this.x / s, this.y / s); }

  length() { return Math.sqrt(this.x * this.x + this.y * this.y); }
  normalize() {
    const len = this.length();
    return len > 0 ? this.div(len) : new Vec2();
  }

  dot(v) { return this.x * v.x + this.y * v.y; }
  cross(v) { return this.x * v.y - this.y * v.x; } // 2D cross product (scalar)

  distTo(v) { return this.sub(v).length(); }

  static fromAngle(angle) {
    return new Vec2(Math.cos(angle), Math.sin(angle));
  }
}
```

---

## PART 2: Newton's Laws in Code

## 43.4 Euler integration (simple but unstable)

```javascript
// F = ma → a = F/m → v += a*dt → pos += v*dt

class Particle {
  constructor(x, y, mass = 1) {
    this.pos = new Vec2(x, y);
    this.vel = new Vec2(0, 0);
    this.acc = new Vec2(0, 0);
    this.mass = mass;
    this.radius = Math.sqrt(mass) * 5;
    this.forces = new Vec2(0, 0);
  }

  applyForce(force) {
    // F = ma → a = F/m
    this.forces = this.forces.add(force);
  }

  update(dt) {
    // Euler integration
    this.acc = this.forces.div(this.mass);  // a = F/m
    this.vel = this.vel.add(this.acc.mul(dt));  // v += a*dt
    this.pos = this.pos.add(this.vel.mul(dt));  // x += v*dt

    // Reset forces for next frame
    this.forces = new Vec2(0, 0);
  }
}
```

**Problem with Euler:** Energy isn't conserved — objects slowly speed up or slow down over time. Fine for simple demos, bad for orbital mechanics or springs.

## 43.5 Verlet integration (stable, better)

Instead of storing velocity explicitly, derive it from position history:

```javascript
class VerletParticle {
  constructor(x, y, mass = 1) {
    this.pos = new Vec2(x, y);
    this.prevPos = new Vec2(x, y);  // position last frame
    this.acc = new Vec2(0, 0);
    this.mass = mass;
    this.radius = Math.sqrt(mass) * 5;
  }

  applyForce(force) {
    this.acc = this.acc.add(force.div(this.mass));
  }

  update(dt) {
    // Velocity is implicit: vel = pos - prevPos
    const vel = this.pos.sub(this.prevPos);

    // New position = current + velocity + acceleration*dt²
    const newPos = this.pos.add(vel).add(this.acc.mul(dt * dt));

    this.prevPos = this.pos;
    this.pos = newPos;
    this.acc = new Vec2(0, 0); // reset
  }

  // Derive velocity when needed
  getVelocity(dt) {
    return this.pos.sub(this.prevPos).div(dt);
  }
}
```

**Why Verlet is great:**
- Energy conserving (orbits stay stable)
- Constraints are easy (just move positions — velocity adjusts automatically)
- Simpler than RK4 (Runge-Kutta), nearly as stable
- Used in: cloth simulation, ragdolls, Hitman games

## 43.6 Common forces

```javascript
// Gravity (constant downward force)
function applyGravity(particle, g = 980) {
  particle.applyForce(new Vec2(0, particle.mass * g));
}

// Gravitational attraction between two bodies (planets)
function gravitationalForce(a, b, G = 1) {
  const dir = b.pos.sub(a.pos);
  const dist = Math.max(dir.length(), 10); // prevent infinite force at 0 distance
  const strength = (G * a.mass * b.mass) / (dist * dist);
  return dir.normalize().mul(strength);
}

// Spring force (Hooke's law: F = -k * stretch)
function springForce(a, b, restLength, stiffness, damping = 0.1) {
  const delta = b.pos.sub(a.pos);
  const dist = delta.length();
  const stretch = dist - restLength;

  const dir = delta.normalize();
  const springF = dir.mul(stiffness * stretch);

  // Damping (reduces oscillation)
  const relVel = b.vel.sub(a.vel);
  const dampF = dir.mul(relVel.dot(dir) * damping);

  return springF.add(dampF);
}

// Drag/Air resistance (F = -cv² in direction of velocity)
function dragForce(particle, coefficient = 0.01) {
  const speed = particle.vel.length();
  if (speed === 0) return new Vec2();
  const drag = particle.vel.normalize().mul(-coefficient * speed * speed);
  return drag;
}

// Mouse attraction (particles pulled toward cursor)
function mouseAttraction(particle, mousePos, strength = 500) {
  const dir = mousePos.sub(particle.pos);
  const dist = Math.max(dir.length(), 1);
  return dir.normalize().mul(strength / dist);
}
```

---

## PART 3: Collision Detection & Response

## 43.7 Circle-circle collision

```javascript
function circleCollision(a, b) {
  const dist = a.pos.distTo(b.pos);
  const minDist = a.radius + b.radius;
  return dist < minDist;
}

function resolveCircleCollision(a, b, restitution = 0.8) {
  const delta = b.pos.sub(a.pos);
  const dist = delta.length();
  const overlap = a.radius + b.radius - dist;

  if (overlap <= 0) return; // no collision

  const normal = delta.normalize();

  // Separate (push apart proportional to mass)
  const totalMass = a.mass + b.mass;
  a.pos = a.pos.sub(normal.mul(overlap * (b.mass / totalMass)));
  b.pos = b.pos.add(normal.mul(overlap * (a.mass / totalMass)));

  // Bounce (impulse-based)
  const relVel = a.vel.sub(b.vel);
  const velAlongNormal = relVel.dot(normal);

  if (velAlongNormal > 0) return; // moving apart already

  const impulse = -(1 + restitution) * velAlongNormal / totalMass;
  a.vel = a.vel.add(normal.mul(impulse * b.mass));
  b.vel = b.vel.sub(normal.mul(impulse * a.mass));
}
```

## 43.8 Boundary collision (walls)

```javascript
function enforceBounds(particle, width, height, restitution = 0.9) {
  // Floor
  if (particle.pos.y + particle.radius > height) {
    particle.pos.y = height - particle.radius;
    particle.vel.y *= -restitution;
  }
  // Ceiling
  if (particle.pos.y - particle.radius < 0) {
    particle.pos.y = particle.radius;
    particle.vel.y *= -restitution;
  }
  // Right wall
  if (particle.pos.x + particle.radius > width) {
    particle.pos.x = width - particle.radius;
    particle.vel.x *= -restitution;
  }
  // Left wall
  if (particle.pos.x - particle.radius < 0) {
    particle.pos.x = particle.radius;
    particle.vel.x *= -restitution;
  }
}
```

## 43.9 Spatial partitioning (many particles)

Checking every pair is O(n²). For 1000+ particles, use a grid:

```javascript
class SpatialGrid {
  constructor(cellSize, width, height) {
    this.cellSize = cellSize;
    this.cols = Math.ceil(width / cellSize);
    this.rows = Math.ceil(height / cellSize);
    this.grid = new Map();
  }

  clear() { this.grid.clear(); }

  getKey(x, y) {
    const col = Math.floor(x / this.cellSize);
    const row = Math.floor(y / this.cellSize);
    return `${col},${row}`;
  }

  insert(particle) {
    const key = this.getKey(particle.pos.x, particle.pos.y);
    if (!this.grid.has(key)) this.grid.set(key, []);
    this.grid.get(key).push(particle);
  }

  getNeighbors(particle) {
    const col = Math.floor(particle.pos.x / this.cellSize);
    const row = Math.floor(particle.pos.y / this.cellSize);
    const neighbors = [];

    // Check 3×3 surrounding cells
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const key = `${col + dx},${row + dy}`;
        if (this.grid.has(key)) {
          neighbors.push(...this.grid.get(key));
        }
      }
    }
    return neighbors;
  }
}
```



---

## PART 4: Build — Simulations

## 43.10 Particle system (Canvas 2D)

```javascript
// Complete runnable simulation
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
canvas.width = 800;
canvas.height = 600;

const particles = [];
const GRAVITY = new Vec2(0, 400);
const NUM_PARTICLES = 200;

// Create particles
for (let i = 0; i < NUM_PARTICLES; i++) {
  const p = new Particle(
    Math.random() * canvas.width,
    Math.random() * canvas.height * 0.3,
    1 + Math.random() * 3
  );
  p.vel = new Vec2(
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200
  );
  p.color = `hsl(${Math.random() * 360}, 70%, 60%)`;
  particles.push(p);
}

const grid = new SpatialGrid(50, canvas.width, canvas.height);

function update(dt) {
  // Apply forces
  for (const p of particles) {
    p.applyForce(GRAVITY.mul(p.mass)); // gravity
    p.applyForce(dragForce(p, 0.002)); // air resistance
  }

  // Integrate
  for (const p of particles) {
    p.update(dt);
  }

  // Collision detection (with spatial grid)
  grid.clear();
  for (const p of particles) grid.insert(p);

  for (const p of particles) {
    const neighbors = grid.getNeighbors(p);
    for (const other of neighbors) {
      if (p === other) continue;
      if (circleCollision(p, other)) {
        resolveCircleCollision(p, other, 0.7);
      }
    }
  }

  // Boundary
  for (const p of particles) {
    enforceBounds(p, canvas.width, canvas.height, 0.8);
  }
}

function render() {
  ctx.fillStyle = "rgba(15, 23, 42, 0.3)"; // trail effect
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (const p of particles) {
    ctx.beginPath();
    ctx.arc(p.pos.x, p.pos.y, p.radius, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  }
}

// Fixed timestep physics + variable render
let lastTime = performance.now();
const FIXED_DT = 1 / 60;
let accumulator = 0;

function loop(now) {
  const frameTime = Math.min((now - lastTime) / 1000, 0.1); // cap at 100ms
  lastTime = now;
  accumulator += frameTime;

  while (accumulator >= FIXED_DT) {
    update(FIXED_DT);
    accumulator -= FIXED_DT;
  }

  render();
  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
```

## 43.11 Cloth simulation (Verlet + constraints)

```javascript
class Cloth {
  constructor(width, height, spacing, x, y) {
    this.particles = [];
    this.constraints = [];
    this.cols = width;
    this.rows = height;
    this.spacing = spacing;

    // Create particles in a grid
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        const p = new VerletParticle(
          x + col * spacing,
          y + row * spacing,
          1
        );
        // Pin top row (fixed points)
        if (row === 0 && col % 4 === 0) p.pinned = true;
        this.particles.push(p);
      }
    }

    // Create constraints (horizontal + vertical links)
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        const idx = row * this.cols + col;
        // Horizontal
        if (col < this.cols - 1) {
          this.constraints.push({
            a: this.particles[idx],
            b: this.particles[idx + 1],
            length: spacing,
          });
        }
        // Vertical
        if (row < this.rows - 1) {
          this.constraints.push({
            a: this.particles[idx],
            b: this.particles[idx + this.cols],
            length: spacing,
          });
        }
      }
    }
  }

  update(dt) {
    const gravity = new Vec2(0, 980);

    // Apply gravity
    for (const p of this.particles) {
      if (!p.pinned) p.applyForce(gravity);
    }

    // Integrate (Verlet)
    for (const p of this.particles) {
      if (!p.pinned) p.update(dt);
    }

    // Solve constraints (multiple iterations for stiffness)
    for (let iter = 0; iter < 5; iter++) {
      for (const c of this.constraints) {
        this.solveConstraint(c);
      }
    }
  }

  solveConstraint(c) {
    const delta = c.b.pos.sub(c.a.pos);
    const dist = delta.length();
    if (dist === 0) return;

    const diff = (dist - c.length) / dist;
    const correction = delta.mul(0.5 * diff);

    if (!c.a.pinned) c.a.pos = c.a.pos.add(correction);
    if (!c.b.pinned) c.b.pos = c.b.pos.sub(correction);

    // Tear if stretched too far
    if (dist > c.length * 2) {
      c.broken = true;
    }
  }

  render(ctx) {
    ctx.strokeStyle = "#94a3b8";
    ctx.lineWidth = 1;

    for (const c of this.constraints) {
      if (c.broken) continue;
      ctx.beginPath();
      ctx.moveTo(c.a.pos.x, c.a.pos.y);
      ctx.lineTo(c.b.pos.x, c.b.pos.y);
      ctx.stroke();
    }
  }
}
```

**How cloth works:** Grid of Verlet particles connected by distance constraints. Each frame:
1. Apply gravity
2. Verlet integration (move particles)
3. Iteratively enforce constraints (push particles to correct distance)
4. More iterations = stiffer cloth

## 43.12 Planetary orbits (gravitational N-body)

```javascript
class SolarSystem {
  constructor() {
    this.bodies = [];
    // Sun
    this.bodies.push({
      pos: new Vec2(400, 300), vel: new Vec2(0, 0),
      mass: 10000, radius: 30, color: "#f59e0b", name: "Sun"
    });
    // Earth
    this.bodies.push({
      pos: new Vec2(400, 150), vel: new Vec2(200, 0),
      mass: 10, radius: 10, color: "#3b82f6", name: "Earth"
    });
    // Mars
    this.bodies.push({
      pos: new Vec2(400, 80), vel: new Vec2(150, 0),
      mass: 5, radius: 7, color: "#ef4444", name: "Mars"
    });
    // Moon (orbits Earth)
    this.bodies.push({
      pos: new Vec2(400, 135), vel: new Vec2(250, 0),
      mass: 1, radius: 4, color: "#9ca3af", name: "Moon"
    });
  }

  update(dt) {
    const G = 50; // gravitational constant

    // Calculate forces between all pairs
    for (let i = 0; i < this.bodies.length; i++) {
      for (let j = i + 1; j < this.bodies.length; j++) {
        const a = this.bodies[i];
        const b = this.bodies[j];

        const delta = b.pos.sub(a.pos);
        const dist = Math.max(delta.length(), 20);
        const force = (G * a.mass * b.mass) / (dist * dist);
        const dir = delta.normalize();

        // Apply to both bodies (Newton's 3rd law)
        const forceVec = dir.mul(force);
        a.vel = a.vel.add(forceVec.div(a.mass).mul(dt));
        b.vel = b.vel.sub(forceVec.div(b.mass).mul(dt));
      }
    }

    // Update positions
    for (const body of this.bodies) {
      body.pos = body.pos.add(body.vel.mul(dt));
    }
  }

  render(ctx) {
    // Draw trails (semi-transparent background)
    ctx.fillStyle = "rgba(15, 23, 42, 0.05)";
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    for (const body of this.bodies) {
      ctx.beginPath();
      ctx.arc(body.pos.x, body.pos.y, body.radius, 0, Math.PI * 2);
      ctx.fillStyle = body.color;
      ctx.fill();
    }
  }
}
```

---

## PART 5: Matter.js — When You Want a Ready-Made Engine

## 43.13 Setup

```bash
npm install matter-js
```

```javascript
import Matter from "matter-js";

const { Engine, Render, Runner, Bodies, Composite, Mouse, MouseConstraint } = Matter;

// Create engine
const engine = Engine.create();
const world = engine.world;

// Create renderer
const render = Render.create({
  element: document.getElementById("canvas-container"),
  engine: engine,
  options: {
    width: 800,
    height: 600,
    wireframes: false,
    background: "#0f172a",
  },
});

// Add bodies
const ground = Bodies.rectangle(400, 580, 800, 40, { isStatic: true, render: { fillStyle: "#334155" } });
const ball = Bodies.circle(400, 100, 30, { restitution: 0.8, render: { fillStyle: "#3b82f6" } });
const box = Bodies.rectangle(450, 50, 60, 60, { render: { fillStyle: "#f59e0b" } });

// Stack of boxes
const stack = Matter.Composites.stack(200, 0, 5, 5, 0, 0, (x, y) =>
  Bodies.rectangle(x, y, 40, 40, { render: { fillStyle: "#22c55e" } })
);

Composite.add(world, [ground, ball, box, stack]);

// Mouse interaction (drag objects)
const mouse = Mouse.create(render.canvas);
const mouseConstraint = MouseConstraint.create(engine, {
  mouse: mouse,
  constraint: { stiffness: 0.2, render: { visible: false } },
});
Composite.add(world, mouseConstraint);

// Run
Render.run(render);
Runner.run(Runner.create(), engine);
```

**Matter.js gives you for free:**
- Rigid body physics (rotation, friction, restitution)
- Polygon collision detection (not just circles)
- Constraints (springs, ropes, joints, hinges)
- Composites (car, stack, chain, ragdoll)
- Sleep (inactive objects stop computing — performance)
- Built-in renderer (or use your own with Canvas/Pixi/SVG)

## 43.14 Matter.js in React/Next.js

```tsx
"use client";

import { useEffect, useRef } from "react";
import Matter from "matter-js";

export default function PhysicsScene() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const engine = Matter.Engine.create();
    const render = Matter.Render.create({
      element: containerRef.current,
      engine: engine,
      options: { width: 800, height: 600, wireframes: false, background: "#0f172a" },
    });

    // Add objects...
    const ground = Matter.Bodies.rectangle(400, 580, 800, 40, { isStatic: true });
    Matter.Composite.add(engine.world, [ground]);

    // Spawn falling objects on click
    containerRef.current.addEventListener("click", (e) => {
      const rect = containerRef.current!.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const body = Matter.Bodies.circle(x, y, 20 + Math.random() * 20, {
        restitution: 0.6,
        render: { fillStyle: `hsl(${Math.random() * 360}, 70%, 60%)` },
      });
      Matter.Composite.add(engine.world, body);
    });

    Matter.Render.run(render);
    Matter.Runner.run(Matter.Runner.create(), engine);

    return () => {
      Matter.Render.stop(render);
      Matter.Engine.clear(engine);
      render.canvas.remove();
    };
  }, []);

  return <div ref={containerRef} className="w-full h-[600px]" />;
}
```

---

## PART 6: Rendering Comparison

## 43.15 Canvas 2D vs SVG vs WebGL for physics

| Renderer | Objects | FPS target | Use when |
|----------|---------|-----------|----------|
| **Canvas 2D** | 100-5000 | 60fps | Most 2D physics (particles, cloth, rigid bodies) |
| **SVG (D3)** | 10-500 | 60fps | Few objects with complex styling, tooltips, interaction |
| **WebGL (Three.js/Pixi.js)** | 10,000-100,000+ | 60fps | Massive particle systems, GPU-computed physics |
| **PixiJS** | 5,000-50,000 | 60fps | 2D sprites with WebGL acceleration |

**Canvas 2D is the default choice** for physics simulations because:
- Immediate mode (draw, forget — no DOM overhead)
- Fast enough for thousands of objects
- Simple API (arc, rect, line, fill, stroke)
- No GC pressure from DOM nodes (unlike SVG)

```javascript
// Canvas 2D — draw 1000 circles in <1ms
ctx.clearRect(0, 0, width, height);
for (const p of particles) {
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = p.color;
  ctx.fill();
}
```

## 43.16 Using D3 for physics VISUALISATION (not simulation)

D3 is good for visualising physics OUTPUT, not running the simulation:

```javascript
// Run physics with raw code, render with D3 (for interactivity + axes + tooltips)
import * as d3 from "d3";

const svg = d3.select("#viz").append("svg").attr("width", 800).attr("height", 600);

function renderWithD3(particles) {
  const circles = svg.selectAll("circle").data(particles, d => d.id);

  circles.enter()
    .append("circle")
    .attr("r", d => d.radius)
    .attr("fill", d => d.color)
    .merge(circles)
    .attr("cx", d => d.pos.x)
    .attr("cy", d => d.pos.y);

  circles.exit().remove();
}

// Physics loop updates positions, D3 renders them
// Good for < 200 objects. Beyond that, use Canvas.
```

---

## Summary

✅ Library choice: raw JS for learning, Matter.js for quick realistic physics, D3-force only for graph layouts
✅ Physics loop: forces → integrate → detect collisions → resolve → constrain
✅ Vector math: add, sub, mul, normalize, dot, distance
✅ Integration: Euler (simple) vs Verlet (stable, great for constraints)
✅ Forces: gravity, springs (Hooke's law), drag, gravitational attraction
✅ Collision: circle-circle detection + impulse-based response
✅ Spatial grid: O(n²) → O(n) collision checking for many particles
✅ Built: particle system, cloth simulation, planetary orbits
✅ Matter.js: ready-made engine with rigid bodies, polygons, constraints, mouse interaction
✅ Rendering: Canvas 2D (default), SVG for few objects with rich interaction, WebGL for massive systems

## Key takeaways

**D3-force is NOT a physics engine.** It's a graph layout tool. For real physics (gravity, collisions, rigid bodies), use raw code or Matter.js.

**Verlet integration is the sweet spot.** Simple to implement, stable (energy conserving), and constraints are trivial (just move positions). It's used in professional game physics for cloth, ragdolls, and ropes.

**Fixed timestep is non-negotiable.** Run physics at 60 steps/second regardless of frame rate. Variable timestep makes simulations non-deterministic and unstable (objects tunnel through walls at low FPS).

**Canvas 2D is your default renderer.** It handles thousands of objects at 60fps with no DOM overhead. Only switch to WebGL (Pixi.js/Three.js) if you need 10,000+ objects or GPU-computed physics.

---

→ [Back to Chapter 42: Rust](./42-RUST.md)
