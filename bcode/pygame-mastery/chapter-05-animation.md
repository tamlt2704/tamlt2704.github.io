# Chapter 5: Sprite Sheets — Making It Look Like a Game

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Sound & Music →](chapter-06-audio.md)

---

## The Problem

Kai finally snaps: "I've sent you 47 sprite sheets. The game is still colored rectangles. I'm doing art for free and you're not using it."

Fair. The game plays well but looks like a programmer-art prototype. Players judge games by visuals in the first 3 seconds. Colored rectangles say "unfinished."

Time to load real art, animate it, and make the player character feel alive.

## Loading a Single Image

The simplest case — one image, one sprite:

```python
# Load image
player_image = pygame.image.load("assets/player.png").convert_alpha()

# Draw it
screen.blit(player_image, player_rect)
```

`convert_alpha()` converts the image to the display's pixel format with transparency support. Without it, blitting is slower (Pygame converts on every frame).

### Common image issues:

```python
# FileNotFoundError — wrong path
# Fix: use os.path or pathlib
import os
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, "assets", "player.png")
player_image = pygame.image.load(image_path).convert_alpha()
```

## Sprite Sheets

Game art comes as sprite sheets — a single image containing multiple frames arranged in a grid:

```
┌────┬────┬────┬────┐
│ F0 │ F1 │ F2 │ F3 │  ← Idle animation (4 frames)
├────┼────┼────┼────┤
│ F0 │ F1 │ F2 │ F3 │  ← Run animation (4 frames)
├────┼────┼────┼────┤
│ F0 │ F1 │ F2 │ F3 │  ← Attack animation (4 frames)
└────┴────┴────┴────┘
```

Each cell is the same size (e.g., 32×32 or 64×64). You extract individual frames by slicing:

```python
def load_spritesheet(path, frame_width, frame_height):
    """Load a sprite sheet and extract individual frames."""
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    frames = []
    for y in range(0, sheet_height, frame_height):
        row = []
        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
            row.append(frame)
        frames.append(row)

    return frames  # frames[row][col]
```

Usage:

```python
# Load 32x32 frames from a sprite sheet
frames = load_spritesheet("assets/player_sheet.png", 32, 32)

idle_frames = frames[0]    # First row: idle
run_frames = frames[1]     # Second row: run
attack_frames = frames[2]  # Third row: attack
```

## Frame Animation

Cycling through frames at a fixed rate:

```python
class Animation:
    def __init__(self, frames, speed=0.1, loop=True):
        """
        frames: list of Surface objects
        speed: seconds per frame
        loop: whether to repeat
        """
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.timer = 0.0
        self.frame_index = 0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        self.timer += dt
        if self.timer >= self.speed:
            self.timer -= self.speed
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        return self.frames[self.frame_index]

    def reset(self):
        self.frame_index = 0
        self.timer = 0.0
        self.finished = False
```

Usage:

```python
idle_anim = Animation(idle_frames, speed=0.15, loop=True)
run_anim = Animation(run_frames, speed=0.08, loop=True)
attack_anim = Animation(attack_frames, speed=0.05, loop=False)

# In update:
current_anim.update(dt)

# In draw:
screen.blit(current_anim.get_frame(), player_rect)
```

## Animation State Machine

The player has multiple animations. Which one plays depends on what they're doing:

```python
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, spritesheet_path, frame_size):
        super().__init__()
        frames = load_spritesheet(spritesheet_path, *frame_size)

        self.animations = {
            "idle": Animation(frames[0], speed=0.15, loop=True),
            "run": Animation(frames[1], speed=0.08, loop=True),
            "attack": Animation(frames[2], speed=0.05, loop=False),
            "hurt": Animation(frames[3], speed=0.1, loop=False),
        }

        self.state = "idle"
        self.facing_right = True
        self.image = self.animations[self.state].get_frame()
        self.rect = self.image.get_rect()

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.animations[self.state].reset()

    def update(self, dt, velocity):
        # Determine state from movement
        if self.state not in ("attack", "hurt"):  # Don't interrupt these
            if velocity.length() > 10:
                self.set_state("run")
            else:
                self.set_state("idle")

        # Track facing direction
        if velocity.x > 0:
            self.facing_right = True
        elif velocity.x < 0:
            self.facing_right = False

        # Update animation
        anim = self.animations[self.state]
        anim.update(dt)

        # Handle non-looping animations finishing
        if anim.finished:
            self.set_state("idle")

        # Get current frame, flip if facing left
        self.image = anim.get_frame()
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def attack(self):
        self.set_state("attack")

    def hurt(self):
        self.set_state("hurt")
```

