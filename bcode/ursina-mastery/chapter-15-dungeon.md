# Chapter 15: Full Game — Dungeon Crawler

Time to combine everything. This capstone builds a playable dungeon crawler with textured walls, enemies, health, pickups, and a win condition — all in about 60 lines.

```python
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import uniform, choice

app = Ursina()

# --- Scene ---
Sky(color=color.black)
ground = Entity(model='plane', texture='grass', scale=30, collider='box')

# Dungeon walls
wall_positions = [
    (-5,1,5), (5,1,5), (-5,1,-5), (5,1,-5),
    (0,1,8), (-8,1,0), (8,1,0), (0,1,-8),
    (-3,1,2), (3,1,-2), (6,1,3), (-6,1,-3),
]
for pos in wall_positions:
    Entity(model='cube', texture='brick', scale=(2,2,2),
           position=pos, collider='box')

# --- Enemies ---
enemies = []
for i in range(5):
    e = Entity(model='cube', color=color.red, scale=0.8,
               position=(uniform(-8,8), 0.4, uniform(-8,8)), collider='box')
    e.speed = uniform(1, 2)
    enemies.append(e)

# --- Pickups ---
pickups = []
for i in range(3):
    p = Entity(model='sphere', color=color.yellow, scale=0.3,
               position=(uniform(-7,7), 0.3, uniform(-7,7)), collider='sphere')
    pickups.append(p)

# --- Player ---
player = FirstPersonController(speed=5)
health = 100
score = 0
health_bar = HealthBar(max_value=100, bar_color=color.red)
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)

# --- Game Loop ---
def update():
    global health, score
    for e in enemies:
        # Enemies drift toward player
        direction = (player.position - e.position).normalized()
        e.position += direction * e.speed * time.dt
        e.rotation_y += 100 * time.dt
        # Damage on contact
        if distance(e.position, player.position) < 1.2:
            health -= 20 * time.dt
            health_bar.value = health

    # Pickup collection
    for p in pickups[:]:
        if distance(p.position, player.position) < 1:
            score += 10
            score_text.text = f'Score: {score}'
            destroy(p)
            pickups.remove(p)

    # Game over
    if health <= 0:
        Text(text='GAME OVER', scale=5, origin=(0,0), color=color.red)
        application.pause()

def input(key):
    # Attack: destroy nearest enemy
    if key == 'left mouse down':
        for e in enemies[:]:
            if distance(e.position, player.position) < 2.5:
                destroy(e)
                enemies.remove(e)
                break

app.run()
```

## Key Points

- **FirstPersonController**: instant FPS movement + mouse look
- **Colliders on walls**: prevent player from walking through
- **Enemy AI**: simple "move toward player" with `(target - self).normalized()`
- **Pickups**: check distance, destroy on contact, update score
- **Health system**: HealthBar + damage over time on enemy contact
- **Attack**: left-click destroys nearest enemy within range

## What You Built (Course Summary)

Over 15 chapters you learned the complete Ursina toolkit:

- **Ch 1-2**: Models, textures, transforms, parenting
- **Ch 3-4**: Input handling, frame-rate independent movement
- **Ch 5-6**: Camera controllers, lighting
- **Ch 7-8**: Collision detection, animation tweening
- **Ch 9-10**: UI elements, audio playback
- **Ch 11-12**: Terrain generation, particle effects
- **Ch 13-14**: Networking basics, building executables
- **Ch 15**: Combining it all into a complete game

You now have the foundation to build 3D games, simulations, and interactive experiences with Ursina.

---

[← Chapter 14: Build & Distribute](chapter-14-build.md)
