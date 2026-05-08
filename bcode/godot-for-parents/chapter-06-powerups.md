# Chapter 6: Super Powers!

[← Previous: Audio](chapter-05-audio.md) | [Next: Chapter 7 - Boss Fight →](chapter-07-boss.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Invents a power-up (what it does, what it looks like) | Builds the power-up scene and logic |
| Draws the power-up item | Implements the Timer and visual feedback |
| Decides how long it lasts | Connects everything to the player |

## Step 1: Kid Designs the Power-Up

Ask your kid: "If your character could have ONE super power for 10 seconds, what would it be?"

Common answers:
- **Speed boost** — run super fast
- **Fly** — ignore gravity
- **Grow big** — become giant
- **Shoot** — throw projectiles
- **Invincible** — can't be hurt

We'll implement a speed boost. The pattern works for any power-up.

## Step 2: Power-Up Scene

1. New scene → **Area2D** as root (name it `PowerUp`)
2. Add **Sprite2D** → their power-up art
3. Add **CollisionShape2D** → sized to the sprite
4. Add **AnimationPlayer** → we'll make it bob up and down

Save as `res://scenes/power_up.tscn`.

## Step 3: Power-Up Script

```gdscript
# power_up.gd — Grants a temporary ability
extends Area2D

# How long the power lasts (kid picks this number)
@export var duration: float = 5.0
# How much faster the player goes
@export var speed_multiplier: float = 2.5

func _ready() -> void:
    body_entered.connect(_on_collected)
    # Make it bob up and down so it looks special
    _start_bobbing()

func _on_collected(body: Node2D) -> void:
    if body.name == "Player" and body.has_method("activate_power_up"):
        body.activate_power_up(speed_multiplier, duration)
        queue_free()

func _start_bobbing() -> void:
    var tween = create_tween().set_loops()
    tween.tween_property(self, "position:y", position.y - 8, 0.5)
    tween.tween_property(self, "position:y", position.y, 0.5)
```

## Step 4: Player Power-Up Logic

Add this to your player script:

```gdscript
# Add to player.gd
var base_speed: float = 200.0
var is_powered_up: bool = false

func activate_power_up(multiplier: float, duration: float) -> void:
    is_powered_up = true
    speed = base_speed * multiplier

    # Visual feedback — glow yellow!
    modulate = Color(1, 1, 0.3, 1)

    # Start a timer for the duration
    var timer = get_tree().create_timer(duration)
    await timer.timeout

    # Power wears off
    speed = base_speed
    modulate = Color(1, 1, 1, 1)
    is_powered_up = false
```

## Step 5: Visual Feedback with Particles

Add a **GPUParticles2D** child to the Player. Enable `emitting` when powered up, disable when it wears off. Yellow/white sparkles with short lifetime look great.

## Other Power-Up Ideas

| Power | What to Change |
|-------|---------------|
| Fly | Set gravity to 0, allow upward movement |
| Grow big | `scale = Vector2(2, 2)` on the player |
| Invincible | Set `is_invincible = true` |
| Shoot | Instance a projectile scene on key press |

The pattern is always: change a property → start a timer → revert the property.

## Keeping Kids Engaged

- The power-up is THEIR invention. Use their exact words for the variable names if you can.
- Let them decide the duration. "5 seconds? 10? 100?" (Negotiate down from 100.)
- Particles make everything feel magical. Even simple white dots = excitement.
- Ask: "Where should the power-up appear? Before the hard part or after?"

## What You Built Together

A power-up system with visual feedback, a timer, and particles. Your kid invented a super power, and now it exists in their game. The pattern you learned (activate → timer → deactivate) works for any temporary ability they dream up next.

---

[← Previous: Audio](chapter-05-audio.md) | [Next: Chapter 7 - Boss Fight →](chapter-07-boss.md)
