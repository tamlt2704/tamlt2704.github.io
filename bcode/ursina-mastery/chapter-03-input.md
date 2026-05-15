# Chapter 3: Input

Ursina handles keyboard and mouse input through two mechanisms: the `input()` function for single key presses, and `held_keys` for continuous input. The mouse provides screen position and world-space raycasting.

```python
from ursina import *

app = Ursina()

player = Entity(model='cube', color=color.orange, scale=1)

def input(key):
    """Called once per key press/release."""
    if key == 'space':
        player.color = color.random_color()
    if key == 'r':
        player.position = Vec3(0, 0, 0)
    if key == 'left mouse down':
        print(f'Clicked at screen: {mouse.position}')
        print(f'World point: {mouse.world_point}')

def update():
    """held_keys for continuous movement."""
    speed = 4 * time.dt
    player.x += held_keys['d'] * speed
    player.x -= held_keys['a'] * speed

EditorCamera()
app.run()
```

## Key Points

- **input(key)**: fires once when a key is pressed — key is a string like `'space'`, `'a'`, `'left mouse down'`
- **held_keys**: dictionary that returns 1 while a key is held, 0 otherwise
- **mouse.position**: normalized screen coordinates (-0.5 to 0.5)
- **mouse.world_point**: the 3D point in the scene the mouse is hovering over
- Key release events use the same name: `'space up'`, `'left mouse up'`

## What You Learned

- How to respond to single key presses with `input(key)`
- How to check continuously held keys with `held_keys`
- How to read mouse position in screen and world space
- The naming convention for keys and mouse buttons

---

[← Chapter 2: Transforms](chapter-02-transforms.md) | [Next → Chapter 4: Movement & Time](chapter-04-movement.md)
