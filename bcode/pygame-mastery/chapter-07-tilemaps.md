# Chapter 7: Tile Maps — Building Worlds

[← Chapter 6: Sound & Music](chapter-06-audio.md) | [Chapter 8: Enemies That Think →](chapter-08-enemies.md)

---

## The Problem

Void Runners takes place in procedurally connected rooms. But right now, there's one room — an empty 800×600 rectangle. No walls. No corridors. No doors. No world.

You could hard-code level layouts:

```python
walls = [
    pygame.Rect(0, 0, 800, 16),      # Top wall
    pygame.Rect(0, 584, 800, 16),     # Bottom wall
    pygame.Rect(0, 0, 16, 600),       # Left wall
    pygame.Rect(784, 0, 16, 600),     # Right wall
    pygame.Rect(200, 200, 16, 200),   # Interior wall
]
```

That works for one room. For 50 rooms with different layouts, it's unmaintainable. You need a data-driven approach: **tile maps**.

## What's a Tile Map?

A tile map is a grid where each cell references a tile from a tileset:

```
Tileset (image):
┌──┬──┬──┬──┐
│ 0│ 1│ 2│ 3│  0=floor, 1=wall, 2=door, 3=pit
└──┴──┴──┴──┘

Map (2D array):
1 1 1 2 1 1 1
1 0 0 0 0 0 1
1 0 0 0 0 0 1
1 0 0 0 0 0 1
1 1 1 1 1 1 1
```

Each number maps to a tile image. The renderer draws the correct tile at each grid position. Change the numbers, change the level.

## Building a Simple Tile Map

```python
TILE_SIZE = 32

# Map data: 0=floor, 1=wall
level_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
```

## The TileMap Class

```python
class TileMap:
    def __init__(self, data, tile_size=32):
        self.data = data
        self.tile_size = tile_size
        self.width = len(data[0])
        self.height = len(data)
        self.pixel_width = self.width * tile_size
        self.pixel_height = self.height * tile_size

        # Pre-build wall rects for collision
        self.wall_rects = []
        for row_idx, row in enumerate(data):
            for col_idx, tile in enumerate(row):
                if tile == 1:  # Wall
                    rect = pygame.Rect(
                        col_idx * tile_size,
                        row_idx * tile_size,
                        tile_size, tile_size
                    )
                    self.wall_rects.append(rect)

    def get_tile(self, col, row):
        if 0 <= col < self.width and 0 <= row < self.height:
            return self.data[row][col]
        return 1  # Out of bounds = wall

    def is_wall(self, col, row):
        return self.get_tile(col, row) == 1

    def world_to_grid(self, x, y):
        """Convert pixel coordinates to grid coordinates."""
        return int(x // self.tile_size), int(y // self.tile_size)

    def draw(self, surface, camera_offset=(0, 0)):
        for row_idx, row in enumerate(self.data):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size - camera_offset[0]
                y = row_idx * self.tile_size - camera_offset[1]

                # Skip tiles outside the screen
                if x < -self.tile_size or x > SCREEN_WIDTH:
                    continue
                if y < -self.tile_size or y > SCREEN_HEIGHT:
                    continue

                if tile == 1:
                    pygame.draw.rect(surface, (60, 60, 80),
                                   (x, y, self.tile_size, self.tile_size))
                else:
                    pygame.draw.rect(surface, (25, 25, 35),
                                   (x, y, self.tile_size, self.tile_size))
```

## Tile-Based Collision

The player shouldn't walk through walls. Check collision against wall tiles:

```python
def resolve_tilemap_collision(entity_pos, entity_size, tilemap, velocity, dt):
    """Move entity and resolve collisions with tilemap walls."""
    # Try moving on X axis
    new_x = entity_pos.x + velocity.x * dt
    entity_rect = pygame.Rect(int(new_x), int(entity_pos.y), entity_size, entity_size)

    for wall in tilemap.wall_rects:
        if entity_rect.colliderect(wall):
            if velocity.x > 0:  # Moving right
                new_x = wall.left - entity_size
            elif velocity.x < 0:  # Moving left
                new_x = wall.right
            break

    # Try moving on Y axis
    new_y = entity_pos.y + velocity.y * dt
    entity_rect = pygame.Rect(int(new_x), int(new_y), entity_size, entity_size)

    for wall in tilemap.wall_rects:
        if entity_rect.colliderect(wall):
            if velocity.y > 0:  # Moving down
                new_y = wall.top - entity_size
            elif velocity.y < 0:  # Moving up
                new_y = wall.bottom
            break

    entity_pos.x = new_x
    entity_pos.y = new_y
```

