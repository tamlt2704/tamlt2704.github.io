# Chapter 5: Making It Sound Like a Game

[← Previous: Levels](chapter-04-levels.md) | [Next: Chapter 6 - Power-Ups →](chapter-06-powerups.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Picks sounds for each event (jump, coin, monster) | Imports audio files and sets up players |
| Records voice lines or sound effects with their mouth | Hooks audio to game events |
| Decides what the monster sounds like | Connects AudioStreamPlayer nodes to signals |

## Step 1: Gather Sounds

Three options, all fun:

1. **Kid records them** — Use your phone's voice recorder. "Boing!" for jump, "Cha-ching!" for coins, "RAWR!" for the monster. Export as `.wav` or `.ogg`.
2. **Pick from free libraries** — [freesound.org](https://freesound.org) or [kenney.nl/assets](https://kenney.nl/assets) have great free game sounds.
3. **Both** — Free sounds for background, kid voices for special moments.

Drop audio files into `res://audio/`.

## Step 2: Add Audio to the Player

Add an **AudioStreamPlayer2D** node to your Player scene for each sound:

```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── JumpSound (AudioStreamPlayer2D)
└── HurtSound (AudioStreamPlayer2D)
```

Drag audio files into each node's `Stream` property.

## Step 3: Play Sounds on Events

Update your player script:

```gdscript
# Add to player.gd
@onready var jump_sound = $JumpSound
@onready var hurt_sound = $HurtSound

func take_damage() -> void:
    if is_invincible:
        return
    hurt_sound.play()
    # ... rest of damage code
```

## Step 4: Collectible Sound

Add an AudioStreamPlayer2D to your Collectible scene:

```gdscript
# Updated collectible.gd — Now with sound!
extends Area2D

@export var points: int = 10
@onready var collect_sound = $CollectSound

func _ready() -> void:
    body_entered.connect(_on_collected)

func _on_collected(body: Node2D) -> void:
    if body.name == "Player":
        ScoreManager.add_points(points)
        # Play sound before disappearing
        collect_sound.play()
        # Hide the sprite but wait for sound to finish
        visible = false
        set_deferred("monitoring", false)
        await collect_sound.finished
        queue_free()
```

## Step 5: Enemy Sounds

Give the monster a growl or footstep sound:

```gdscript
# Add to enemy.gd
@onready var growl_sound = $GrowlSound

func _ready() -> void:
    # Play growl on a loop or at random intervals
    _growl_loop()

func _growl_loop() -> void:
    while is_inside_tree():
        await get_tree().create_timer(randf_range(3.0, 6.0)).timeout
        if is_inside_tree():
            growl_sound.play()
```

## Recording Tips

- **Quiet room** — bathroom with the door closed works great
- **Close to the mic** — phone 6 inches from their mouth
- **Short clips** — 1-2 seconds max for sound effects
- **Multiple takes** — record 5, pick the funniest one together
- **Format** — `.ogg` for music, `.wav` for short effects

## Keeping Kids Engaged

- Recording sounds is hilarious. Monster growls will have you both laughing.
- Let them be the voice of the character. "Ow!" when hit, "Yeah!" when collecting.
- Play the game with sound off, then with sound on. They'll hear the difference immediately.
- If they want background music, hum something together and record it. Imperfect is charming.

## What You Built Together

A game that sounds alive — coins that chime, monsters that growl, a character that reacts. And some of those sounds are your kid's actual voice, which makes this game truly one-of-a-kind.

---

[← Previous: Levels](chapter-04-levels.md) | [Next: Chapter 6 - Power-Ups →](chapter-06-powerups.md)
