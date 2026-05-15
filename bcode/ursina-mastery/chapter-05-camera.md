# Chapter 5: Camera

Ursina provides ready-made camera controllers. `FirstPersonController` gives you FPS-style movement with mouse look and WASD built in. `EditorCamera` gives orbit, pan, and zoom for inspecting scenes.

```python
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Scene
ground = Entity(model='plane', texture='grass', scale=50, collider='box')
for x in range(-5, 6, 3):
    Entity(model='cube', texture='brick', position=(x, 0.5, 5), collider='box')

# FPS camera with built-in WASD + mouse look + gravity
player = FirstPersonController()
player.speed = 6
player.mouse_sensitivity = Vec2(80, 80)

# Or use EditorCamera for scene inspection:
# EditorCamera()  # right-click drag to orbit, scroll to zoom

# Manual camera control (without a controller):
# camera.position = Vec3(0, 10, -20)
# camera.rotation_x = 30
# camera.fov = 90

app.run()
```

## Key Points

- **FirstPersonController**: WASD movement, mouse look, gravity, jumping (space) — all built in
- **EditorCamera**: orbit (right-drag), pan (middle-drag), zoom (scroll) — great for debugging
- **camera.position / camera.rotation**: manual control when you need custom behavior
- **camera.fov**: field of view in degrees (default 60)
- FirstPersonController needs a ground with a collider to stand on

## What You Learned

- How to use FirstPersonController for instant FPS gameplay
- How to use EditorCamera for scene inspection
- How to manually position and rotate the camera
- That FirstPersonController requires colliders on walkable surfaces

---

[← Chapter 4: Movement & Time](chapter-04-movement.md) | [Next → Chapter 6: Lighting](chapter-06-lighting.md)
