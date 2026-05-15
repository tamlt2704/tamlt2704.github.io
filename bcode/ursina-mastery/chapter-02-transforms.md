# Chapter 2: Transforms

Every entity has a position, rotation, and scale. These three properties define where an object is, how it's oriented, and how big it is. Parenting lets you group objects so children move with their parent.

```python
from ursina import *

app = Ursina()

# Position, rotation, scale are all Vec3
parent_cube = Entity(model='cube', color=color.blue, position=(0, 0, 0))
parent_cube.rotation = Vec3(0, 45, 0)
parent_cube.scale = Vec3(2, 0.5, 2)

# Child moves relative to parent
child_sphere = Entity(model='sphere', color=color.red, position=(2, 1, 0))
child_sphere.parent = parent_cube  # now child orbits with parent

# World vs local position
print(f'Local position: {child_sphere.position}')
print(f'World position: {child_sphere.world_position}')

# Uniform scale with a single float
marker = Entity(model='cone', color=color.yellow, position=(-3, 0, 0), scale=0.5)

EditorCamera()
app.run()
```

## Key Points

- **position**: `Vec3(x, y, z)` — y is up in Ursina
- **rotation**: `Vec3(pitch, yaw, roll)` in degrees
- **scale**: `Vec3(x, y, z)` or a single float for uniform scaling
- **Parenting**: set `child.parent = parent_entity` — child's position becomes relative to parent
- **world_position**: the actual global position after parenting is applied
- Changing the parent's transform automatically moves all children

## What You Learned

- How to set position, rotation, and scale on entities
- The difference between local and world position
- How parenting works to create object hierarchies
- That a single float scale applies uniformly to all axes

---

[← Chapter 1: Models & Textures](chapter-01-models-textures.md) | [Next → Chapter 3: Input](chapter-03-input.md)