The key insight: resolve X and Y axes separately. If you check both at once, the player gets stuck on corners.

## Camera Scrolling

When the map is larger than the screen, the camera follows the player:

```python
class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def update(self, target_pos, map_width, map_height):
        """Center camera on target, clamped to map bounds."""
        self.rect.centerx = int(target_pos.x)
        self.rect.centery = int(target_pos.y)

        # Don't scroll past map edges
        self.rect.left = max(0, self.rect.left)
        self.rect.top = max(0, self.rect.top)
        self.rect.right = min(map_width, self.rect.right)
        self.rect.bottom = min(map_height, self.rect.bottom)

    def apply(self, pos):
        """Convert world position to screen position."""
        return (int(pos.x - self.rect.left), int(pos.y - self.rect.top))

    @property
    def offset(self):
        return (self.rect.left, self.rect.top)


camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# In game loop:
camera.update(player.pos, tilemap.pixel_width, tilemap.pixel_height)

# Drawing with camera offset:
tilemap.draw(screen, camera.offset)

# Draw entities at screen position:
screen_pos = camera.apply(player.pos)
screen.blit(player.image, (screen_pos[0] - 16, screen_pos[1] - 16))
```

## Loading TMX Files (Tiled Editor)

For real level design, use [Tiled](https://www.mapeditor.org/) — a free tile map editor. It exports `.tmx` files. Use the `pytmx` library to load them:

```bash
pip install pytmx
```

```python
import pytmx

class TMXMap:
    def __init__(self, tmx_path):
        self.tmx = pytmx.load_pygame(tmx_path)
        self.tile_size = self.tmx.tilewidth
        self.width = self.tmx.width
        self.height = self.tmx.height
        self.pixel_width = self.width * self.tile_size
        self.pixel_height = self.height * self.tile_size

        # Extract collision layer
        self.wall_rects = []
        collision_layer = self.tmx.get_layer_by_name("collision")
        for x, y, gid in collision_layer:
            if gid:  # Non-empty tile
                self.wall_rects.append(pygame.Rect(
                    x * self.tile_size, y * self.tile_size,
                    self.tile_size, self.tile_size
                ))

    def draw(self, surface, camera_offset):
        for layer in self.tmx.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        pos = (x * self.tile_size - camera_offset[0],
                               y * self.tile_size - camera_offset[1])
                        surface.blit(image, pos)
```

Tiled gives you:
- Visual level editor (drag and paint tiles)
- Multiple layers (background, foreground, collision)
- Object layers (spawn points, triggers, doors)
- Tileset management

## Layers

Real maps have depth — floor under the player, walls at player level, decorations above:

```python
# Draw order:
# 1. Background layer (floor tiles)
# 2. Entities (player, enemies, bullets)
# 3. Foreground layer (pillars, overhangs that cover the player)

tilemap.draw_layer(screen, "background", camera.offset)
# ... draw all entities ...
tilemap.draw_layer(screen, "foreground", camera.offset)
```

This creates depth without actual 3D — a pillar's top half covers the player when they walk behind it.

## Room Transitions

Void Runners has connected rooms. When the player reaches a door:

```python
class Door:
    def __init__(self, rect, target_room, spawn_pos):
        self.rect = rect
        self.target_room = target_room
        self.spawn_pos = spawn_pos  # Where player appears in new room

doors = [
    Door(pygame.Rect(384, 0, 32, 16), "room_02", pygame.math.Vector2(400, 560)),
]

# Check door collision
for door in doors:
    if player_rect.colliderect(door.rect):
        load_room(door.target_room)
        player.pos = pygame.math.Vector2(door.spawn_pos)
        break
```

## What You Learned

- **Tile maps** — grid of tile IDs, data-driven level design
- **TileMap class** — data, rendering, collision rects
- **Tile-based collision** — resolve X and Y separately
- **Camera scrolling** — follow player, clamp to map bounds
- **TMX loading** — Tiled editor + pytmx for real level design
- **Layers** — background/foreground for visual depth
- **Room transitions** — doors that load new maps

The game has a world. Walls you can't walk through. Rooms connected by doors. A camera that follows the player through spaces larger than the screen.

But the enemies still just bounce randomly. They don't chase the player. They don't patrol. They don't react to anything. Time to give them brains.

---

[← Chapter 6: Sound & Music](chapter-06-audio.md) | [Chapter 8: Enemies That Think →](chapter-08-enemies.md)
