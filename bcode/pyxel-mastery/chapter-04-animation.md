# Chapter 4 — Animation

## Frame-Based Animation

Place animation frames side by side on the sprite sheet:

```
Sheet layout (8x8 sprites):
(0,0)  (8,0)  (16,0)  (24,0)
 ┌──┐   ┌──┐   ┌──┐   ┌──┐
 │F0│   │F1│   │F2│   │F3│   ← 4 walk frames
 └──┘   └──┘   └──┘   └──┘
```

Cycle through them based on `frame_count`:

```python
import pyxel

pyxel.init(160, 120)

# Define 4 animation frames on the sheet
frames = [
    "00077000", "00777700", "07777770", "77777777",
    "07777770", "00777700", "00077000", "00007000",
]
pyxel.images[0].set(0, 0, frames[:8])  # frame 0 at (0,0)

# Simpler: define frames as sheet positions
ANIM_FRAMES = [(0, 0), (8, 0), (16, 0), (24, 0)]
ANIM_SPEED = 8  # frames per animation frame

px, py = 76, 56
moving = False

def update():
    global px, moving
    moving = False
    if pyxel.btn(pyxel.KEY_RIGHT):
        px += 2
        moving = True

def draw():
    pyxel.cls(0)
    if moving:
        # Cycle through animation frames
        frame_idx = (pyxel.frame_count // ANIM_SPEED) % len(ANIM_FRAMES)
        u, v = ANIM_FRAMES[frame_idx]
    else:
        u, v = 0, 0  # idle frame

    pyxel.blt(px, py, 0, u, v, 8, 8, 0)

pyxel.run(update, draw)
```

## Animation Speed

`ANIM_SPEED` controls how many game frames per animation frame:

| ANIM_SPEED | At 30 FPS | Feel |
|------------|-----------|------|
| 4 | 7.5 anim FPS | Fast/frantic |
| 8 | 3.75 anim FPS | Normal walk |
| 15 | 2 anim FPS | Slow/idle |

## Animation Class

For cleaner code:

```python
class Animator:
    def __init__(self, frames, speed=8):
        self.frames = frames  # list of (u, v) positions
        self.speed = speed
        self.tick = 0

    def update(self):
        self.tick += 1

    def current_frame(self):
        idx = (self.tick // self.speed) % len(self.frames)
        return self.frames[idx]

    def reset(self):
        self.tick = 0
```

Usage:

```python
walk_anim = Animator([(0, 0), (8, 0), (16, 0), (24, 0)], speed=6)
idle_anim = Animator([(0, 0), (0, 8)], speed=15)

current_anim = idle_anim

def update():
    global current_anim
    if pyxel.btn(pyxel.KEY_RIGHT):
        current_anim = walk_anim
    else:
        current_anim = idle_anim
    current_anim.update()

def draw():
    pyxel.cls(0)
    u, v = current_anim.current_frame()
    pyxel.blt(px, py, 0, u, v, 8, 8, 0)
```

## One-Shot Animations (play once, don't loop)

```python
class OneShotAnimator:
    def __init__(self, frames, speed=4):
        self.frames = frames
        self.speed = speed
        self.tick = 0
        self.done = False

    def update(self):
        if not self.done:
            self.tick += 1
            if self.tick // self.speed >= len(self.frames):
                self.done = True

    def current_frame(self):
        idx = min(self.tick // self.speed, len(self.frames) - 1)
        return self.frames[idx]
```

Good for explosions, death animations, etc.

## Blinking / Flashing

```python
def draw():
    pyxel.cls(0)
    # Blink: visible 20 frames, hidden 10 frames
    if pyxel.frame_count % 30 < 20:
        pyxel.blt(px, py, 0, 0, 0, 8, 8, 0)
```

## Exercise

Create a character with:
- 2-frame idle animation (slow)
- 4-frame walk animation (faster)
- Switches between them based on movement

## Next

Chapter 5: Detecting collisions between sprites.
