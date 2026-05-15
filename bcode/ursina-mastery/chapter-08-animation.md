# Chapter 8: Animation

Ursina has built-in tweening for position, rotation, and scale. Chain animations with `Sequence()` and control easing with curves. No external libraries needed.

```python
from ursina import *

app = Ursina()

cube = Entity(model='cube', color=color.orange, position=(0, 0.5, 0))
sphere = Entity(model='sphere', color=color.azure, position=(3, 0.5, 0))

def input(key):
    if key == '1':
        # Animate position over 1 second with easing
        cube.animate_position(Vec3(0, 3, 0), duration=1, curve=curve.out_bounce)

    if key == '2':
        # Animate rotation
        cube.animate_rotation(Vec3(0, 360, 0), duration=1.5)

    if key == '3':
        # Animate scale
        sphere.animate_scale(Vec3(2, 2, 2), duration=0.5, curve=curve.in_out_expo)

    if key == '4':
        # Sequence: chain multiple animations
        s = Sequence(
            Func(setattr, cube, 'color', color.red),
            cube.animate_position(Vec3(-3, 0.5, 0), duration=1),
            cube.animate_position(Vec3(0, 0.5, 0), duration=1),
            Func(setattr, cube, 'color', color.orange),
        )

ground = Entity(model='plane', texture='grass', scale=20)
EditorCamera()
app.run()
```

## Key Points

- **animate_position(target, duration)**: smoothly moves entity to target
- **animate_rotation(target, duration)**: smoothly rotates entity
- **animate_scale(target, duration)**: smoothly scales entity
- **curve=curve.out_bounce**: easing function — also `in_out_expo`, `linear`, `in_quad`, etc.
- **Sequence()**: chains animations and function calls in order
- **Func()**: wraps a function call inside a Sequence

## What You Learned

- How to animate position, rotation, and scale with one line each
- How to apply easing curves for natural-feeling motion
- How to chain animations with Sequence
- How to insert function calls between animations with Func

---

[← Chapter 7: Collisions](chapter-07-collisions.md) | [Next → Chapter 9: UI](chapter-09-ui.md)
