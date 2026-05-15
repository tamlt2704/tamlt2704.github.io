# Chapter 9 — Particles & Effects

## Particle System

Particles add "juice" — explosions, dust, sparkles, trails.

```python
import pyxel
import random

pyxel.init(160, 120)

particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -0.5)
        self.life = random.randint(10, 30)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

def spawn_burst(x, y, count=10, color=9):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def update():
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        spawn_burst(pyxel.mouse_x, pyxel.mouse_y)

    for p in particles:
        p.update()
    particles[:] = [p for p in particles if not p.is_dead()]

def draw():
    pyxel.cls(0)
    for p in particles:
        pyxel.pset(int(p.x), int(p.y), p.color)
    pyxel.text(30, 5, f"Particles: {len(particles)}", 7)
    pyxel.text(30, 110, "Click to spawn!", 13)

pyxel.run(update, draw)
```

## Particle Variations

**Explosion (radial burst):**

```python
import math

def spawn_explosion(x, y, count=20):
    for i in range(count):
        angle = (i / count) * math.pi * 2
        speed = random.uniform(1, 3)
        p = Particle(x, y, random.choice([8, 9, 10]))
        p.vx = math.cos(angle) * speed
        p.vy = math.sin(angle) * speed
        particles.append(p)
```

**Trail (spawn behind moving object):**

```python
def spawn_trail(x, y):
    p = Particle(x, y, 13)
    p.vx = random.uniform(-0.3, 0.3)
    p.vy = random.uniform(0, 0.5)
    p.life = random.randint(5, 15)
    particles.append(p)

# In update, every few frames:
if pyxel.frame_count % 3 == 0:
    spawn_trail(px + 4, py + 8)  # behind player
```

**Dust (on landing):**

```python
def spawn_dust(x, y):
    for _ in range(5):
        p = Particle(x + random.randint(0, 8), y, 13)
        p.vx = random.uniform(-1, 1)
        p.vy = random.uniform(-1, 0)
        p.life = random.randint(5, 10)
        particles.append(p)
```

**Sparkle (floating, no gravity):**

```python
def spawn_sparkle(x, y):
    p = Particle(x, y, random.choice([7, 10, 12]))
    p.vx = random.uniform(-0.5, 0.5)
    p.vy = random.uniform(-0.5, 0.5)
    p.life = random.randint(15, 40)
    particles.append(p)

# Override gravity for sparkles — use a flag or subclass
```

## Fading Particles

Change color as life decreases:

```python
class FadingParticle(Particle):
    def __init__(self, x, y, colors):
        super().__init__(x, y, colors[0])
        self.colors = colors  # e.g. [10, 9, 8, 2] yellow→red→dark

    def current_color(self):
        progress = 1 - (self.life / 30)  # 0 to 1
        idx = min(int(progress * len(self.colors)), len(self.colors) - 1)
        return self.colors[idx]
```

Draw with: `pyxel.pset(int(p.x), int(p.y), p.current_color())`

## Bigger Particles

Use `rect` or `circ` instead of `pset` for larger particles:

```python
def draw():
    pyxel.cls(0)
    for p in particles:
        size = max(1, p.life // 10)
        pyxel.circ(int(p.x), int(p.y), size, p.color)
```

## Performance

Keep particle count reasonable for Pyxel:
- Cap at ~200 particles on screen
- Remove dead particles every frame
- Use `pset` (single pixel) for most particles — it's fastest

```python
MAX_PARTICLES = 200

def spawn_burst(x, y, count=10, color=9):
    for _ in range(count):
        if len(particles) < MAX_PARTICLES:
            particles.append(Particle(x, y, color))
```

## Exercise

Add particles to the coin game:
- Yellow sparkle burst when collecting a coin
- Dust puff when player changes direction
- Trail behind a moving enemy

## Next

Chapter 10: Managing game states (menu, playing, game over).
