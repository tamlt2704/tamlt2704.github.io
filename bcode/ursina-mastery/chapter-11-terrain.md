# Chapter 11: Terrain & Sky

Ursina generates terrain from heightmap images and provides a one-line skybox. Combine them for outdoor environments with minimal code.

```python
from ursina import *

app = Ursina()

# Sky (instant skybox)
sky = Sky()

# Terrain from heightmap
# Place a grayscale 'heightmap.png' in your project folder
# White = high, black = low
terrain = Entity(
    model=Terrain('heightmap', skip=4),  # skip=4 for lower poly count
    scale=(100, 10, 100),                # x/z spread, y height
    texture='grass',
    collider='mesh'                      # walk on it
)

# A few trees on the terrain
from random import uniform
for i in range(10):
    Entity(
        model='cube', color=color.dark_green,
        scale=(0.5, 2, 0.5),
        position=(uniform(-30, 30), 1, uniform(-30, 30))
    )

# FPS controller to walk around
from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController()

app.run()
```

## Key Points

- **Terrain('heightmap')**: generates mesh from a grayscale image (no extension needed)
- **scale=(x, y, z)**: x/z control spread, y controls height exaggeration
- **skip=4**: reduces vertex count for performance (higher = fewer polygons)
- **Sky()**: adds a default skybox with one line
- Add `collider='mesh'` to terrain so the player can walk on it
- Place heightmap images in your project root folder

## What You Learned

- How to generate 3D terrain from a heightmap image
- How to add a skybox with `Sky()`
- How to control terrain scale and polygon density
- How to combine terrain with FirstPersonController for exploration

---

[← Chapter 10: Audio](chapter-10-audio.md) | [Next → Chapter 12: Particles & Effects](chapter-12-particles.md)
