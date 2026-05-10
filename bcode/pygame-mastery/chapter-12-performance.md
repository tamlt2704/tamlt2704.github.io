# Chapter 12: Performance — Keeping 60 FPS

[← Chapter 11: Save & Load](chapter-11-persistence.md) | [Chapter 13: Gamepad Support →](chapter-13-gamepad.md)

---

## The Problem

Wave 15. Thirty enemies on screen. Fifty bullets. Two hundred particles. The FPS counter reads 38. The game stutters. Inputs feel laggy. Rena: "It gets choppy when things get intense. That's exactly when it needs to be smooth."

Time to profile, identify bottlenecks, and optimize.

## Measuring First

Never optimize without measuring. Add an FPS counter:

```python
class FPSCounter:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.fps_history = []

    def update(self):
        fps = self.clock.get_fps()
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)

    def draw(self, surface):
        if not self.fps_history:
            return
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        color = (0, 255, 0) if avg_fps >= 55 else (255, 255, 0) if avg_fps >= 40 else (255, 0, 0)
        text = self.font.render(f"FPS: {avg_fps:.0f}", True, color)
        surface.blit(text, (SCREEN_WIDTH - 80, 10))
```

For detailed profiling:

```python
import time

class Profiler:
    def __init__(self):
        self.timings = {}

    def start(self, label):
        self.timings[label] = time.perf_counter()

    def end(self, label):
        if label in self.timings:
            elapsed = (time.perf_counter() - self.timings[label]) * 1000
            self.timings[label] = elapsed

    def report(self):
        for label, ms in self.timings.items():
            if isinstance(ms, float):
                print(f"  {label}: {ms:.2f}ms")


profiler = Profiler()

# In game loop:
profiler.start("update")
# ... update logic ...
profiler.end("update")

profiler.start("draw")
# ... draw logic ...
profiler.end("draw")

profiler.start("particles")
particles.update(dt)
profiler.end("particles")
```

Typical results on a slow frame:
```
  update: 2.1ms
  draw: 14.8ms    ← bottleneck
  particles: 3.2ms
  tilemap: 8.1ms  ← biggest draw cost
```

## Optimization 1: Culling Off-Screen Entities

Don't update or draw things the camera can't see:

```python
def is_on_screen(pos, camera, margin=64):
    """Check if a position is visible (with margin for partially visible sprites)."""
    screen_x = pos.x - camera.rect.left
    screen_y = pos.y - camera.rect.top
    return (-margin < screen_x < SCREEN_WIDTH + margin and
            -margin < screen_y < SCREEN_HEIGHT + margin)

# Only update/draw visible enemies:
for enemy in enemy_group:
    if is_on_screen(enemy.pos, camera):
        enemy.update(dt)
        enemy.draw(screen)
```

## Optimization 2: Pre-Rendered Tile Map

Drawing 500+ tiles every frame is expensive. Render the static tilemap to a surface once, then blit that single surface:

```python
class TileMap:
    def __init__(self, data, tile_size):
        # ... existing init ...

        # Pre-render the entire map to a surface
        self.surface = pygame.Surface(
            (self.pixel_width, self.pixel_height)
        )
        self._render_to_surface()

    def _render_to_surface(self):
        """Render all tiles once to an internal surface."""
        for row_idx, row in enumerate(self.data):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                if tile == 1:
                    pygame.draw.rect(self.surface, (60, 60, 80),
                                   (x, y, self.tile_size, self.tile_size))
                else:
                    pygame.draw.rect(self.surface, (25, 25, 35),
                                   (x, y, self.tile_size, self.tile_size))

    def draw(self, surface, camera_offset):
        """Blit the pre-rendered map (one blit instead of 500+)."""
        surface.blit(self.surface, (-camera_offset[0], -camera_offset[1]))
```

One blit instead of hundreds. Tilemap rendering goes from 8ms to 0.3ms.

For very large maps, blit only the visible portion:

```python
def draw(self, surface, camera_offset):
    visible_area = pygame.Rect(camera_offset[0], camera_offset[1],
                               SCREEN_WIDTH, SCREEN_HEIGHT)
    surface.blit(self.surface, (0, 0), visible_area)
```

## Optimization 3: Object Pooling

Creating and destroying objects (bullets, particles) causes garbage collection spikes. Reuse objects instead:

