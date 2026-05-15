# Chapter 1: Models & Textures

Every 3D object in Ursina is an `Entity` with a model and optional texture. Ursina ships with built-in models and textures so you can prototype instantly without any external assets.

```python
from ursina import *

app = Ursina()

# Built-in models with different textures
cube = Entity(model='cube', texture='brick', position=(-3, 0, 0))
sphere = Entity(model='sphere', texture='white_cube', position=(0, 0, 0))
plane = Entity(model='plane', texture='grass', scale=10, y=-1)
cylinder = Entity(model='cylinder', color=color.azure, position=(3, 0, 0))
cone = Entity(model='cone', color=color.orange, position=(1.5, 1, 0))
quad = Entity(model='quad', texture='brick', position=(-1.5, 1, 0))

# Custom texture from file (place image in your project folder)
# custom = Entity(model='cube', texture='my_image.png')

EditorCamera()
app.run()
```

## Key Points

- **Built-in models**: `'cube'`, `'sphere'`, `'plane'`, `'quad'`, `'cylinder'`, `'cone'`
- **Built-in textures**: `'brick'`, `'grass'`, `'white_cube'`, `'shore'`
- **Custom textures**: pass any image filename as a string — Ursina looks in your project folder
- **color vs texture**: if you set both, texture takes priority. Use `color` for flat shading when no texture is needed
- **scale**: adjusts model size — a single float scales uniformly, a `Vec3` scales per axis

## What You Learned

- How to create 3D entities with built-in models
- How to apply built-in and custom textures
- The relationship between color and texture on an entity
- All six built-in model primitives available in Ursina

---

[Next → Chapter 2: Transforms](chapter-02-transforms.md)
