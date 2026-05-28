# Chapter 0: Physics Simulations with Matter.js

## Chapters

- [Chapter 0: Overview (this page)](/blog/physics-matterjs/chapter-00-overview)
- [Chapter 1: Setup & First World](/blog/physics-matterjs/chapter-01-setup)
- [Chapter 2: Bodies & Properties](/blog/physics-matterjs/chapter-02-bodies)
- [Chapter 3: Forces & Gravity](/blog/physics-matterjs/chapter-03-forces)
- [Chapter 4: Constraints & Joints](/blog/physics-matterjs/chapter-04-constraints)
- [Chapter 5: Collisions & Events](/blog/physics-matterjs/chapter-05-collisions)
- [Chapter 6: Advanced Demos](/blog/physics-matterjs/chapter-06-advanced)

---

## What is Matter.js?

Matter.js is a 2D rigid body physics engine for the web. It simulates real-world physics — gravity, collisions, friction, springs — and renders them on a canvas.

```
npm install matter-js
```

## Why Matter.js for Learning Physics?

- **Visual** — see physics concepts in action immediately
- **Interactive** — drag objects, change parameters, observe results
- **Simple API** — create a world in 10 lines of code
- **Real physics** — uses the same math as professional simulations

## What You'll Build

| Chapter | Topic             | Physics Concept                                 |
| ------- | ----------------- | ----------------------------------------------- |
| 1       | Engine + Renderer | World setup, game loop                          |
| 2       | Bodies            | Mass, density, shape, restitution, friction     |
| 3       | Forces            | Gravity, applied forces, velocity, acceleration |
| 4       | Constraints       | Springs, pendulums, joints, ropes               |
| 5       | Collisions        | Detection, events, categories, filtering        |
| 6       | Advanced          | Newton's cradle, slingshot, stacking, ragdolls  |

## The Architecture

```
Matter.js Core Concepts:

Engine ─── runs the physics simulation (timestep loop)
  │
  ├── World ─── contains all bodies and constraints
  │     ├── Bodies ─── circles, rectangles, polygons
  │     ├── Constraints ─── springs, ropes, pins
  │     └── Composites ─── groups of bodies
  │
  ├── Render ─── draws everything to canvas
  │
  └── Runner ─── calls Engine.update() at 60fps
```

## Prerequisites

- Next.js project with TypeScript
- Basic understanding of coordinates (x, y)
- Curiosity about how things fall, bounce, and collide

## Try It

Visit [/games/physics](/games/physics) to play with the interactive demos as you read.

---

[Chapter 1: Setup & First World →](/blog/physics-matterjs/chapter-01-setup)
