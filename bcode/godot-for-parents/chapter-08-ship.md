# Chapter 8: Polish and Ship It

[← Previous: Boss Fight](chapter-07-boss.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Playtests the whole game start to finish | Adds screen shake, particles, and juice |
| Picks a title and draws a title screen | Exports to HTML5 or Android |
| Decides who to share it with | Uploads and sends the link |

## Step 1: Screen Shake

When the player gets hit or the boss stomps, shake the camera. Kids love this.

```gdscript
# camera_shake.gd — Attach to your Camera2D
extends Camera2D

func shake(intensity: float = 5.0, duration: float = 0.3) -> void:
    var elapsed = 0.0
    while elapsed < duration:
        offset = Vector2(
            randf_range(-intensity, intensity),
            randf_range(-intensity, intensity)
        )
        elapsed += get_process_delta_time()
        await get_tree().process_frame
    offset = Vector2.ZERO
```

Call it from your player's `take_damage()`:

```gdscript
# In player.gd
func take_damage() -> void:
    if is_invincible:
        return
    current_lives -= 1
    # Shake the camera!
    var camera = get_viewport().get_camera_2d()
    if camera and camera.has_method("shake"):
        camera.shake(8.0, 0.4)
    # ... rest of damage code
```

## Step 2: Particles on Collect

Add a **GPUParticles2D** to your collectible that bursts when collected:

```gdscript
# Updated collectible.gd — Now with sparkles!
extends Area2D

@export var points: int = 10
@onready var particles = $BurstParticles
@onready var sprite = $Sprite2D

func _ready() -> void:
    body_entered.connect(_on_collected)

func _on_collected(body: Node2D) -> void:
    if body.name == "Player":
        ScoreManager.add_points(points)
        # Hide sprite, show particles, then disappear
        sprite.visible = false
        set_deferred("monitoring", false)
        particles.emitting = true
        await get_tree().create_timer(0.5).timeout
        queue_free()
```

## Step 3: Death Animation

When the player runs out of lives, use a Tween to spin and shrink the sprite before restarting. `tween_property(self, "rotation", TAU * 3, 1.0)` and `tween_property(self, "scale", Vector2.ZERO, 1.0)` in parallel. Await the tween, then reload the scene.

## Step 4: Title Screen

Kid draws a title screen. Create a **Control** scene with a **TextureRect** (their art) and a **Button** ("Play!"). Connect the button's `pressed` signal to `get_tree().change_scene_to_file("res://scenes/levels/level_1.tscn")`. Set this as your main scene in Project Settings.

## Step 5: Export to Web (HTML5)

1. Editor → Export → Add Preset → **Web**
2. Download the export template when prompted
3. Export Project → save as `index.html`
4. Upload to [itch.io](https://itch.io) (free, no account needed for viewing)
5. Share the link with grandparents, friends, the whole family

## The Sharing Moment

This is the payoff. Send the link to grandparents. Text it to aunts and uncles. Let your kid watch someone else play their game. The pride on their face is worth every Saturday morning.

## Keeping Kids Engaged

- Let them write the credits. "Game by [Kid's Name]. Code by [Parent's Name]."
- Ask: "What should happen when you win?" A victory screen with their art.
- Screen shake and particles are instant "wow" moments. Add them first.
- The export step is magic — "our game is on the INTERNET?!"

## What You Built Together

A polished, complete game with juice (screen shake, particles, animations), a title screen, and a shareable export. Nine Saturdays, one game, a hundred memories. Your kid is a game designer. You built it together.

---

## The Whole Course

| Chapter | What You Built |
|---------|---------------|
| 0–1 | Setup, movement |
| 2–3 | Collectibles, enemies |
| 4–5 | Levels, audio |
| 6–7 | Power-ups, boss fight |
| 8 | Polish and ship |

**Now go play your game together.**

---

[← Previous: Boss Fight](chapter-07-boss.md)
