# Chapter 0: Saturday Morning Game Dev

[Next: Chapter 1 - Movement →](chapter-01-movement.md)

---

## The Philosophy

Here's the deal: your kid is the **creative director**. They draw the characters, design the levels, pick the colors, name the enemies. You're the engineer — you make their ideas come alive on screen.

This isn't a programming course for children. This is a course for developer-parents who want to build something real with their kids on Saturday mornings. The code is yours. The creativity is theirs. The game belongs to both of you.

## Who This Is For

- **Parent**: Comfortable with code. Doesn't need to know GDScript yet — we'll teach you.
- **Kid**: Ages 5–12. Loves drawing, has opinions, wants to see their art move on screen.
- **Time**: ~1 hour per Saturday. Nine Saturdays, one finished game.

## Install Godot 4

1. Go to [godotengine.org](https://godotengine.org/download)
2. Download **Godot 4.x** (standard version, not .NET)
3. Unzip and run — no installer needed
4. Create a new project: `OurGame` (or let your kid name it)

That's it. Godot is a single executable. No dependencies, no build tools.

## The Saturday Plan

| Kid Does | Parent Does |
|----------|-------------|
| Names the project | Creates the Godot project |
| Draws a title screen | Sets up the folder structure |
| Picks a theme (space, jungle, underwater) | Configures project settings |

## Importing Kid Art

This is the magic trick that hooks kids instantly — their drawing appears in the game.

1. Kid draws a character on paper (thick markers work best)
2. Photograph it with your phone against a white background
3. Use any free background remover (remove.bg, or your phone's built-in tool)
4. Save as PNG, drop it into your project's `res://sprites/` folder
5. Drag it onto a Sprite2D node — their character is in the game

**Tips for good art imports:**
- Thick black outlines photograph better
- Bright colors pop on screen
- Keep drawings small-ish (a character, not a whole scene)
- 256×256 to 512×512 pixels is plenty

## Course Roadmap

| Chapter | What You Build |
|---------|---------------|
| 1 | Character moves around |
| 2 | Collectibles and score |
| 3 | An enemy that chases |
| 4 | Multiple levels with doors |
| 5 | Sound effects |
| 6 | A power-up |
| 7 | A boss fight |
| 8 | Polish and ship it |

## Keeping Kids Engaged

- Let them playtest constantly. Every 10 minutes, hand them the keyboard.
- Their ideas are never wrong — just "for a future update" if too complex.
- Name things after their suggestions. `SuperDragonBlast.gd` is a valid filename.
- Celebrate small wins. Character moved? High five. That's a game.

## Project Folder Structure

Keep things organized from the start:

```
res://
├── scenes/
│   ├── levels/
│   └── ui/
├── sprites/
├── audio/
└── scripts/
```

Create these folders now. Your kid can name the `sprites/` folder whatever they want — "art," "drawings," "masterpieces."

## What You Built Together

A Godot 4 project with a name your kid chose, their first drawing imported as a sprite, and a plan for nine Saturdays of building something together.

---

[Next: Chapter 1 - Movement →](chapter-01-movement.md)
