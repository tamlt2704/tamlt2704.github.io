# Chapter 0 — Overview & Setup

## What is Pyxel?

Pyxel is a retro game engine for Python with deliberate constraints:

- **16 colors** (customizable palette)
- **256x256** max screen size
- **3 image banks** (256x256 each) for sprites
- **8 tilemaps** (256x256 tiles each)
- **4 sound channels** with 64 definable sounds
- **8 music tracks**
- Built-in **sprite, tilemap, sound, and music editors**
- **Web export** (WASM) with one command

These constraints force creativity — like making games for a fantasy console.

## Install

```bash
pip install pyxel
```

Verify:

```bash
python -c "import pyxel; print(pyxel.VERSION)"
```

## The Built-in Editor

Pyxel includes a resource editor for creating sprites, tilemaps, and sounds:

```bash
pyxel edit my_resources.pyxres
```

This opens a GUI with tabs for:
- **Image editor** — draw sprites pixel by pixel
- **Tilemap editor** — arrange tiles into maps
- **Sound editor** — create chiptune sounds
- **Music editor** — sequence sounds into tracks

## Minimal Program

```python
import pyxel

pyxel.init(160, 120, title="Hello Pyxel")

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.text(55, 55, "Hello, Pyxel!", 7)

pyxel.run(update, draw)
```

Run it:

```bash
python hello.py
```

You'll see a 160x120 window with white text on a black background.

## The Game Loop

Pyxel runs at 30 FPS by default. Every frame:

1. `update()` — handle input, update game state
2. `draw()` — render everything to screen

That's it. No event loops, no callbacks. Just two functions.

## Color Palette

Pyxel uses 16 colors (0–15) by default:

```
 0: Black        4: Brown        8: Red         12: Light blue
 1: Dark blue    5: Dark green   9: Orange      13: Gray
 2: Purple       6: Light green  10: Yellow     14: Pink
 3: Dark green   7: White        11: Tan        15: Peach
```

You can customize the palette:

```python
pyxel.colors[0] = 0x1a1c2c  # replace color 0 with custom hex
```

## Project Structure

```
my_game/
├── main.py          # game code
├── assets.pyxres    # sprites, tilemaps, sounds (from editor)
└── README.md
```

## Next

Chapter 1: Drawing shapes, understanding coordinates, and the frame cycle.
