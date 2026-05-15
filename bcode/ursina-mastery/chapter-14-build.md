# Chapter 14: Build & Distribute

Once your game is ready, you can package it as a standalone executable. Users won't need Python or Ursina installed. Ursina provides a built-in build tool, or you can use PyInstaller for more control.

```python
# === Option 1: Ursina's built-in build tool ===
# Run this script (not your game) to build:
from ursina import *
from ursina.build.build_game import build_game

build_game(
    script='main.py',           # your game entry point
    name='MyGame',              # output name
    include_modules=[],         # extra Python modules to include
    compressed=True
)

# === Option 2: PyInstaller (more control) ===
# Terminal command:
# pyinstaller --onefile --windowed --add-data "assets;assets" main.py

# === Project structure for building ===
# my_game/
# ├── main.py              <- your game script
# ├── assets/
# │   ├── models/          <- custom .obj, .blend files
# │   ├── textures/        <- .png, .jpg images
# │   └── audio/           <- .wav, .ogg, .mp3 files
# └── build/               <- output goes here
```

## Key Points

- **Ursina build tool**: `build_game(script, name)` — simplest option
- **PyInstaller**: `pyinstaller --onefile --windowed main.py` — more control over bundling
- **Assets**: keep all assets in a subfolder and include them with `--add-data`
- **Output**: a standalone `.exe` (Windows) or binary (Mac/Linux)
- Test the built executable on a clean machine without Python installed
- The build includes Python runtime + Ursina + your code + assets

## What You Learned

- How to use Ursina's built-in build tool
- How to use PyInstaller as an alternative
- How to structure your project for clean builds
- That the output is a standalone executable requiring no Python installation

---

[← Chapter 13: Networking](chapter-13-networking.md) | [Next → Chapter 15: Full Game](chapter-15-dungeon.md)
