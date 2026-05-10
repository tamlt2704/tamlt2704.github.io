# Chapter 3: Responding to Input — Keyboard, Mouse, and Buffering

[← Chapter 2: Movement](chapter-02-movement.md) | [Chapter 4: Collisions →](chapter-04-collisions.md)

---

## The Problem

Rena's playtest report, Friday evening:

"I pressed dash and nothing happened. I pressed shoot and it fired twice. When I aim with the mouse, the bullets go to where the cursor *was*, not where it *is*. Also, holding shoot should fire continuously but it only fires once."

Four bugs. All input-related. All because you're treating input as simpler than it is.

The current code uses `pygame.key.get_pressed()` for everything. That works for movement (held keys), but games need more:

- **Single press**: Dash, jump, interact (fire once per press)
- **Held keys**: Movement, charging (continuous while held)
- **Mouse position**: Aiming (where is the cursor right now?)
- **Mouse clicks**: Shooting (single shot vs. auto-fire)
- **Input buffering**: Accept input slightly before it's valid

## Two Input Systems

Pygame gives you two ways to read input:

### Event-Based (for single presses)

```python
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            player.dash()  # Fires ONCE when pressed
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_SPACE:
            player.end_dash()  # Fires ONCE when released
```

`KEYDOWN` fires once when the key is first pressed. `KEYUP` fires once when released. No repeats.

### State-Based (for held keys)

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_w]:
    direction.y = -1  # True EVERY FRAME the key is held
```

`get_pressed()` returns the current state of every key. It's a snapshot — true if held right now, false if not.

### When to Use Which

| Action | System | Why |
|---|---|---|
| Move | State-based | Continuous while held |
| Jump | Event-based | Once per press |
| Shoot (single) | Event-based | Once per press |
| Shoot (auto) | State-based + cooldown | Continuous with rate limit |
| Dash | Event-based | Once per press |
| Pause | Event-based | Toggle, not hold |
| Aim | State-based (mouse) | Continuous position |

## Mouse Input

### Position

```python
mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
```

This gives you the cursor position every frame. For aiming:

```python
# Direction from player to mouse
aim_direction = (mouse_pos - player_pos)
if aim_direction.length() > 0:
    aim_direction = aim_direction.normalize()
```

### Clicks (Event-Based)

```python
for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left click
            player.shoot(aim_direction)
        elif event.button == 3:  # Right click
            player.alt_fire(aim_direction)
```

### Held Mouse (State-Based)

```python
mouse_buttons = pygame.mouse.get_pressed()
if mouse_buttons[0]:  # Left button held
    # Auto-fire with cooldown
    pass
```

## Building the Input Manager

Mixing input logic throughout the game loop gets messy fast. Let's centralize it:

```python
class InputManager:
    def __init__(self):
        self.keys_pressed = set()   # Keys pressed THIS frame
        self.keys_released = set()  # Keys released THIS frame
        self.keys_held = set()      # Keys currently held
        self.mouse_pos = pygame.math.Vector2(0, 0)
        self.mouse_pressed = set()  # Buttons pressed THIS frame
        self.mouse_held = set()     # Buttons currently held
        self.quit_requested = False

    def update(self):
        """Call once per frame, before game logic."""
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_pressed.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_held.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_released.add(event.key)
                self.keys_held.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed.add(event.button)
                self.mouse_held.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_held.discard(event.button)

        self.mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())

    def is_pressed(self, key):
        """True only on the frame the key was first pressed."""
        return key in self.keys_pressed

    def is_held(self, key):
        """True every frame the key is held down."""
        return key in self.keys_held

    def is_released(self, key):
        """True only on the frame the key was released."""
        return key in self.keys_released

    def is_mouse_pressed(self, button=1):
        """True only on the frame the mouse button was clicked."""
        return button in self.mouse_pressed

    def is_mouse_held(self, button=1):
        """True every frame the mouse button is held."""
        return button in self.mouse_held

    def get_mouse_pos(self):
        return self.mouse_pos
```

Usage:

```python
input_mgr = InputManager()

