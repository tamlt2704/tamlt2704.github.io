# Chapter 13: Gamepad Support — Beyond Keyboard and Mouse

[← Chapter 12: Performance](chapter-12-performance.md) | [Chapter 14: Polish & Juice →](chapter-14-polish.md)

---

## The Problem

Rena: "I tried playing on my couch with a controller. Nothing worked. This is a twin-stick shooter — it should support gamepads natively."

She's right. Void Runners is a top-down shooter. The genre was born on gamepads. Left stick moves, right stick aims. Triggers shoot. It's the natural input method.

## Pygame Joystick Basics

```python
# Initialize joystick subsystem
pygame.joystick.init()

# Check for connected controllers
joystick_count = pygame.joystick.get_count()
print(f"Controllers found: {joystick_count}")

# Initialize the first controller
if joystick_count > 0:
    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
    print(f"Controller: {gamepad.get_name()}")
    print(f"Axes: {gamepad.get_numaxes()}")
    print(f"Buttons: {gamepad.get_numbuttons()}")
```

## Reading Stick Input

```python
# Axis mapping (Xbox layout):
# Axis 0: Left stick X (-1 left, +1 right)
# Axis 1: Left stick Y (-1 up, +1 down)
# Axis 2: Right stick X
# Axis 3: Right stick Y
# Axis 4: Left trigger (0 to 1)
# Axis 5: Right trigger (0 to 1)

DEAD_ZONE = 0.15  # Ignore small stick movements

def get_stick(joystick, x_axis, y_axis):
    """Read a stick with dead zone applied."""
    x = joystick.get_axis(x_axis)
    y = joystick.get_axis(y_axis)

    # Apply dead zone
    magnitude = (x ** 2 + y ** 2) ** 0.5
    if magnitude < DEAD_ZONE:
        return pygame.math.Vector2(0, 0)

    # Normalize and rescale (so edge of dead zone = 0, full tilt = 1)
    direction = pygame.math.Vector2(x, y)
    normalized_magnitude = (magnitude - DEAD_ZONE) / (1.0 - DEAD_ZONE)
    normalized_magnitude = min(1.0, normalized_magnitude)
    return direction.normalize() * normalized_magnitude
```

### Dead Zones

Without a dead zone, the stick drifts. Even when centered, most sticks report small non-zero values (0.01–0.1). The dead zone ignores values below a threshold.

```
Without dead zone:     With dead zone:
  Stick at rest:         Stick at rest:
  x=0.03, y=-0.02       x=0, y=0 (ignored)
  → player slowly        → player stays still
    drifts down-right
```

## Input Abstraction Layer

Support both keyboard+mouse AND gamepad with a unified interface:

```python
class InputState:
    """Unified input regardless of device."""
    def __init__(self):
        self.move_direction = pygame.math.Vector2(0, 0)
        self.aim_direction = pygame.math.Vector2(0, 0)
        self.shoot = False
        self.dash = False
        self.pause = False
        self.confirm = False


class InputHandler:
    def __init__(self):
        self.gamepad = None
        self.using_gamepad = False

        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()

    def update(self, events):
        state = InputState()

        # Check for gamepad connection/disconnection
        for event in events:
            if event.type == pygame.JOYDEVICEADDED:
                self.gamepad = pygame.joystick.Joystick(event.device_index)
                self.gamepad.init()
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.gamepad = None
                self.using_gamepad = False

        # Read gamepad
        if self.gamepad:
            gp_move = get_stick(self.gamepad, 0, 1)
            gp_aim = get_stick(self.gamepad, 2, 3)

            if gp_move.length() > 0 or gp_aim.length() > 0:
                self.using_gamepad = True

            if self.using_gamepad:
                state.move_direction = gp_move
                state.aim_direction = gp_aim

                # Right trigger = shoot
                rt = self.gamepad.get_axis(5)
                state.shoot = rt > 0.5

                # A button = dash (button 0 on Xbox)
                state.dash = self.gamepad.get_button(0)

                # Start button = pause (button 7 on Xbox)
                state.pause = self.gamepad.get_button(7)

                # A button = confirm in menus
                state.confirm = self.gamepad.get_button(0)

        # Read keyboard+mouse (overrides gamepad if used)
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        kb_move = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]: kb_move.y = -1
        if keys[pygame.K_s]: kb_move.y = 1
        if keys[pygame.K_a]: kb_move.x = -1
        if keys[pygame.K_d]: kb_move.x = 1

        if kb_move.length() > 0:
            self.using_gamepad = False
            state.move_direction = kb_move.normalize()

        if not self.using_gamepad:
            # Mouse aim
            mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
            # (aim_direction computed relative to player in game logic)
            state.aim_direction = mouse_pos  # Raw position, game converts to direction
            state.shoot = mouse_buttons[0]

        # Keyboard events (single press)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    state.dash = True
                if event.key == pygame.K_ESCAPE:
                    state.pause = True
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state.confirm = True
                if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    self.using_gamepad = False

        return state
```

