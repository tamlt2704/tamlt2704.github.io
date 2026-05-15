# Chapter 7: Collisions

Ursina provides simple collision detection through colliders. Assign a collider shape to an entity, then use `intersects()` or `raycast()` to detect overlaps and line-of-sight checks.

```python
from ursina import *

app = Ursina()

# Player with a box collider
player = Entity(model='cube', color=color.orange, position=(0, 0.5, 0),
                collider='box', scale=1)

# Collectible with a sphere collider
coin = Entity(model='sphere', color=color.yellow, position=(3, 0.5, 0),
              collider='sphere', scale=0.5)

# Wall
wall = Entity(model='cube', color=color.gray, position=(0, 1, 5),
              collider='box', scale=(6, 2, 0.5))

ground = Entity(model='plane', scale=20, collider='box', color=color.green)

def update():
    player.x += (held_keys['d'] - held_keys['a']) * 5 * time.dt

    # Check overlap
    hit = player.intersects()
    if hit.hit:
        if hit.entity == coin:
            print('Coin collected!')
            destroy(coin)

def input(key):
    if key == 'space':
        # Raycast forward from player
        ray = raycast(player.position, direction=(0, 0, 1), distance=10)
        if ray.hit:
            print(f'Hit {ray.entity} at distance {ray.distance:.1f}')

EditorCamera()
app.run()
```

## Key Points

- **collider='box'**: axis-aligned bounding box — fast and good for most shapes
- **collider='sphere'**: spherical collider — best for round objects
- **collider='mesh'**: uses the actual model geometry — accurate but slower
- **entity.intersects()**: returns hit info (`.hit`, `.entity`, `.point`)
- **raycast(origin, direction, distance)**: casts a ray and returns what it hits
- Colliders are invisible — they don't change how the entity looks

## What You Learned

- How to add colliders to entities for collision detection
- How to use `intersects()` for overlap checks
- How to use `raycast()` for line-of-sight and distance checks
- The three collider types and when to use each

---

[← Chapter 6: Lighting](chapter-06-lighting.md) | [Next → Chapter 8: Animation](chapter-08-animation.md)