while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)
    input_mgr.update()

    if input_mgr.quit_requested:
        running = False
    if input_mgr.is_pressed(pygame.K_ESCAPE):
        running = False

    # Movement (held)
    direction = pygame.math.Vector2(0, 0)
    if input_mgr.is_held(pygame.K_w):
        direction.y = -1
    if input_mgr.is_held(pygame.K_s):
        direction.y = 1
    if input_mgr.is_held(pygame.K_a):
        direction.x = -1
    if input_mgr.is_held(pygame.K_d):
        direction.x = 1

    # Dash (single press)
    if input_mgr.is_pressed(pygame.K_LSHIFT):
        player.dash()

    # Shoot (single click)
    if input_mgr.is_mouse_pressed(1):
        aim = (input_mgr.get_mouse_pos() - player_pos).normalize()
        spawn_bullet(player_pos, aim)
```

Clean separation: `is_pressed` for one-shot actions, `is_held` for continuous actions.

## Auto-Fire with Cooldown

Holding the mouse button should fire continuously, but not every frame (that's 60 bullets/second). Use a cooldown timer:

```python
class Weapon:
    def __init__(self, fire_rate):
        self.fire_rate = fire_rate  # Shots per second
        self.cooldown = 0.0

    def update(self, dt):
        self.cooldown = max(0, self.cooldown - dt)

    def can_fire(self):
        return self.cooldown <= 0

    def fire(self):
        self.cooldown = 1.0 / self.fire_rate
        return True  # Bullet spawned


weapon = Weapon(fire_rate=8)  # 8 shots per second

# In game loop:
weapon.update(dt)

if input_mgr.is_mouse_held(1) and weapon.can_fire():
    aim = (input_mgr.get_mouse_pos() - player_pos)
    if aim.length() > 0:
        aim = aim.normalize()
        spawn_bullet(player_pos, aim)
        weapon.fire()
```

Hold left mouse → fires 8 times per second. Release → stops. Click once → fires once (cooldown is 0 on first click).

## Input Buffering

Rena's complaint: "I pressed dash but nothing happened."

She pressed dash 2 frames before landing. The game checked "is player on ground?" — no — and ignored the input. By the time she landed, the KEYDOWN event was gone.

The fix: **buffer** inputs for a short window:

```python
class BufferedAction:
    def __init__(self, buffer_time=0.1):
        self.buffer_time = buffer_time  # seconds
        self.timer = 0.0
        self.buffered = False

    def request(self):
        """Player pressed the button."""
        self.buffered = True
        self.timer = self.buffer_time

    def update(self, dt):
        if self.buffered:
            self.timer -= dt
            if self.timer <= 0:
                self.buffered = False

    def consume(self):
        """Try to use the buffered input. Returns True if available."""
        if self.buffered:
            self.buffered = False
            return True
        return False


dash_buffer = BufferedAction(buffer_time=0.15)  # 150ms buffer

# When player presses dash:
if input_mgr.is_pressed(pygame.K_LSHIFT):
    dash_buffer.request()

dash_buffer.update(dt)

# When checking if player can dash:
if player.on_ground and dash_buffer.consume():
    player.start_dash()
```

Now if Rena presses dash up to 150ms before landing, it still triggers. The game feels responsive instead of punishing.

## Aim Direction with Visual Feedback

Players need to see where they're aiming:

```python
def draw_aim_indicator(surface, player_pos, mouse_pos):
    """Draw a line from player toward mouse cursor."""
    direction = mouse_pos - player_pos
    if direction.length() > 0:
        direction = direction.normalize()

    # Aim line (subtle)
    end_pos = player_pos + direction * 60
    pygame.draw.line(surface, (0, 255, 180, 128), 
                     (int(player_pos.x), int(player_pos.y)),
                     (int(end_pos.x), int(end_pos.y)), 2)

    # Crosshair at mouse
    mx, my = int(mouse_pos.x), int(mouse_pos.y)
    size = 8
    pygame.draw.line(surface, (255, 255, 255), (mx - size, my), (mx + size, my), 1)
    pygame.draw.line(surface, (255, 255, 255), (mx, my - size), (mx, my + size), 1)
