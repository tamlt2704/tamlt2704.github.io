# Chapter 7: The Final Boss

[← Previous: Power-Ups](chapter-06-powerups.md) | [Next: Chapter 8 - Ship It →](chapter-08-ship.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Designs the boss (what it looks like, how it attacks) | Builds the boss scene with a state machine |
| Decides the boss's 3 phases | Implements each phase as a state |
| Draws the boss's health bar | Creates the health bar UI |

## Step 1: Kid Designs the Boss

This is the big creative moment. Ask your kid:
- "What does the final boss look like?" (Draw it!)
- "How does it attack?" (Shoots fireballs? Charges at you? Stomps the ground?)
- "What makes it vulnerable?" (Stops to rest? Opens its mouth? Turns around?)
- "How many hits to defeat it?"

Write down their answers. These become the three phases.

## Step 2: Boss Scene Setup

1. New scene → **CharacterBody2D** as root (name it `Boss`)
2. Add **Sprite2D** → their boss art
3. Add **CollisionShape2D** → sized to the boss
4. Add **Area2D** (name it `HitBox`) → for damaging the player
5. Add **Area2D** (name it `WeakSpot`) → for taking damage

Save as `res://scenes/boss.tscn`.

## Step 3: State Machine

The boss cycles through phases. Each phase has different behavior:

```gdscript
# boss.gd — A boss with 3 phases
extends CharacterBody2D

enum State { IDLE, ATTACK, VULNERABLE }

@export var max_health: int = 9
var health: int = max_health
var current_state: State = State.IDLE

signal health_changed(new_health: int, max_hp: int)
signal defeated

func _ready() -> void:
    $WeakSpot.body_entered.connect(_on_weak_spot_hit)
    health_changed.emit(health, max_health)
    _start_cycle()

func _start_cycle() -> void:
    # Boss loop: idle → attack → vulnerable → repeat
    while health > 0:
        # Phase 1: Idle (boss taunts or moves around)
        current_state = State.IDLE
        await get_tree().create_timer(2.0).timeout

        # Phase 2: Attack (boss does something dangerous)
        current_state = State.ATTACK
        _do_attack()
        await get_tree().create_timer(3.0).timeout

        # Phase 3: Vulnerable (player can hit the boss)
        current_state = State.VULNERABLE
        modulate = Color(1, 0.5, 0.5, 1)  # Turn red = hittable
        await get_tree().create_timer(2.5).timeout
        modulate = Color(1, 1, 1, 1)

func _do_attack() -> void:
    # Simple attack: charge toward the player
    var player = get_tree().get_first_node_in_group("player")
    if player:
        var dir = (player.global_position - global_position).normalized()
        velocity = dir * 300.0
        move_and_slide()
```

## Step 4: Taking Damage

The `WeakSpot` Area2D only registers hits during the VULNERABLE state. When health reaches zero, emit `defeated` and remove the boss.

## Step 5: Health Bar UI

Add a **ProgressBar** to your CanvasLayer. Connect it to the boss's `health_changed` signal to update `max_value` and `value`. Add the Boss node to a group called `"boss"` so the health bar can find it.

## Making It Harder Each Phase

Scale the boss's attack speed based on missing health: `var rage_speed = 200.0 + (max_health - health) * 30.0`. As health drops, the boss charges faster. Simple, effective, and your kid will notice.

## Keeping Kids Engaged

- This is THEIR villain. Let them name it. Give it a backstory. "Why is it evil?"
- Three phases = three drawings. "What does it look like when it's angry? When it's tired?"
- Let them playtest the boss fight. If it's too hard, make the vulnerable window longer.
- When they beat it: celebrate. This is the climax of their game.

## What You Built Together

A boss fight with three phases, a health bar, and a state machine that makes the boss feel alive. Your kid designed the villain, decided how it fights, and now they get to defeat it. That's a complete game arc.

---

[← Previous: Power-Ups](chapter-06-powerups.md) | [Next: Chapter 8 - Ship It →](chapter-08-ship.md)
