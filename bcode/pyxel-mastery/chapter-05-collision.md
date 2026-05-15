# Chapter 5 — Collision Detection

## AABB (Axis-Aligned Bounding Box)

The simplest and most common method for pixel games. Two rectangles overlap if:

```python
def collides(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)
```

## Collecting Coins

```python
import pyxel

pyxel.init(160, 120)

pyxel.images[0].set(0, 0, [
    "00088000", "00888800", "08888880", "88888888",
    "08888880", "00888800", "00088000", "00000000",
])
pyxel.images[0].set(8, 0, [
    "000aa000", "00aaaa00", "0aaaaaa0", "aaaaaaaa",
    "0aaaaaa0", "00aaaa00", "000aa000", "00000000",
])

px, py = 76, 56
coins = [[20, 30], [100, 80], [50, 90], [130, 20]]
score = 0

def collides(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

def update():
    global px, py, score
    if pyxel.btn(pyxel.KEY_LEFT):  px -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): px += 2
    if pyxel.btn(pyxel.KEY_UP):    py -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  py += 2

    # Check coin collisions
    for coin in coins[:]:  # iterate copy
        if collides(px, py, 8, 8, coin[0], coin[1], 8, 8):
            coins.remove(coin)
            score += 1

def draw():
    pyxel.cls(1)
    pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)
    for coin in coins:
        pyxel.blt(coin[0], coin[1], 0, 8, 0, 8, 8, 0)
    pyxel.text(5, 5, f"Score: {score}", 7)

pyxel.run(update, draw)
```

## Circle Collision

Better for round objects:

```python
import math

def circle_collides(x1, y1, r1, x2, y2, r2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist < r1 + r2
```

## Point-in-Rect (Mouse Clicks)

```python
def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px < rx + rw and ry <= py < ry + rh

def update():
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        if point_in_rect(pyxel.mouse_x, pyxel.mouse_y, 50, 50, 30, 15):
            print("Button clicked!")
```

## Solid Walls (Blocking Movement)

```python
walls = [(40, 40, 16, 16), (80, 60, 16, 16)]

def update():
    global px, py
    new_x, new_y = px, py

    if pyxel.btn(pyxel.KEY_LEFT):  new_x -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): new_x += 2
    if pyxel.btn(pyxel.KEY_UP):    new_y -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  new_y += 2

    # Check X movement
    blocked = False
    for wx, wy, ww, wh in walls:
        if collides(new_x, py, 8, 8, wx, wy, ww, wh):
            blocked = True
            break
    if not blocked:
        px = new_x

    # Check Y movement separately
    blocked = False
    for wx, wy, ww, wh in walls:
        if collides(px, new_y, 8, 8, wx, wy, ww, wh):
            blocked = True
            break
    if not blocked:
        py = new_y
```

Checking X and Y separately allows sliding along walls.

## Pixel-Perfect Collision

Check if non-transparent pixels overlap (expensive, use sparingly):

```python
def pixel_collides(x1, y1, img1, u1, v1, w, h, x2, y2, img2, u2, v2):
    for dy in range(h):
        for dx in range(w):
            sx, sy = x1 + dx, y1 + dy
            if x2 <= sx < x2 + w and y2 <= sy < y2 + h:
                p1 = pyxel.images[img1].pget(u1 + dx, v1 + dy)
                ox, oy = sx - x2, sy - y2
                p2 = pyxel.images[img2].pget(u2 + ox, v2 + oy)
                if p1 != 0 and p2 != 0:  # both non-transparent
                    return True
    return False
```

Usually AABB is enough for pixel art games.

## Exercise

Extend the coin game:
- Add walls the player can't pass through
- Add an enemy that moves back and forth
- If player touches enemy, reset position

## Next

Chapter 6: Adding sound effects and music.