```

Hide the system cursor and draw your own:

```python
pygame.mouse.set_visible(False)
```

## The Complete Chapter 3 Code

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

pygame.mouse.set_visible(False)

BG_COLOR = (15, 15, 25)
PLAYER_COLOR = (0, 255, 180)
BULLET_COLOR = (255, 255, 100)
PLAYER_SIZE = 32
PLAYER_SPEED = 300

player_pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
bullets = []

# Weapon system
fire_cooldown = 0.0
FIRE_RATE = 8  # shots per second

# Input manager (simplified inline for clarity)
running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)
    fire_cooldown = max(0, fire_cooldown - dt)

    # --- Input ---
    keys_pressed_this_frame = set()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_pressed_this_frame.add(event.key)
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
    mouse_held = pygame.mouse.get_pressed()

    # --- Movement (held keys) ---
    direction = pygame.math.Vector2(0, 0)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        direction.y = -1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        direction.y = 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction.x = -1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction.x = 1

    if direction.length() > 0:
        direction = direction.normalize()
    player_pos += direction * PLAYER_SPEED * dt

    # Clamp to screen
    player_pos.x = max(PLAYER_SIZE // 2, min(player_pos.x, SCREEN_WIDTH - PLAYER_SIZE // 2))
    player_pos.y = max(PLAYER_SIZE // 2, min(player_pos.y, SCREEN_HEIGHT - PLAYER_SIZE // 2))

    # --- Shooting (held mouse with cooldown) ---
    if mouse_held[0] and fire_cooldown <= 0:
        aim = mouse_pos - player_pos
        if aim.length() > 0:
            aim = aim.normalize()
            bullets.append({
                "pos": pygame.math.Vector2(player_pos),
                "vel": aim * 600,
            })
            fire_cooldown = 1.0 / FIRE_RATE

    # --- Update bullets ---
    for bullet in bullets:
        bullet["pos"] += bullet["vel"] * dt

    # Remove off-screen bullets
    bullets = [b for b in bullets if 0 <= b["pos"].x <= SCREEN_WIDTH
               and 0 <= b["pos"].y <= SCREEN_HEIGHT]

    # --- Draw ---
    screen.fill(BG_COLOR)

    # Player
    player_rect = pygame.Rect(
        int(player_pos.x - PLAYER_SIZE // 2),
        int(player_pos.y - PLAYER_SIZE // 2),
        PLAYER_SIZE, PLAYER_SIZE
    )
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, BULLET_COLOR, (int(bullet["pos"].x), int(bullet["pos"].y)), 4)

    # Crosshair
    mx, my = int(mouse_pos.x), int(mouse_pos.y)
    pygame.draw.line(screen, (255, 255, 255), (mx - 8, my), (mx + 8, my), 1)
    pygame.draw.line(screen, (255, 255, 255), (mx, my - 8), (mx, my + 8), 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
```

Run this. WASD to move, mouse to aim, hold left click to shoot. Bullets fly toward the cursor at 8/second. Crosshair follows the mouse.

## Common Mistakes

### Reading mouse position from the event

```python
# WRONG — only updates when mouse moves
if event.type == pygame.MOUSEMOTION:
    mouse_pos = event.pos

# RIGHT — always current
mouse_pos = pygame.mouse.get_pos()
```

The event gives you position only when the mouse moves. `get_pos()` gives you the current position every frame.

### Shooting toward the old mouse position

```python
# WRONG — aim calculated before events are processed
aim = (mouse_pos - player_pos).normalize()
for event in pygame.event.get():
    ...

# RIGHT — process events first, then read mouse
for event in pygame.event.get():
    ...
mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
aim = (mouse_pos - player_pos).normalize()
```

### Not handling zero-length aim vector

If the mouse is exactly on the player, `(mouse_pos - player_pos)` is (0, 0). Normalizing that crashes. Always check length > 0.

## What You Learned

- **Event-based vs. state-based** — single press vs. held
- **InputManager pattern** — centralized, clean input handling
- **Mouse aiming** — direction from player to cursor, normalized
- **Auto-fire with cooldown** — rate-limited continuous shooting
- **Input buffering** — accept input slightly early for responsiveness
- **Custom crosshair** — hide system cursor, draw your own

The player moves, aims, and shoots. Bullets fly across the screen. It feels like a game.

But the bullets pass through everything. Enemies don't react. Nothing collides with anything. The game has no consequences.

Time to make things hit each other.

---

[← Chapter 2: Movement](chapter-02-movement.md) | [Chapter 4: Collisions →](chapter-04-collisions.md)
