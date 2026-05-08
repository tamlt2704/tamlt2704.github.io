# Chapter 4: Building a World with Levels

[← Previous: Enemies](chapter-03-enemies.md) | [Next: Chapter 5 - Audio →](chapter-05-audio.md)

---

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Draws a map on paper (walls, platforms, gaps) | Builds it with TileMap |
| Draws a door or portal | Creates the scene transition system |
| Designs 2–3 levels on paper | Implements each level as a scene |

## Step 1: Kid Draws the Map

Give your kid graph paper (or plain paper with a grid drawn on it). Each square = one tile. They draw:
- Solid squares = walls/ground
- Empty squares = air/walkable space
- A star = where the player starts
- A door = where the level ends

This is level design. Your kid is doing it with crayons.

## Step 2: Create a TileSet

1. In your World scene, add a **TileMapLayer** node
2. In the Inspector, create a new **TileSet**
3. Click the TileSet → add a new Atlas source
4. Use a simple tileset image (your kid can draw tiles too — grass, brick, stone)
5. Set tile size (16×16 or 32×32 works well)

Paint the level following your kid's map. Let them point at the screen: "wall there, gap there, platform up here."

## Step 3: The Door Scene

Kid draws a door (or portal, or magic swirl, or whatever connects levels).

```gdscript
# door.gd — Takes the player to the next level
extends Area2D

# Which scene to load when the player enters
@export_file("*.tscn") var next_level: String

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.name == "Player":
        if next_level and next_level != "":
            get_tree().change_scene_to_file(next_level)
```

## Step 4: Build Multiple Levels

Create separate scenes for each level:
- `res://scenes/levels/level_1.tscn`
- `res://scenes/levels/level_2.tscn`
- `res://scenes/levels/level_3.tscn`

Each level has:
- A TileMapLayer (the walls/platforms)
- A Player instance
- Collectibles scattered around
- An Enemy or two
- A Door with `next_level` pointing to the next scene

## Step 5: Connect the Levels

Set each door's `next_level` export in the Inspector:
- Level 1's door → `res://scenes/levels/level_2.tscn`
- Level 2's door → `res://scenes/levels/level_3.tscn`
- Level 3's door → a win screen or back to level 1

## Level Design Tips (For Your Kid)

Ask them these questions while they draw:
- "Where should the hard part be?"
- "Should there be a secret area?"
- "Where do the coins go — easy ones and hard-to-reach ones?"
- "Where does the monster patrol?"

## Keeping Kids Engaged

- Graph paper is your best friend. Kids love filling in squares.
- Let them name each level. "The Lava Cave," "Sky Kingdom," "Monster Basement."
- Each level can have a different color scheme — ask them to pick.
- If they draw something impossible to build, simplify it but keep the spirit. "We can't do a loop, but we can do a tall tower!"

## What You Built Together

A multi-level game with hand-designed maps, doors that transport the player between worlds, and the feeling of a real adventure with a beginning, middle, and end. Your kid is a level designer now.

---

[← Previous: Enemies](chapter-03-enemies.md) | [Next: Chapter 5 - Audio →](chapter-05-audio.md)
