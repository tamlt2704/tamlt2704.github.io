# Chapter 15: Ship It — Packaging and Distribution

[← Chapter 14: Polish & Juice](chapter-14-polish.md)

---

## The Problem

The game is done. It's fun. It's polished. Sam asks the question that matters: "How do I give this to someone who doesn't have Python installed?"

You can't tell players to install Python 3.10, pip install pygame-ce, clone a repo, and run `python main.py`. That's a developer workflow, not a player experience. Players expect: download, double-click, play.

## PyInstaller: The Standard Approach

PyInstaller bundles your Python script, the interpreter, and all dependencies into a single executable:

```bash
pip install pyinstaller
```

### Basic Build

```bash
pyinstaller --onefile --windowed main.py
```

- `--onefile`: Single .exe file (slower startup, cleaner distribution)
- `--windowed`: No console window (for GUI apps)

Output: `dist/main.exe` — a standalone executable.

### Including Assets

PyInstaller doesn't automatically include your `assets/` folder. You need a spec file:

```bash
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

On Windows, the separator is `;`. On Linux/Mac, it's `:`.

### The Resource Path Problem

When bundled, assets aren't in the same relative path. PyInstaller extracts them to a temp directory. Fix your asset loading:

```python
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Usage:
player_image = pygame.image.load(resource_path("assets/player.png"))
shoot_sound = pygame.mixer.Sound(resource_path("assets/audio/shoot.wav"))
```

Use `resource_path()` everywhere you load files. This is the #1 reason PyInstaller builds crash — hardcoded relative paths that don't work when bundled.

### The Spec File

For full control, use a spec file:

```python
# void_runners.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('saves', 'saves'),
    ],
    hiddenimports=['pygame'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoidRunners',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)
```

Build with:

```bash
pyinstaller void_runners.spec
```

## cx_Freeze: Alternative Bundler

```bash
pip install cx_freeze
```

```python
# setup.py
from cx_Freeze import setup, Executable

setup(
    name="Void Runners",
    version="1.0",
    description="Top-down action game",
    executables=[
        Executable(
            "main.py",
            base="Win32GUI",  # No console on Windows
            icon="assets/icon.ico",
            target_name="VoidRunners.exe",
        )
    ],
    options={
        "build_exe": {
            "include_files": ["assets/", "saves/"],
            "packages": ["pygame"],
        }
    },
)
```

```bash
python setup.py build
```

cx_Freeze creates a folder with the exe and dependencies. Zip the folder for distribution.

## Platform-Specific Builds

### Windows

```bash
# Build on Windows for Windows
pyinstaller --onefile --windowed --icon=assets/icon.ico --name=VoidRunners main.py
```

Result: `VoidRunners.exe` (~30-50MB with pygame bundled)

### macOS

```bash
# Build on macOS for macOS
pyinstaller --onefile --windowed --icon=assets/icon.icns --name=VoidRunners main.py
```

Result: `VoidRunners.app` bundle

### Linux

```bash
# Build on Linux for Linux
pyinstaller --onefile --name=VoidRunners main.py
```

Result: `VoidRunners` binary (mark as executable: `chmod +x VoidRunners`)

You must build on each platform — PyInstaller doesn't cross-compile.

## Reducing File Size

A basic pygame bundle is 30-50MB. To reduce:

```bash
# Use UPX compression
pip install pyinstaller
# Download UPX from https://upx.github.io/ and add to PATH
pyinstaller --onefile --windowed --upx-dir=/path/to/upx main.py
```

Exclude unused modules:

```python
# In spec file:
excludes=['tkinter', 'unittest', 'email', 'html', 'http', 'xml',
          'pydoc', 'doctest', 'argparse', 'difflib', 'inspect']
```

Compress audio (OGG instead of WAV for music, lower sample rates for effects).

## Publishing to itch.io

[itch.io](https://itch.io) is the standard platform for indie games:

1. Create an account at itch.io
2. Click "Upload new project"
3. Fill in details:
   - Title: Void Runners
   - Kind: Game
   - Classification: Game
   - Pricing: Free (or set a price)
   - Uploads: Upload your zip files per platform

### Preparing the Upload

```bash
# Windows build
mkdir dist/VoidRunners-win
cp dist/VoidRunners.exe dist/VoidRunners-win/
cp -r assets dist/VoidRunners-win/  # If not bundled in exe
cd dist && zip -r VoidRunners-win.zip VoidRunners-win/

# Tag the upload as "Windows" on itch.io
```

### The itch.io Page

A good game page needs:
- **Cover image** (630×500px)
- **Screenshots** (at least 3)
- **GIF** showing gameplay (use ScreenToGif or similar)
- **Description** — what is it, how to play, controls
- **Tags** — action, top-down, shooter, indie

## Testing the Build

Before shipping, test on a clean machine (or VM):

```
✓ Game launches without Python installed
✓ All assets load (images, sounds, music)
✓ Save/load works (check file paths)
✓ Gamepad works
✓ Fullscreen works
✓ No console window appears
✓ Game closes cleanly
```

Common issues:
- Missing DLLs → include them in the bundle
- Assets not found → use `resource_path()` everywhere
- Save path wrong → use user's home directory for saves in production:

```python
import pathlib

def get_save_dir():
    """Platform-appropriate save location."""
    if sys.platform == "win32":
        base = pathlib.Path(os.environ.get("APPDATA", "~"))
    elif sys.platform == "darwin":
        base = pathlib.Path.home() / "Library" / "Application Support"
    else:
        base = pathlib.Path.home() / ".local" / "share"

    save_dir = base / "VoidRunners"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir
```

## The Launch Checklist

- [ ] Game runs from exe without Python
- [ ] All assets included and loading
- [ ] Save/load uses proper user directory
- [ ] Icon set for executable
- [ ] Version number in window title
- [ ] No debug output or FPS counter (unless settings toggle)
- [ ] Tested on clean machine
- [ ] itch.io page with screenshots and description
- [ ] Builds for Windows (minimum), Mac and Linux (bonus)

## What You Learned

- **PyInstaller** — bundle Python + deps into standalone exe
- **Resource paths** — `sys._MEIPASS` for bundled asset loading
- **cx_Freeze** — alternative bundler with setup.py
- **Platform builds** — Windows, macOS, Linux (no cross-compile)
- **Size reduction** — UPX, exclude unused modules, compress audio
- **itch.io** — upload, page setup, tagging
- **Production paths** — save to AppData/Library, not game directory
- **Testing** — verify on clean machine without dev tools

## The End

You shipped a game. From a blank window to a polished, packaged, distributed product. Void Runners is on itch.io. People are playing it. Rena left a review: "Actually fun. The screen shake is too much though."

Sam: "So... when's the next one?"

You open a new Python file. The cursor blinks.

---

## What You Built (The Complete System)

| Chapter | System | Status |
|---|---|---|
| 1 | Game loop, display, clock | ✓ |
| 2 | Movement, delta time, vectors | ✓ |
| 3 | Input handling, mouse aim, buffering | ✓ |
| 4 | Collision detection, sprite groups | ✓ |
| 5 | Sprite sheets, animation state machine | ✓ |
| 6 | Sound effects, music, mixer | ✓ |
| 7 | Tile maps, camera, room transitions | ✓ |
| 8 | Enemy AI, state machines, waves | ✓ |
| 9 | Particles, screen shake, hitstop | ✓ |
| 10 | Scenes, menus, HUD, pause | ✓ |
| 11 | Save/load, settings, high scores | ✓ |
| 12 | Profiling, pooling, spatial hash | ✓ |
| 13 | Gamepad, input abstraction, rumble | ✓ |
| 14 | Tweening, camera lerp, polish | ✓ |
| 15 | Packaging, distribution, shipping | ✓ |

You didn't just learn Pygame. You learned how to make a game.

---

[← Chapter 14: Polish & Juice](chapter-14-polish.md)