```python
class BulletPool:
    def __init__(self, size=200):
        self.pool = [Bullet() for _ in range(size)]
        self.active = []

    def spawn(self, pos, velocity):
        if self.pool:
            bullet = self.pool.pop()
            bullet.activate(pos, velocity)
            self.active.append(bullet)
            return bullet
        return None  # Pool exhausted

    def update(self, dt):
        for bullet in self.active[:]:  # Copy list for safe removal
            bullet.update(dt)
            if not bullet.alive:
                self.active.remove(bullet)
                bullet.deactivate()
                self.pool.append(bullet)

    def draw(self, surface, camera_offset):
        for bullet in self.active:
            bullet.draw(surface, camera_offset)


class Bullet:
    def __init__(self):
        self.alive = False
        self.pos = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

    def activate(self, pos, velocity):
        self.alive = True
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)

    def deactivate(self):
        self.alive = False
```

No allocations during gameplay. No GC spikes.

## Optimization 4: Spatial Hashing for Collisions

From Chapter 4's preview — now we need it:

```python
class SpatialGrid:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.cells = {}

    def clear(self):
        self.cells.clear()

    def insert(self, entity):
        key = (int(entity.pos.x // self.cell_size),
               int(entity.pos.y // self.cell_size))
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(entity)

    def get_nearby(self, pos):
        cx = int(pos.x // self.cell_size)
        cy = int(pos.y // self.cell_size)
        nearby = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                key = (cx + dx, cy + dy)
                if key in self.cells:
                    nearby.extend(self.cells[key])
        return nearby


# Each frame:
grid = SpatialGrid(64)
grid.clear()
for enemy in enemies:
    grid.insert(enemy)

# Check bullet collisions:
for bullet in bullets:
    nearby_enemies = grid.get_nearby(bullet.pos)
    for enemy in nearby_enemies:  # Only check nearby, not ALL
        if circle_collide(bullet.pos, 4, enemy.pos, enemy.radius):
            # Hit!
            pass
```

100 bullets × 30 enemies = 3,000 checks → ~300 checks with spatial hashing.

## Optimization 5: Dirty Rect Rendering

Instead of redrawing the entire screen every frame, only redraw areas that changed:

```python
# Track dirty rectangles
dirty_rects = []

# When something moves, mark its old and new position as dirty
dirty_rects.append(entity.old_rect)
dirty_rects.append(entity.rect)

# Only update dirty areas
pygame.display.update(dirty_rects)  # Instead of pygame.display.flip()
```

This is complex to implement correctly (you need to track every moving entity's previous position). For Void Runners with many moving objects, full-screen redraw with the pre-rendered tilemap is simpler and fast enough.

## Optimization 6: Reduce Draw Calls

```python
# SLOW — individual draw calls for each particle
for particle in particles:
    pygame.draw.circle(screen, particle.color, particle.pos, particle.size)

# FASTER — batch similar operations
# Pre-render particle images at different sizes
particle_images = {}
for size in range(1, 10):
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 200, 50), (size, size), size)
    particle_images[size] = surf

# Blit pre-rendered images (faster than draw.circle)
for particle in particles:
    size_key = max(1, min(9, int(particle.size)))
    screen.blit(particle_images[size_key], 
                (int(particle.pos.x) - size_key, int(particle.pos.y) - size_key))
```

## Performance Budget

At 60 FPS, you have 16.6ms per frame. Budget it:

| System | Budget | Typical |
|---|---|---|
| Input | 0.1ms | 0.05ms |
| Update (entities) | 2ms | 1.5ms |
| Update (particles) | 1ms | 0.8ms |
| Collision detection | 2ms | 1.2ms |
| Draw (tilemap) | 1ms | 0.3ms (pre-rendered) |
| Draw (entities) | 3ms | 2.5ms |
| Draw (particles) | 2ms | 1.5ms |
| Draw (UI) | 1ms | 0.5ms |
| Display flip | 1ms | 0.8ms |
| **Total** | **<16.6ms** | **~9.2ms** |

If you're under budget, don't optimize further. Premature optimization wastes development time.

## What You Learned

- **Profile first** — measure before optimizing
- **Culling** — skip off-screen entities entirely
- **Pre-rendering** — render static content once to a surface
- **Object pooling** — reuse objects instead of create/destroy
- **Spatial hashing** — only check nearby entities for collision
- **Batch rendering** — pre-rendered images faster than draw calls
- **Performance budget** — 16.6ms per frame, allocate wisely

The game runs at 60 FPS even during intense moments. Wave 15 with 30 enemies is smooth. The optimization work is invisible to players — they just notice it doesn't stutter.

Next: gamepad support, because not everyone wants to use keyboard and mouse.

---

[← Chapter 11: Save & Load](chapter-11-persistence.md) | [Chapter 13: Gamepad Support →](chapter-13-gamepad.md)
