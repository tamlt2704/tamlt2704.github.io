# Chapter 12: Particles & Effects

Ursina doesn't have a built-in particle system, but you can create convincing effects by spawning many small entities with random velocities and auto-destroying them. This pattern is simple and flexible.

```python
from ursina import *
from random import uniform

app = Ursina()

def spawn_particles(position, count=20):
    """Spawn burst of particles at a position."""
    for i in range(count):
        p = Entity(
            model='quad', color=color.yellow,
            scale=uniform(0.05, 0.15),
            position=position,
            billboard=True  # always faces camera
        )
        # Random velocity
        p.velocity = Vec3(uniform(-2, 2), uniform(1, 4), uniform(-2, 2))
        p.fade_out(duration=0.8)
        destroy(p, delay=1)

def update():
    # Move all particles by their velocity
    for e in scene.entities:
        if hasattr(e, 'velocity'):
            e.position += e.velocity * time.dt
            e.velocity.y -= 5 * time.dt  # gravity

def input(key):
    if key == 'space':
        spawn_particles(Vec3(0, 1, 0))

ground = Entity(model='plane', texture='grass', scale=20)
Text(text='Press SPACE for particles', position=(-0.4, 0.45))
EditorCamera()
app.run()
```

## Key Points

- **Particle pattern**: spawn many small entities → give random velocity → destroy after delay
- **destroy(entity, delay=N)**: auto-removes entity after N seconds
- **entity.fade_out(duration)**: smoothly fades alpha to 0
- **billboard=True**: entity always faces the camera — perfect for flat particles
- Apply gravity by subtracting from velocity.y each frame
- Keep particle count reasonable (20-50 per burst) for performance

## What You Learned

- How to create particle effects without a dedicated particle system
- How to use `destroy()` with delay for auto-cleanup
- How to apply physics (gravity) to particles manually
- The billboard trick for camera-facing quads
- How `fade_out()` creates smooth disappearing effects

---

[← Chapter 11: Terrain & Sky](chapter-11-terrain.md) | [Next → Chapter 13: Networking](chapter-13-networking.md)
