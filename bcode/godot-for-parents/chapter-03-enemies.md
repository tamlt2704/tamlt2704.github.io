# Chapter 3: The Monster That Chases You

[← Previous: Collectibles](chapter-02-collectibles.md) | [Next: Chapter 4 - Levels →](chapter-04-levels.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Draws the scariest monster they can imagine | Imports art, builds the enemy scene |
| Decides how fast the monster moves | Writes the chase AI |
| Decides how many lives the player gets | Adds the lives system and damage |

## Step 1: The Enemy Scene

Kid draws a monster. The weirder the better — three eyes, tentacle arms, whatever.

1. New scene → **CharacterBody2D** as root (name it `Enemy`)
2. Add **Sprite2D** → assign the monster art
3. Add **CollisionShape2D** → size it to the monster
4. Add an **Area2D** child (name it `HitZone`) with its own **CollisionShape2D** — slightly larger than the body

Save as `res://scenes/enemy.tscn`.

## Step 2: Chase AI

The simplest enemy AI: move toward the player every frame.

```gdscript
# enemy.gd — A monster that chases the player
extends CharacterBody2D

# How fast the monster moves (slower than player = fair, faster = scary)
@export var speed: float = 80.0

func _physics_process(_delta: float) -> void:
    # Find the player in the scene
    var player = get_tree().get_first_node_in_group("player")
    if player == null:
        return

    # Calculate direction toward the player
    var direction = (player.global_position - global_position).normalized()

    # Move toward them
    velocity = direction * speed
    move_and_slide()
```

**Important:** Add your Player node to a group called `"player"` (Node → Groups tab in the editor).

## Step 3: Damage on Contact

Add this to the Enemy's `HitZone` Area2D:

```gdscript
# hit_zone.gd — Hurts the player on contact
extends Area2D

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.name == "Player" and body.has_method("take_damage"):
        body.take_damage()
```

## Step 4: Lives System

Update your player script to handle damage:

```gdscript
# Add these to player.gd
@export var max_lives: int = 3
var current_lives: int = max_lives
var is_invincible: bool = false

func take_damage() -> void:
    if is_invincible:
        return
    current_lives -= 1
    if current_lives <= 0:
        # Game over! (restart the scene for now)
        get_tree().reload_current_scene()
    else:
        # Brief invincibility so you don't lose all lives instantly
        is_invincible = true
        # Flash the sprite to show damage
        modulate = Color(1, 0.3, 0.3, 0.7)
        await get_tree().create_timer(1.5).timeout
        modulate = Color(1, 1, 1, 1)
        is_invincible = false
```

## Step 5: Lives Display

Add a Label to your CanvasLayer that reads `player.current_lives` each frame and displays "Lives: X". Same pattern as the score label from Chapter 2.

## Keeping Kids Engaged

- Ask them: "Should the monster be fast or slow?" Start slow — they can always say "make it faster!"
- Let them place the monster in the level. Where's the scariest spot?
- If they want multiple monsters, just duplicate the scene. Instant swarm.
- "What happens when you lose all lives?" Let them decide (restart, game over screen, silly animation).

## What You Built Together

A hand-drawn monster that chases the player using simple AI, a lives system with invincibility frames, and the tension that makes a game feel like a game. Your kid designed something scary, and now it's hunting them on screen.

---

[← Previous: Collectibles](chapter-02-collectibles.md) | [Next: Chapter 4 - Levels →](chapter-04-levels.md)
