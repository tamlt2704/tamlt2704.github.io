# Chapter 2 — Input & Movement

## Input Functions

| Function | Meaning |
|----------|---------|
| `pyxel.btn(key)` | True while key is held down |
| `pyxel.btnp(key)` | True only on the frame key is first pressed |
| `pyxel.btnr(key)` | True only on the frame key is released |

## Moving a Player

```python
import pyxel

pyxel.init(160, 120, title="Movement")

player_x = 76
player_y = 56

def update():
    global player_x, player_y

    if pyxel.btn(pyxel.KEY_LEFT):
        player_x -= 2
    if pyxel.btn(pyxel.KEY_RIGHT):
        player_x += 2
    if pyxel.btn(pyxel.KEY_UP):
        player_y -= 2
    if pyxel.btn(pyxel.KEY_DOWN):
        player_y += 2

    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.rect(player_x, player_y, 8, 8, 11)  # 8x8 square player

pyxel.run(update, draw)
```

## Speed & Delta

Pyxel runs at fixed FPS (no delta time needed). Just move by pixels per frame:

```python
SPEED = 2  # pixels per frame

if pyxel.btn(pyxel.KEY_RIGHT):
    player_x += SPEED
```

At 30 FPS, `SPEED = 2` means 60 pixels/second.

## Screen Boundaries

Keep the player on screen:

```python
def update():
    global player_x, player_y

    if pyxel.btn(pyxel.KEY_LEFT):
        player_x = max(0, player_x - 2)
    if pyxel.btn(pyxel.KEY_RIGHT):
        player_x = min(152, player_x + 2)  # 160 - 8 (player width)
    if pyxel.btn(pyxel.KEY_UP):
        player_y = max(0, player_y - 2)
    if pyxel.btn(pyxel.KEY_DOWN):
        player_y = min(112, player_y + 2)  # 120 - 8
```

## Mouse Input

```python
def update():
    # Mouse position
    mx = pyxel.mouse_x
    my = pyxel.mouse_y

    # Mouse click
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        print(f"Clicked at {mx}, {my}")

def draw():
    pyxel.cls(0)
    # Crosshair at mouse position
    pyxel.circ(pyxel.mouse_x, pyxel.mouse_y, 2, 8)
```

Show/hide the system cursor:

```python
pyxel.mouse(True)   # show
pyxel.mouse(False)  # hide (draw your own)
```

## Gamepad

```python
if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
    player_x -= 2
```

## Key Constants

Common keys:
- `KEY_LEFT`, `KEY_RIGHT`, `KEY_UP`, `KEY_DOWN`
- `KEY_SPACE`, `KEY_RETURN`
- `KEY_A` through `KEY_Z`
- `KEY_1` through `KEY_0`
- `MOUSE_BUTTON_LEFT`, `MOUSE_BUTTON_RIGHT`

## btnp with Repeat

`btnp` supports auto-repeat (hold to keep triggering):

```python
# Triggers on press, then repeats every 4 frames after 20 frame delay
if pyxel.btnp(pyxel.KEY_RIGHT, hold=20, repeat=4):
    player_x += 8  # grid-based movement
```

## Exercise

Make a character that:
- Moves with arrow keys
- Changes color when SPACE is held
- Wraps around screen edges (appears on opposite side)

```python
import pyxel

pyxel.init(160, 120, title="Wrap Around")

px, py = 76, 56

def update():
    global px, py
    if pyxel.btn(pyxel.KEY_LEFT):  px -= 2
    if pyxel.btn(pyxel.KEY_RIGHT): px += 2
    if pyxel.btn(pyxel.KEY_UP):    py -= 2
    if pyxel.btn(pyxel.KEY_DOWN):  py += 2

    # Wrap
    px = px % 160
    py = py % 120

def draw():
    pyxel.cls(0)
    color = 10 if pyxel.btn(pyxel.KEY_SPACE) else 7
    pyxel.rect(px, py, 8, 8, color)

pyxel.run(update, draw)
```

## Next

Chapter 3: Creating sprites with the built-in editor and drawing them.
