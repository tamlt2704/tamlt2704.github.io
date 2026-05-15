# Chapter 7 — Tilemaps

## What's a Tilemap?

A tilemap is a grid where each cell references an 8x8 tile from your sprite sheet. Instead of placing every pixel, you paint levels with reusable tiles.

Pyxel provides **8 tilemap slots** (0–7), each 256x256 tiles (2048x2048 pixels).

## Creating Tilemaps in the Editor

```bash
pyxel edit assets.pyxres
```

1. Draw tiles on the **Image** tab (8x8 blocks)
2. Switch to **Tilemap** tab
3. Select a tile from the image bank
4. Paint it onto the tilemap grid

## Drawing a Tilemap

```python
pyxel.bltm(x, y, tm, u, v, w, h)
pyxel.bltm(x, y, tm, u, v, w, h, colkey)
```

| Param | Meaning |
|-------|---------|
| x, y | Screen position |
| tm | Tilemap index (0–7) |
| u, v | Top-left tile position (in pixels) on the tilemap |
| w, h | Width/height to draw (in pixels) |
| colkey | Transparent color |

```python
def draw():
    pyxel.cls(0)
    # Draw a 160x120 section of tilemap 0 starting at tile (0,0)
    pyxel.bltm(0, 0, 0, 0, 0, 160, 120, 0)
    # Draw player on top
    pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)
```

## Tilemaps in Code (No Editor)

```python
import pyxel

pyxel.init(160, 120)

# Define some tiles on image bank 0
# Tile 0 (0,0): empty/sky
pyxel.images[0].set(0, 0, [
    "11111111", "11111111", "11111111", "11111111",
    "11111111", "11111111", "11111111", "11111111",
])
# Tile 1 (8,0): ground
pyxel.images[0].set(8, 0, [
    "55555555", "5d5d5d5d", "d5d5d5d5", "55555555",
    "55555555", "5d5d5d5d", "d5d5d5d5", "55555555",
])
# Tile 2 (16,0): brick
pyxel.images[0].set(16, 0, [
    "44444444", "48484848", "44444444", "84848484",
    "44444444", "48484848", "44444444", "84848484",
])

# Set tilemap 0 using tile coordinates
# Each tuple (tx, ty) refers to tile position on image bank
# Tilemap.set takes (x, y, list_of_strings)
# Each char pair is a tile index: "0000" = 4 tiles of type (0,0)
pyxel.tilemaps[0].set(0, 0, [
    "0000 0000 0000 0000 0000 0000 0000 0000 0000 0000",
    "0000 0000 0000 0000 0000 0000 0000 0000 0000 0000",
    "0000 0000 0000 0200 0200 0000 0000 0000 0000 0000",
    "0100 0100 0100 0100 0100 0100 0100 0100 0100 0100",
])
```

Note: Tilemap `set()` format uses hex pairs for tile (x, y) on the image bank divided by 8.

## Simpler: Array-Based Levels

For small games, a 2D array is often easier:

```python
import pyxel

pyxel.init(160, 120)

TILE_SIZE = 8

# 0 = empty, 1 = ground, 2 = brick
level = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

TILE_COLORS = {0: None, 1: 5, 2: 4}

px, py = 16, 96

def get_tile(x, y):
    col = int(x // TILE_SIZE)
    row = int(y // TILE_SIZE)
    if 0 <= row < len(level) and 0 <= col < len(level[0]):
        return level[row][col]
    return 0

def is_solid(x, y, w, h):
    """Check if a rectangle overlaps any solid tile."""
    for check_x in [x, x + w - 1]:
        for check_y in [y, y + h - 1]:
            tile = get_tile(check_x, check_y)
            if tile != 0:
                return True
    return False

def update():
    global px, py
    new_x, new_y = px, py

    if pyxel.btn(pyxel.KEY_LEFT):  new_x -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): new_x += 2
    if pyxel.btn(pyxel.KEY_UP):    new_y -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  new_y += 2

    if not is_solid(new_x, py, 8, 8):
        px = new_x
    if not is_solid(px, new_y, 8, 8):
        py = new_y

def draw():
    pyxel.cls(0)
    for row in range(len(level)):
        for col in range(len(level[0])):
            tile = level[row][col]
            if tile != 0:
                pyxel.rect(col * TILE_SIZE, row * TILE_SIZE,
                          TILE_SIZE, TILE_SIZE, TILE_COLORS[tile])
    pyxel.rect(px, py, 8, 8, 11)

pyxel.run(update, draw)
```

## Tile Collision with Tilemap

When using Pyxel's built-in tilemaps, read tile values with:

```python
# Get tile at pixel position (x, y) on tilemap 0
tile = pyxel.tilemaps[0].pget(x // 8, y // 8)
# Returns (tile_x, tile_y) on the image bank
```

## Exercise

Build a simple platformer level:
- Ground tiles at the bottom
- Some floating platforms
- Player can walk and collide with tiles
- Use the array-based approach or the editor

## Next

Chapter 8: Camera scrolling for levels larger than the screen.
