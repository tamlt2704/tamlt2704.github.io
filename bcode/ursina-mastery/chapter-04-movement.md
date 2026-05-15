# Chapter 4: Movement & Time

Smooth movement requires frame-rate independence. Ursina provides `time.dt` (delta time) — the seconds elapsed since the last frame. Multiply all movement by `time.dt` so your game runs the same speed on any machine.

```python
from ursina import *

app = Ursina()

player = Entity(model='cube', color=color.orange, position=(0, 0, 0))
ground = Entity(model='plane', texture='grass', scale=20, y=-0.5)
speed = 5

def update():
    """WASD movement, frame-rate independent."""
    move = Vec3(
        held_keys['d'] - held_keys['a'],
        0,
        held_keys['w'] - held_keys['s']
    ).normalized() * speed * time.dt

    player.position += move

EditorCamera()
app.run()
```

## Key Points

- **time.dt**: seconds since last frame (~0.016 at 60 FPS)
- Always multiply speed by `time.dt` for consistent movement
- **Vec3.normalized()**: keeps diagonal movement the same speed as cardinal
- The `update()` function runs every frame automatically
- `held_keys['key']` returns 1 (held) or 0 (not held) — perfect for arithmetic

## What You Learned

- Why `time.dt` is essential for frame-rate independent movement
- How to implement WASD movement in ~15 lines
- How to normalize diagonal movement so it isn't faster
- That `update()` is Ursina's main game loop function

---

[← Chapter 3: Input](chapter-03-input.md) | [Next → Chapter 5: Camera](chapter-05-camera.md)
