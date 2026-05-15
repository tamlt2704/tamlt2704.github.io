# Chapter 0: First Window

[Next → Chapter 1: Models & Textures](chapter-01-models-textures.md)

---

## The Simplest 3D App

```python
from ursina import *

app = Ursina()
app.run()
```

That's a running 3D window. Empty, but running. 4 lines.

---

## Add Something

```python
from ursina import *

app = Ursina()

# Entity = anything in the 3D world
cube = Entity(model='cube', color=color.orange, scale=2)

app.run()
```

An orange cube floating in space. `Entity` is the building block of everything in Ursina — every object, every UI element, every light.

---

## Make It Spin

```python
from ursina import *

app = Ursina()
cube = Entity(model='cube', color=color.orange, scale=2)

def update():
    cube.rotation_y += 60 * time.dt  # 60 degrees per second

app.run()
```

`update()` is called every frame (like a game loop). `time.dt` is delta time — frame-rate independent.

---

## Entity Properties

Every Entity has these out of the box:

```python
e = Entity(
    model='cube',          # shape: cube, sphere, plane, quad, custom
    color=color.red,       # solid color
    texture='brick',       # image texture (overrides color)
    position=(0, 1, 0),    # x, y, z
    rotation=(0, 45, 0),   # pitch, yaw, roll
    scale=(2, 1, 1),       # width, height, depth
    collider='box',        # for physics/raycasting
)
```

---

## What You Learned

- `Ursina()` creates the app and window
- `Entity` is the universal building block
- `update()` runs every frame — put game logic here
- `time.dt` makes movement frame-rate independent
- Properties: model, color, texture, position, rotation, scale

---

[Next → Chapter 1: Models & Textures](chapter-01-models-textures.md)
