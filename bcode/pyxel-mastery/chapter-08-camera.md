# Chapter 8 — Camera & Scrolling

## The Concept

Your level is bigger than the screen. A "camera" defines which portion is visible. Everything is drawn offset by the camera position.

```
Level (400 pixels wide):
┌──────────────────────────────────────────────┐
│          ┌─────────────┐                     │
│          │  Screen     │                     │
│          │  (160x120)  │                     │
│          └─────────────┘                     │
│              ↑ camera_x, camera_y            │
└──────────────────────────────────────────────┘
```

## Basic Camera

```python
import pyxel

pyxel.init(160, 120)

LEVEL_W = 400
LEVEL_H = 200

px, py = 80, 100
cam_x, cam_y = 0, 0

def update():
    global px, py, cam_x, cam_y

    if pyxel.btn(pyxel.KEY_LEFT):  px -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): px += 2
    if pyxel.btn(pyxel.KEY_UP):    py -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  py += 2

    # Camera follows player (centered)
    cam_x = px - 80   # half screen width
    cam_y = py - 60   # half screen height

    # Clamp camera to level bounds
    cam_x = max(0, min(cam_x, LEVEL_W - 160))
    cam_y = max(0, min(cam_y, LEVEL_H - 120))

def draw():
    pyxel.cls(1)

    # Draw objects offset by camera
    # Some scattered "trees"
    trees = [(50, 150), (120, 130), (200, 160), (300, 140), (350, 170)]
    for tx, ty in trees:
        sx = tx - cam_x  # screen x
        sy = ty - cam_y  # screen y
        if -8 <= sx <= 160 and -8 <= sy <= 120:  # only draw if visible
            pyxel.rect(sx, sy, 8, 16, 5)

    # Draw ground
    pyxel.rect(0, 180 - cam_y, LEVEL_W, 20, 3)

    # Draw player (always offset by camera)
    pyxel.rect(px - cam_x, py - cam_y, 8, 8, 11)

    # HUD (not affected by camera)
    pyxel.text(5, 5, f"pos: {px},{py}", 7)

pyxel.run(update, draw)
```

## Pyxel's Built-in Camera

Pyxel has `pyxel.camera(x, y)` which offsets ALL subsequent draw calls:

```python
def draw():
    pyxel.cls(1)

    # Set camera — everything after this is offset
    pyxel.camera(cam_x, cam_y)

    # Draw world objects at their WORLD positions (no manual offset!)
    for tx, ty in trees:
        pyxel.rect(tx, ty, 8, 16, 5)
    pyxel.rect(px, py, 8, 8, 11)

    # Reset camera for HUD
    pyxel.camera(0, 0)
    pyxel.text(5, 5, f"pos: {px},{py}", 7)
```

Much cleaner! Use `pyxel.camera()` for world rendering, reset to (0,0) for UI.

## Smooth Camera (Lerp)

Instead of snapping to the player, ease toward them:

```python
def update():
    global cam_x, cam_y

    # Target position
    target_x = px - 80
    target_y = py - 60

    # Lerp (linear interpolation) — 0.1 = smooth, 1.0 = instant
    cam_x += (target_x - cam_x) * 0.1
    cam_y += (target_y - cam_y) * 0.1

    # Clamp
    cam_x = max(0, min(cam_x, LEVEL_W - 160))
    cam_y = max(0, min(cam_y, LEVEL_H - 120))
```

## Scrolling Tilemap

```python
def draw():
    pyxel.cls(0)
    pyxel.camera(int(cam_x), int(cam_y))

    # Draw tilemap — Pyxel handles the offset
    pyxel.bltm(0, 0, 0, 0, 0, LEVEL_W, LEVEL_H, 0)

    # Draw player at world position
    pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)

    # HUD
    pyxel.camera(0, 0)
    pyxel.text(5, 5, f"Score: {score}", 7)
```

## Parallax Background

Multiple layers scrolling at different speeds:

```python
def draw():
    pyxel.cls(0)

    # Far background (moves slow)
    bg_x = int(cam_x * 0.2) % 160
    pyxel.bltm(-bg_x, 0, 1, 0, 0, 320, 120, 0)

    # Mid layer (moves medium)
    mid_x = int(cam_x * 0.5) % 160
    pyxel.bltm(-mid_x, 40, 2, 0, 0, 320, 80, 0)

    # Foreground (moves with camera)
    pyxel.camera(int(cam_x), int(cam_y))
    pyxel.bltm(0, 0, 0, 0, 0, LEVEL_W, LEVEL_H, 0)
    pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)

    pyxel.camera(0, 0)
```

## Screen Shake

```python
import random

shake = 0

def trigger_shake():
    global shake
    shake = 10  # frames of shake

def update():
    global shake
    if shake > 0:
        shake -= 1

def draw():
    offset_x = random.randint(-2, 2) if shake > 0 else 0
    offset_y = random.randint(-2, 2) if shake > 0 else 0

    pyxel.camera(int(cam_x) + offset_x, int(cam_y) + offset_y)
    # ... draw world ...
```

## Exercise

Create a scrolling level:
- Level wider than screen (400+ pixels)
- Camera follows player with smooth lerp
- Add a parallax background layer
- Trigger screen shake when player hits something

## Next

Chapter 9: Particle effects for juice and polish.
