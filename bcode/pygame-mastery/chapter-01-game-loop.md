# Chapter 1: The Blank Window — The Game Loop

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Movement →](chapter-02-movement.md)

---

## The Problem

Day 1 at Pixel Forge. You open a new file called `main.py`. You need something on screen. Anything. A window that stays open and responds to the close button.

You try the obvious:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Void Runners")
```

You run it. A window appears for a split second and vanishes. The program ended — there's nothing keeping it alive.

You add a sleep:

```python
import time
time.sleep(10)
```

The window stays open for 10 seconds but it's frozen. You can't close it. You can't interact with it. The OS marks it as "Not Responding."

Games aren't scripts that run and exit. They're loops that run continuously until the player quits. You need a game loop.

## The Minimal Game Loop

```python
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Void Runners")

running = True
while running:
    # 1. Handle input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update (nothing yet)

    # 3. Draw
    screen.fill((15, 15, 25))  # Dark blue-black background
    pygame.display.flip()

pygame.quit()
sys.exit()
```

Run this. A dark window appears. It stays open. You can close it with the X button. That's a game loop.

### What's Happening

1. `pygame.event.get()` — pulls all pending OS events (key presses, mouse moves, window close)
2. We check for `QUIT` — the user clicked the close button
3. `screen.fill()` — clears the screen with a color (RGB tuple)
4. `pygame.display.flip()` — swaps the back buffer to the front (shows what we drew)

Without `flip()`, nothing appears. Pygame uses double buffering — you draw to a hidden surface, then flip it visible all at once. This prevents flickering.

## The Problem: Uncontrolled Speed

That loop runs as fast as your CPU allows. On a fast machine, it might run 5,000 iterations per second. On a slow one, 200. This means:

- Your game runs at different speeds on different machines
- Your CPU is at 100% doing nothing useful
- When you add movement later, objects will teleport on fast machines

You need a clock.

## Adding the Clock

```python
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Void Runners")
clock = pygame.time.Clock()

FPS = 60
running = True

while running:
    # 1. Handle input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update
    pass

    # 3. Draw
    screen.fill((15, 15, 25))
    pygame.display.flip()

    # 4. Tick — wait until 16.6ms have passed
    clock.tick(FPS)

pygame.quit()
sys.exit()
```

`clock.tick(60)` does two things:
1. Waits until at least 16.6ms (1000ms / 60) have passed since the last call
2. Returns the actual elapsed time in milliseconds (we'll use this for delta time in Chapter 2)

Now the loop runs at exactly 60 FPS regardless of machine speed. Your CPU usage drops from 100% to ~2%.

## Drawing Something

A blank screen isn't a game. Let's draw the player — for now, a colored rectangle:

```python
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Void Runners")
clock = pygame.time.Clock()

FPS = 60

# Player as a rectangle
player_rect = pygame.Rect(400, 300, 32, 32)  # x, y, width, height
player_color = (0, 255, 180)  # Cyan-green

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw
    screen.fill((15, 15, 25))
    pygame.draw.rect(screen, player_color, player_rect)
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
```

A small cyan square sits in the center of a dark window. It doesn't move yet — that's Chapter 2. But it's there. It's real. It's your player.

## Understanding the Coordinate System

Pygame's coordinate system:

```
(0,0) ────────────────→ x (800)
  │
  │
  │      (400, 300) ← player
  │
  ↓
  y (600)
```

- Origin (0, 0) is the **top-left** corner
- X increases to the right
- Y increases **downward** (opposite of math class)
- `pygame.Rect(400, 300, 32, 32)` means: top-left corner at (400, 300), size 32×32

This trips up everyone at first. "Move up" means **decrease** Y. You'll internalize it by Chapter 3.

## The Display Surface

`pygame.display.set_mode((800, 600))` returns a Surface — Pygame's image type. Everything you draw goes onto a Surface.

```python
# The screen is a Surface
screen = pygame.display.set_mode((800, 600))

# You can create other Surfaces
overlay = pygame.Surface((200, 200))
overlay.fill((255, 0, 0))

# Blit (copy) one Surface onto another
screen.blit(overlay, (50, 50))
```

`blit` is the fundamental drawing operation. "Blit" = Block Image Transfer. It copies pixels from one surface to another at a given position.

The draw order matters — later blits cover earlier ones. This is the **painter's algorithm**: draw background first, then objects, then UI on top.

## Display Modes

```python
# Windowed (default)
screen = pygame.display.set_mode((800, 600))

# Fullscreen
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

# Resizable window
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

# Borderless fullscreen (best for development)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
```

For development, stick with windowed. You'll want to see your terminal for print debugging. We'll handle fullscreen in Chapter 15 when shipping.

## The Complete Chapter 1 Template

This is your starting point for Void Runners. Every future chapter builds on this:

```python
import pygame
import sys

# --- Init ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Void Runners")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BG_COLOR = (15, 15, 25)
PLAYER_COLOR = (0, 255, 180)

# --- Game State ---
player_rect = pygame.Rect(
    SCREEN_WIDTH // 2 - 16,
    SCREEN_HEIGHT // 2 - 16,
    32, 32
)

# --- Game Loop ---
running = True
while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Update
    # (nothing yet)

    # Draw
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.display.flip()

    # Tick
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
```

Added: ESC to quit (you'll thank yourself during development).

## Common Mistakes

### Forgetting `pygame.display.flip()`

You draw everything but nothing appears. The back buffer has your art — it's just never shown.

### Forgetting `screen.fill()` each frame

Without clearing the screen, old frames persist. When you add movement, the player leaves a trail of rectangles. Sometimes that's intentional (see: Snake). Usually it's a bug.

### Calling `pygame.event.get()` multiple times per frame

```python
# WRONG — second call gets nothing, events already consumed
for event in pygame.event.get():
    if event.type == pygame.QUIT: ...

for event in pygame.event.get():  # Empty! Events already pulled above.
    if event.type == pygame.KEYDOWN: ...
```

`pygame.event.get()` drains the event queue. Call it once, handle everything in that one loop.

### Not calling `pygame.quit()`

On some systems, the window hangs on exit. Always clean up.

## What You Learned

- **The game loop** — input → update → draw, every frame
- **`pygame.time.Clock`** — locks the loop to a target FPS
- **Surfaces and blitting** — everything is pixel buffers copied onto each other
- **Coordinate system** — (0,0) is top-left, Y increases downward
- **Double buffering** — draw to back buffer, flip to show
- **Display modes** — windowed, fullscreen, resizable

You have a window. You have a rectangle. You have a loop running at 60 FPS.

Rena's feedback: "It doesn't move."

Fair. Let's fix that.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Movement →](chapter-02-movement.md)
