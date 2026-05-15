# Pymunk + Manim — Physics Animations for Teaching

A narrative-driven course on combining Pymunk (2D physics engine) with Manim (animation engine) to create beautiful physics simulations for educational videos. Balls bounce, pendulums swing, gears turn — all rendered as publication-quality animations.

## The Idea

Pymunk simulates the physics. Manim renders the frames. Together: accurate, beautiful physics animations.

```
Pymunk (physics)          Manim (rendering)
┌──────────────┐         ┌──────────────────┐
│ Bodies       │ ──────→ │ Circles, Lines   │
│ Shapes      │  sync   │ Animations       │
│ Constraints │ each    │ Camera, Colors   │
│ Space.step()│ frame   │ Scene.play()     │
└──────────────┘         └──────────────────┘
```

## Episodes

| # | Title | Pymunk Concept | Manim Concept |
|---|---|---|---|
| 00 | [Setup & First Ball](chapter-00-setup.md) | Space, Body, Circle shape | Scene, Dot, updaters |
| 01 | [Gravity & Bouncing](chapter-01-gravity.md) | Gravity, elasticity, static bodies | Traced paths, color |
| 02 | [Multiple Bodies](chapter-02-bodies.md) | Body types (dynamic/static/kinematic) | VGroup, batch sync |
| 03 | [Constraints: Joints](chapter-03-joints.md) | PinJoint, SlideJoint, DampedSpring | Lines between bodies |
| 04 | [Pendulum](chapter-04-pendulum.md) | Pivot constraint, damping | Arc traces, energy viz |
| 05 | [Collisions & Callbacks](chapter-05-collisions.md) | Collision handlers, categories | Flash on impact, sound |
| 06 | [Shapes: Polygons & Segments](chapter-06-shapes.md) | Poly, Segment, convex hulls | Polygon mobjects |
| 07 | [Forces & Impulses](chapter-07-forces.md) | apply_force, apply_impulse, torque | Arrows showing forces |
| 08 | [Friction & Materials](chapter-08-friction.md) | friction, surface_velocity | Ramps, sliding blocks |
| 09 | [Ragdoll / Chain](chapter-09-chain.md) | Multiple joints, body chains | Connected segments |
| 10 | [Gears & Motors](chapter-10-gears.md) | SimpleMotor, GearJoint | Rotating shapes |
| 11 | [Fluid-like Particles](chapter-11-particles.md) | Many small circles, no friction | Particle effects |
| 12 | [Full Scene: Rube Goldberg](chapter-12-rube-goldberg.md) | Everything combined | Cinematic camera |

## Setup

```bash
uv python install 3.12
uv init pymunk-manim --python 3.12
cd pymunk-manim
uv add pymunk manim
```

## Philosophy

Each chapter: learn ONE pymunk concept, render it with manim. Code stays short (~20 lines per function). Physics first, then beauty.
