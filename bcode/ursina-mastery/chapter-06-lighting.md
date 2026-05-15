# Chapter 6: Lighting

Ursina supports directional, point, and ambient lights. Lights affect how models are shaded, giving your scene depth and atmosphere. Without lights, entities use flat unlit shading by default.

```python
from ursina import *

app = Ursina()

# Scene objects
ground = Entity(model='plane', color=color.gray, scale=20)
cube = Entity(model='cube', color=color.white, position=(0, 0.5, 0))
sphere = Entity(model='sphere', color=color.white, position=(3, 1, 0))

# Directional light (like the sun)
sun = DirectionalLight(y=3, rotation=(45, 45, 0))
sun.color = color.rgb(255, 245, 230)

# Point light (like a lamp)
lamp = PointLight(position=(-3, 2, 0), color=color.orange)

# Ambient light (fills in shadows)
ambient = AmbientLight(color=color.rgba(100, 100, 100, 255))

# Enable shadows (experimental, GPU-dependent)
# sun.shadow = True

EditorCamera()
app.run()
```

## Key Points

- **DirectionalLight**: parallel rays like sunlight — rotation controls direction
- **PointLight**: emits in all directions from a position — good for lamps, torches
- **AmbientLight**: uniform fill light — prevents pure-black shadows
- **Shadows**: set `light.shadow = True` (experimental, may not work on all GPUs)
- Without any light, Ursina renders entities with flat unlit colors

## What You Learned

- How to add directional, point, and ambient lights to a scene
- How light rotation and position affect shading
- How ambient light fills in dark areas
- That shadows are experimental and GPU-dependent in Ursina

---

[← Chapter 5: Camera](chapter-05-camera.md) | [Next → Chapter 7: Collisions](chapter-07-collisions.md)