The state machine ensures:
- Moving → run animation
- Standing still → idle animation
- Attack interrupts movement animation
- Hurt interrupts everything
- Non-looping animations return to idle when done
- Sprite flips horizontally based on direction

## Scaling Sprites

Pixel art should be scaled with nearest-neighbor (no blurring):

```python
# Scale 2x (pixel-perfect)
scaled = pygame.transform.scale(original, (original.get_width() * 2, original.get_height() * 2))

# For the entire display (render at low res, scale up):
INTERNAL_WIDTH = 400
INTERNAL_HEIGHT = 300
internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

# Draw everything to internal_surface at low res
# Then scale up to display:
scaled_surface = pygame.transform.scale(internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
screen.blit(scaled_surface, (0, 0))
```

This gives you crisp pixel art at any window size.

## Rotation

For bullets or enemies that face their movement direction:

```python
import math

def get_rotation_angle(velocity):
    """Get angle in degrees from velocity vector."""
    return math.degrees(math.atan2(-velocity.y, velocity.x))

# Rotate sprite
angle = get_rotation_angle(bullet.velocity)
rotated = pygame.transform.rotate(bullet_image, angle)
# Rotation changes the rect size — recenter it
rotated_rect = rotated.get_rect(center=bullet.rect.center)
screen.blit(rotated, rotated_rect)
```

Warning: rotating every frame is expensive. For bullets that don't change direction, rotate once on creation and cache it.

## Color Tinting (Damage Flash)

When an enemy takes damage, flash it white for one frame:

```python
def tint_surface(surface, color):
    """Create a white-tinted copy of a surface (for damage flash)."""
    tinted = surface.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGB_ADD)
    return tinted

# In enemy draw:
if self.flash_timer > 0:
    screen.blit(tint_surface(self.image, (200, 200, 200)), self.rect)
    self.flash_timer -= dt
else:
    screen.blit(self.image, self.rect)
```

## Putting It Together (Without Real Assets)

Since you might not have Kai's sprite sheets, here's how to generate placeholder animated sprites programmatically:

```python
def make_placeholder_frames(size, color, frame_count=4):
    """Generate simple animated placeholder frames."""
    frames = []
    for i in range(frame_count):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Pulsing size for "animation"
        offset = int(2 * math.sin(i * math.pi / frame_count * 2))
        rect = pygame.Rect(offset, offset, size - offset * 2, size - offset * 2)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        # Frame indicator dot
        pygame.draw.circle(surface, (255, 255, 255),
                          (size // 2, size - 4), 2)
        frames.append(surface)
    return frames

idle_frames = make_placeholder_frames(32, (0, 255, 180), 4)
run_frames = make_placeholder_frames(32, (0, 200, 255), 6)
```

Replace these with real art when Kai's assets arrive. The animation system doesn't care what the frames look like.

## What You Learned

- **Loading images** — `pygame.image.load().convert_alpha()`
- **Sprite sheets** — single image, grid of frames, slice by coordinates
- **Frame animation** — timer-based cycling through frame list
- **Animation state machine** — idle/run/attack/hurt with transitions
- **Facing direction** — `pygame.transform.flip()` for horizontal mirror
- **Scaling** — nearest-neighbor for pixel art, internal resolution
- **Rotation** — `pygame.transform.rotate()` for directional sprites
- **Color tinting** — damage flash with `BLEND_RGB_ADD`

The game looks like a game now. Characters animate. They face the right direction. They flash when hit. It's no longer programmer art.

But it's silent. No sound effects, no music. Rena: "I can't tell when I'm hitting things. There's no audio feedback."

---

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Sound & Music →](chapter-06-audio.md)
