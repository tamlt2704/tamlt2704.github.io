# Chapter 3 — Sprites & the Resource Editor

## The Resource Editor

Open it:

```bash
pyxel edit assets.pyxres
```

Tabs:
- **Image** — draw sprites on a 256x256 pixel sheet (3 banks: 0, 1, 2)
- **Tilemap** — arrange 8x8 tiles into maps
- **Sound** — create sound effects
- **Music** — sequence sounds

Draw your sprites on image bank 0. Each sprite is typically 8x8 or 16x16 pixels.

## Loading Resources

```python
import pyxel

pyxel.init(160, 120, title="Sprites")
pyxel.load("assets.pyxres")  # load all resources
```

## Drawing a Sprite (blt)

```python
pyxel.blt(x, y, img, u, v, w, h)
pyxel.blt(x, y, img, u, v, w, h, colkey)
```

| Param | Meaning |
|-------|---------|
| x, y | Screen position to draw at |
| img | Image bank (0, 1, or 2) |
| u, v | Top-left corner of sprite on the sheet |
| w, h | Width and height to copy |
| colkey | Transparent color (optional) |

Example — draw an 8x8 sprite from position (0,0) on bank 0:

```python
def draw():
    pyxel.cls(0)
    # Draw sprite at screen position (76, 56)
    # From image bank 0, at sheet position (0, 0), size 8x8
    # Color 0 (black) is transparent
    pyxel.blt(76, 56, 0, 0, 0, 8, 8, 0)
```

## Flipping Sprites

Use negative width/height to flip:

```python
# Flip horizontally
pyxel.blt(x, y, 0, 0, 0, -8, 8, 0)

# Flip vertically
pyxel.blt(x, y, 0, 0, 0, 8, -8, 0)

# Flip both
pyxel.blt(x, y, 0, 0, 0, -8, -8, 0)
```

## Drawing Sprites Without the Editor

You can set pixels directly in code:

```python
import pyxel

pyxel.init(160, 120)

# Define an 8x8 sprite in image bank 0
# Each string is a row, each char is a color (hex 0-f)
pyxel.images[0].set(0, 0, [
    "00088000",
    "00888800",
    "08888880",
    "88888888",
    "08888880",
    "00888800",
    "00088000",
    "00008000",
])

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(1)
    pyxel.blt(76, 56, 0, 0, 0, 8, 8, 0)

pyxel.run(update, draw)
```

Each character maps to a color (0-f in hex = 0-15).

## 16x16 Sprites

Just use larger dimensions:

```python
pyxel.blt(x, y, 0, 0, 0, 16, 16, 0)
```

And draw your sprite in a 16x16 area on the sheet.

## Sprite Sheet Layout

Organize your sheet like a grid:

```
(0,0)   (8,0)   (16,0)  ...
  ┌───┐   ┌───┐   ┌───┐
  │ A │   │ B │   │ C │   ← row 0
  └───┘   └───┘   └───┘
(0,8)   (8,8)   (16,8)
  ┌───┐   ┌───┐   ┌───┐
  │ D │   │ E │   │ F │   ← row 1
  └───┘   └───┘   └───┘
```

To draw sprite E: `pyxel.blt(x, y, 0, 8, 8, 8, 8, 0)`

## Player with Direction

```python
import pyxel

pyxel.init(160, 120)
pyxel.images[0].set(0, 0, [
    "00077000",
    "00777700",
    "07777770",
    "77777777",
    "07777770",
    "00777700",
    "00077000",
    "00007000",
])

px, py = 76, 56
facing_right = True

def update():
    global px, facing_right
    if pyxel.btn(pyxel.KEY_LEFT):
        px -= 2
        facing_right = False
    if pyxel.btn(pyxel.KEY_RIGHT):
        px += 2
        facing_right = True

def draw():
    pyxel.cls(0)
    w = 8 if facing_right else -8
    pyxel.blt(px, py, 0, 0, 0, w, 8, 0)

pyxel.run(update, draw)
```

## Exercise

Create a scene with:
- A player sprite (defined in code or editor)
- A few "coin" sprites placed at fixed positions
- Player moves with arrow keys

```python
import pyxel

pyxel.init(160, 120)

# Player sprite at (0,0) on sheet
pyxel.images[0].set(0, 0, [
    "00088000",
    "00888800",
    "08898880",
    "88888888",
    "08888880",
    "00888800",
    "00088000",
    "00000000",
])

# Coin sprite at (8,0) on sheet
pyxel.images[0].set(8, 0, [
    "000aa000",
    "00aaaa00",
    "0aaaaaa0",
    "aaaaaaaa",
    "0aaaaaa0",
    "00aaaa00",
    "000aa000",
    "00000000",
])

px, py = 76, 56
coins = [(20, 30), (100, 80), (50, 90), (130, 20)]

def update():
    global px, py
    if pyxel.btn(pyxel.KEY_LEFT):  px -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): px += 2
    if pyxel.btn(pyxel.KEY_UP):    py -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  py += 2

def draw():
    pyxel.cls(1)
    pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)
    for cx, cy in coins:
        pyxel.blt(cx, cy, 0, 8, 0, 8, 8, 0)

pyxel.run(update, draw)
```

## Next

Chapter 4: Animating sprites with frame sequences.
