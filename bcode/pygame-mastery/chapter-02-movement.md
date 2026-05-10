# Chapter 2: Something Moves — Velocity and Delta Time

[← Chapter 1: Game Loop](chapter-01-game-loop.md) | [Chapter 3: Input →](chapter-03-input.md)

---

## The Problem

You have a window. You have a rectangle. Rena's feedback: "It doesn't move."

You try the obvious:

```python
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move right
    player_rect.x += 5

    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.display.flip()
    clock.tick(FPS)
```

The rectangle slides to the right and disappears off-screen. It moves. But:

1. It moves on its own — the player isn't controlling it (that's Chapter 3)
2. It moves at different speeds depending on FPS
3. There's no concept of velocity or direction

Let's fix #2 first, because it's the one that will haunt you for the entire project if you ignore it.

## The Frame Rate Problem

Your game runs at 60 FPS. Each frame, the player moves 5 pixels. That's 300 pixels/second.

But what if the game drops to 30 FPS during a particle-heavy boss fight? Now it's 150 pixels/second. The player moves at half speed when the game lags. Enemies slow down too. The whole game runs in slow motion.

What if someone has a 144Hz monitor and you unlock the frame rate? 720 pixels/second. Everything is twice as fast. Unplayable.

**Movement must be independent of frame rate.**

## Delta Time

The fix: multiply movement by the time elapsed since the last frame.

```python
dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
```

`clock.tick(60)` returns the number of milliseconds since the last call. At 60 FPS, that's ~16.6ms = 0.0166 seconds.

Now instead of "move 5 pixels per frame," you say "move 300 pixels per second":

```python
speed = 300  # pixels per second
player_rect.x += speed * dt
```

At 60 FPS: `300 * 0.0166 = 5.0` pixels per frame
At 30 FPS: `300 * 0.0333 = 10.0` pixels per frame
At 144 FPS: `300 * 0.0069 = 2.1` pixels per frame

Different pixels per frame, same pixels per second. The player moves at the same real-world speed regardless of frame rate.

## Vectors: Direction + Magnitude

A rectangle moving right is boring. Games need movement in any direction. Enter vectors.

A 2D vector has an x and y component:

```python
# Moving right:      (1, 0)
# Moving down:       (0, 1)
# Moving diagonally: (1, 1) — but this is wrong (we'll fix it)
```

Pygame has a built-in Vector2 class:

```python
import pygame

pos = pygame.math.Vector2(400, 300)
velocity = pygame.math.Vector2(200, -100)  # 200 px/s right, 100 px/s up

# Update position
pos += velocity * dt
```

### The Diagonal Problem

If the player holds RIGHT and DOWN simultaneously, the naive approach:

```python
direction = pygame.math.Vector2(0, 0)
if keys[pygame.K_RIGHT]:
    direction.x = 1
if keys[pygame.K_DOWN]:
    direction.y = 1

player_pos += direction * speed * dt
```

The direction vector is (1, 1). Its length (magnitude) is √2 ≈ 1.414. The player moves 41% faster diagonally than horizontally. Every player will notice.

The fix: **normalize** the direction vector (make its length exactly 1):

```python
if direction.length() > 0:
    direction = direction.normalize()

player_pos += direction * speed * dt
```

Now (1, 1) becomes (0.707, 0.707). Length = 1. Same speed in all directions.

## Floating Point Position

There's a subtle bug. `pygame.Rect` uses integers for position:

```python
player_rect = pygame.Rect(400, 300, 32, 32)
player_rect.x += 2.7  # Stored as 2! Truncated to int.
```

At high frame rates with small dt, movement per frame might be 0.8 pixels. Truncated to 0. The player doesn't move at all on fast machines.

The fix: store position as a float, convert to Rect only for drawing:

```python
# Position as float vector
player_pos = pygame.math.Vector2(400, 300)

# Update with full precision
player_pos += velocity * dt

# Convert to rect for drawing/collision
player_rect = pygame.Rect(int(player_pos.x), int(player_pos.y), 32, 32)
```

This is a pattern you'll use for the entire project: **float position for physics, integer rect for rendering.**

## The Complete Movement System

```python
import pygame
import sys

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Void Runners")
clock = pygame.time.Clock()
FPS = 60

BG_COLOR = (15, 15, 25)
PLAYER_COLOR = (0, 255, 180)
PLAYER_SIZE = 32
PLAYER_SPEED = 300  # pixels per second

# Float position for smooth movement
player_pos = pygame.math.Vector2(
    SCREEN_WIDTH // 2 - PLAYER_SIZE // 2,
    SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Input → direction vector
    keys = pygame.key.get_pressed()
    direction = pygame.math.Vector2(0, 0)

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        direction.y = -1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        direction.y = 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction.x = -1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction.x = 1

    # Normalize to prevent fast diagonals
    if direction.length() > 0:
        direction = direction.normalize()

    # Update position
    player_pos += direction * PLAYER_SPEED * dt

    # Keep player on screen
    player_pos.x = max(0, min(player_pos.x, SCREEN_WIDTH - PLAYER_SIZE))
    player_pos.y = max(0, min(player_pos.y, SCREEN_HEIGHT - PLAYER_SIZE))

    # Draw
    screen.fill(BG_COLOR)
    player_rect = pygame.Rect(int(player_pos.x), int(player_pos.y), PLAYER_SIZE, PLAYER_SIZE)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()
```

