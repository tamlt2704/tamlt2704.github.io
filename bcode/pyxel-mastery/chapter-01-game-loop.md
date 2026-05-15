# Chapter 1 — Game Loop & Drawing

## The Frame Cycle

Every frame (30 FPS default):

```
update() → draw() → update() → draw() → ...
```

- `update()`: logic only, no drawing
- `draw()`: rendering only, no state changes

## Drawing Primitives

```python
import pyxel

pyxel.init(160, 120, title="Drawing")

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(1)  # clear screen with color 1 (dark blue)

    # Pixel
    pyxel.pset(10, 10, 7)  # x, y, color

    # Line
    pyxel.line(20, 20, 60, 40, 8)  # x1, y1, x2, y2, color

    # Rectangle (outline)
    pyxel.rect(70, 10, 30, 20, 10)  # x, y, w, h, color

    # Rectangle (filled)
    pyxel.rectb(70, 40, 30, 20, 11)  # outline only

    # Circle (filled)
    pyxel.circ(40, 80, 15, 12)  # x, y, radius, color

    # Circle (outline)
    pyxel.circb(90, 80, 15, 14)

    # Text
    pyxel.text(5, 110, "Pyxel draws!", 7)  # x, y, string, color

pyxel.run(update, draw)
```

## Coordinate System

```
(0,0) ──────────→ x (160)
  │
  │
  │
  ↓
  y (120)
```

Top-left is (0, 0). X goes right, Y goes down.

## Frame Counter

`pyxel.frame_count` increments every frame. Useful for animation timing:

```python
def draw():
    pyxel.cls(0)
    # Blink text every 30 frames (1 second)
    if pyxel.frame_count % 60 < 30:
        pyxel.text(50, 55, "PRESS START", 7)
```

## Screen Size & FPS

```python
# 256x256 at 60 FPS
pyxel.init(256, 256, title="Big & Fast", fps=60)

# Tiny 64x64 at 30 FPS (default)
pyxel.init(64, 64, title="Tiny")
```

Max screen size is 256x256.

## cls() is Required

Always call `pyxel.cls(color)` at the start of `draw()`. Without it, previous frames bleed through (which can be a deliberate effect for trails).

## Exercise

Draw a simple scene: sky (blue background), green ground rectangle at the bottom, yellow circle sun, white text title.

```python
import pyxel

pyxel.init(160, 120, title="My Scene")

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(12)  # light blue sky
    pyxel.rect(0, 90, 160, 30, 5)  # green ground
    pyxel.circ(130, 20, 12, 10)  # yellow sun
    pyxel.text(50, 5, "My World", 7)

pyxel.run(update, draw)
```

## Next

Chapter 2: Reading keyboard/mouse/gamepad input and moving things around.
