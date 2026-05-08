# Chapter 1: Making Their Character Walk

[← Previous: Overview](chapter-00-overview.md) | [Next: Chapter 2 - Collectibles →](chapter-02-collectibles.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Draws their character on paper | Photographs and imports the art |
| Decides how fast the character should move | Writes the movement script |
| Playtests and says "faster!" or "slower!" | Tweaks the speed value |

## Step 1: Import the Character Art

Have your kid draw their hero. Photograph it, remove the background, save as `player.png` in `res://sprites/`.

## Step 2: Build the Player Scene

1. Create a new scene → **CharacterBody2D** as root (name it `Player`)
2. Add a **Sprite2D** child → drag `player.png` into the Texture property
3. Add a **CollisionShape2D** child → set shape to RectangleShape2D, resize to fit the sprite

Save as `res://scenes/player.tscn`.

## Step 3: The Movement Script

Attach a script to the Player node. Here's the full movement code:

```gdscript
# player.gd — Makes our character move with arrow keys or WASD
extends CharacterBody2D

# How fast the character moves (let your kid pick this number!)
@export var speed: float = 200.0

func _physics_process(_delta: float) -> void:
    # Get input direction: returns a Vector2 like (1, 0) or (-1, 1)
    var direction = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")

    # Set velocity based on direction and speed
    velocity = direction * speed

    # Actually move the character (handles collisions automatically)
    move_and_slide()
```

## What Each Line Does

- `@export var speed` — Shows up in the editor. Your kid can drag the slider to change speed without touching code.
- `Input.get_vector()` — Reads arrow keys/WASD and returns a direction. Handles diagonals properly.
- `velocity` — Built into CharacterBody2D. Set it, then call `move_and_slide()`.
- `move_and_slide()` — Moves the character and stops at walls. One line does all the physics.

## Step 4: Create the Main Scene

1. New scene → **Node2D** as root (name it `World`)
2. Instance your Player scene (drag `player.tscn` in, or use the link icon)
3. Add a **Camera2D** as a child of the Player node (check "Current" in inspector)
4. Press F5 to run — pick this scene as main

Your kid's character moves around. That's it. That's the game (so far).

## Make It Better Together

Ask your kid:
- "Should the character face the direction they're moving?" (flip the sprite)
- "What should the background color be?" (Project → Project Settings → Rendering → Environment)
- "Is it too fast or too slow?" (change the speed export)

## Keeping Kids Engaged

- Run the game every time you change something. Kids need to see results.
- Let them hold the keyboard while you type. They press the arrow keys to test.
- If they want the character to fly, say "that's Chapter 6!" and write it on a sticky note.

## What You Built Together

A character drawn by your kid that moves around the screen with arrow keys. Their art is alive. That feeling — "I drew that and now it MOVES" — is the whole point.

---

[← Previous: Overview](chapter-00-overview.md) | [Next: Chapter 2 - Collectibles →](chapter-02-collectibles.md)