Run this. WASD or arrow keys move the player. Diagonal movement is the same speed as cardinal. The player stays on screen. Movement is frame-rate independent.

## Acceleration and Friction

Instant start/stop feels robotic. Real movement has inertia:

```python
ACCELERATION = 1500   # pixels/sec²
FRICTION = 800        # pixels/sec² (deceleration when no input)
MAX_SPEED = 350       # pixels/sec

velocity = pygame.math.Vector2(0, 0)

# In the game loop:
if direction.length() > 0:
    direction = direction.normalize()
    velocity += direction * ACCELERATION * dt
else:
    # Apply friction (decelerate toward zero)
    if velocity.length() > 0:
        friction_force = velocity.normalize() * FRICTION * dt
        if friction_force.length() > velocity.length():
            velocity = pygame.math.Vector2(0, 0)
        else:
            velocity -= friction_force

# Clamp to max speed
if velocity.length() > MAX_SPEED:
    velocity = velocity.normalize() * MAX_SPEED

# Update position
player_pos += velocity * dt
```

Now the player accelerates when you hold a key and decelerates when you release. It feels like the character has weight. Rena: "That feels better."

## Screen Wrapping vs. Clamping

Two common approaches for screen boundaries:

### Clamping (stay on screen):

```python
player_pos.x = max(0, min(player_pos.x, SCREEN_WIDTH - PLAYER_SIZE))
player_pos.y = max(0, min(player_pos.y, SCREEN_HEIGHT - PLAYER_SIZE))
```

### Wrapping (appear on other side):

```python
if player_pos.x > SCREEN_WIDTH:
    player_pos.x = -PLAYER_SIZE
elif player_pos.x < -PLAYER_SIZE:
    player_pos.x = SCREEN_WIDTH

if player_pos.y > SCREEN_HEIGHT:
    player_pos.y = -PLAYER_SIZE
elif player_pos.y < -PLAYER_SIZE:
    player_pos.y = SCREEN_HEIGHT
```

Void Runners uses clamping for now. When we add camera scrolling (Chapter 7), the player moves freely and the world scrolls around them.

## Multiple Entities

The player isn't alone. Let's add some enemies that move on their own:

```python
import random

class Entity:
    def __init__(self, x, y, size, color, speed):
        self.pos = pygame.math.Vector2(x, y)
        self.size = size
        self.color = color
        self.speed = speed
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ).normalize() * speed

    def update(self, dt):
        self.pos += self.velocity * dt

        # Bounce off walls
        if self.pos.x <= 0 or self.pos.x >= SCREEN_WIDTH - self.size:
            self.velocity.x *= -1
        if self.pos.y <= 0 or self.pos.y >= SCREEN_HEIGHT - self.size:
            self.velocity.y *= -1

        # Clamp to screen
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - self.size))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - self.size))

    def draw(self, surface):
        rect = pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)


# Create enemies
enemies = [
    Entity(
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT),
        24, (255, 60, 60), random.uniform(100, 200)
    )
    for _ in range(10)
]

# In the game loop:
for enemy in enemies:
    enemy.update(dt)
    enemy.draw(screen)
```

Ten red squares bouncing around the screen. They move independently, each with their own velocity. All frame-rate independent.

## Common Mistakes

### Forgetting dt

```python
# WRONG — speed depends on frame rate
player_pos.x += 5

# RIGHT — speed is consistent
player_pos.x += 300 * dt
```

This is the #1 beginner mistake. If you see movement without `* dt`, it's a bug.

### Normalizing a zero vector

```python
direction = pygame.math.Vector2(0, 0)
direction.normalize()  # ERROR! Can't normalize zero-length vector
```

Always check `if direction.length() > 0` before normalizing.

### Using Rect for sub-pixel movement

```python
# WRONG — loses precision
player_rect.x += int(speed * dt)  # Often rounds to 0

# RIGHT — float position, int for drawing
player_pos.x += speed * dt
player_rect.x = int(player_pos.x)
```

### Large dt spikes

If the game freezes for 1 second (loading, alt-tab), dt becomes 1.0. The player teleports 300 pixels. Cap dt:

```python
dt = min(clock.tick(FPS) / 1000.0, 0.05)  # Cap at 50ms (20 FPS minimum)
```

This prevents physics explosions during lag spikes.

## What You Learned

- **Delta time** — multiply movement by elapsed time for frame-rate independence
- **Vectors** — direction + magnitude, the language of 2D movement
- **Normalization** — make diagonal movement the same speed as cardinal
- **Float position** — store position as float, convert to int for rendering
- **Acceleration/friction** — makes movement feel physical
- **Screen boundaries** — clamping vs. wrapping
- **Entity pattern** — pos, velocity, update, draw

The player moves. Enemies bounce. Everything is smooth and frame-rate independent.

But there's a problem: we're reading input with `pygame.key.get_pressed()` directly in the game loop. That works for held keys, but what about single presses? What about mouse aiming? What about input buffering for responsive controls?

Rena: "I pressed dash but nothing happened. I swear I pressed it."

She did press it. The game just didn't notice. That's Chapter 3.

---

[← Chapter 1: Game Loop](chapter-01-game-loop.md) | [Chapter 3: Input →](chapter-03-input.md)