## Gamepad Aim → Bullet Direction

With a mouse, aim direction is `(mouse_pos - player_pos).normalize()`. With a stick, the aim direction IS the stick value:

```python
# In gameplay:
input_state = input_handler.update(events)

if input_handler.using_gamepad:
    # Right stick directly gives aim direction
    aim = input_state.aim_direction
    if aim.length() > 0.3:  # Only aim if stick is pushed enough
        player.aim_direction = aim.normalize()
else:
    # Mouse position → direction from player
    mouse_pos = input_state.aim_direction  # Raw mouse position
    aim = mouse_pos - player.pos
    if aim.length() > 0:
        player.aim_direction = aim.normalize()
```

## Cursor Visibility

Hide the mouse cursor when using gamepad, show it when using keyboard:

```python
# In game loop:
if input_handler.using_gamepad:
    pygame.mouse.set_visible(False)
    # Draw aim reticle at player position + aim direction
    reticle_pos = player.pos + player.aim_direction * 60
    draw_reticle(screen, reticle_pos, camera)
else:
    pygame.mouse.set_visible(False)  # We draw our own crosshair
    draw_crosshair(screen, pygame.mouse.get_pos())
```

## Rumble/Vibration

Pygame CE supports haptic feedback:

```python
if hasattr(gamepad, 'rumble'):
    # When player takes damage:
    gamepad.rumble(0.7, 0.7, 200)  # low_freq, high_freq, duration_ms

    # When shooting:
    gamepad.rumble(0.2, 0.4, 50)

    # When big explosion:
    gamepad.rumble(1.0, 1.0, 300)
```

## Hot-Swapping

Players might plug in a controller mid-game or unplug it:

```python
for event in events:
    if event.type == pygame.JOYDEVICEADDED:
        print(f"Controller connected: {event.device_index}")
        self.gamepad = pygame.joystick.Joystick(event.device_index)
        self.gamepad.init()
        self.using_gamepad = True

    elif event.type == pygame.JOYDEVICEREMOVED:
        print("Controller disconnected")
        self.gamepad = None
        self.using_gamepad = False
        pygame.mouse.set_visible(True)
```

## What You Learned

- **Joystick API** — axes, buttons, initialization
- **Dead zones** — ignore stick drift near center
- **Input abstraction** — unified InputState for any device
- **Twin-stick aiming** — right stick as direct aim direction
- **Auto-detection** — switch between gamepad/keyboard seamlessly
- **Rumble** — haptic feedback for impacts
- **Hot-swapping** — handle connect/disconnect events

The game supports both input methods. Players on the couch use a controller. Players at a desk use keyboard+mouse. The game detects which one you're using and adapts.

Almost there. The game works, performs well, and supports multiple input methods. But it still feels a bit... mechanical. Time for the final layer of polish.

---

[← Chapter 12: Performance](chapter-12-performance.md) | [Chapter 14: Polish & Juice →](chapter-14-polish.md)
