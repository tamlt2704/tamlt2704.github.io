# Chapter 2: Coins, Stars, and Shiny Things

[← Previous: Movement](chapter-01-movement.md) | [Next: Chapter 3 - Enemies →](chapter-03-enemies.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Draws 2–3 collectible items (coins, gems, stars) | Imports art and creates the collectible scene |
| Decides how many points each one is worth | Writes the signal logic and score UI |
| Places collectibles around the level | Connects everything together |

## Step 1: The Collectible Scene

Kid draws a coin (or star, or gem, or taco — whatever they want to collect).

1. New scene → **Area2D** as root (name it `Collectible`)
2. Add **Sprite2D** → assign their collectible art
3. Add **CollisionShape2D** → CircleShape2D, sized to match the sprite

Save as `res://scenes/collectible.tscn`.

## Step 2: Collectible Script

```gdscript
# collectible.gd — Disappears when the player touches it
extends Area2D

# How many points this item is worth (let your kid decide!)
@export var points: int = 10

func _ready() -> void:
    # Connect the signal: when a body enters our area, call _on_collected
    body_entered.connect(_on_collected)

func _on_collected(body: Node2D) -> void:
    # Only react to the player
    if body.name == "Player":
        # Tell the game we scored points
        ScoreManager.add_points(points)
        # Disappear!
        queue_free()
```

## Step 3: Score Manager (Autoload)

Create a simple global script to track the score:

```gdscript
# score_manager.gd — Keeps track of points across the whole game
extends Node

var score: int = 0

signal score_changed(new_score: int)

func add_points(amount: int) -> void:
    score += amount
    score_changed.emit(score)

func reset() -> void:
    score = 0
    score_changed.emit(score)
```

Enable it: Project → Project Settings → Autoload → add `score_manager.gd` as `ScoreManager`.

## Step 4: Score Display

Add a **CanvasLayer** to your World scene, then add a **Label** child:

```gdscript
# score_label.gd — Shows the score on screen
extends Label

func _ready() -> void:
    ScoreManager.score_changed.connect(_on_score_changed)
    text = "Score: 0"

func _on_score_changed(new_score: int) -> void:
    text = "Score: " + str(new_score)
```

## Step 5: Scatter Collectibles

Duplicate the collectible scene around your level. Let your kid decide where they go. "Put one on that ledge!" "Put three in a row here!"

## How Signals Work (The Simple Version)

Signals are like a doorbell. The Area2D says "someone entered me!" and your script hears it and reacts. No polling, no checking every frame — just an event when it happens.

```
Area2D detects overlap → emits body_entered → your function runs → item disappears
```

## Keeping Kids Engaged

- Let them place every single collectible. Drag and drop in the editor is kid-friendly.
- Make the score label big and colorful. Kids love watching numbers go up.
- Ask: "What sound should it make?" (we'll add sounds in Chapter 5 — write it down!)
- If they want 1000-point items, let them. It's their game.

## What You Built Together

Collectible items your kid designed that disappear when touched, a score that goes up on screen, and the foundation of signals — Godot's way of making things talk to each other.

---

[← Previous: Movement](chapter-01-movement.md) | [Next: Chapter 3 - Enemies →](chapter-03-enemies.md)
