# Chapter 4: Tilesets — Building Ember's World

[← Chapter 3: Shape Language](chapter-03-shape-language.md) | [Chapter 5: Pixel Art Rules →](chapter-05-pixel-art-rules.md)

---

## The Problem

Ember looks great. You place it on a white background. It floats in the void. You try drawing a ground beneath it — a brown rectangle. Now Ember is standing on a chocolate bar. You draw some rocks. They look like potatoes.

Riku opens a new file:

> "Characters get all the love, but the environment is 90% of what players see. And environments are built from **tiles** — small, repeating pieces that snap together like puzzle pieces. You don't draw a whole level. You draw a handful of tiles and the level builds itself."

He creates a 16×16 canvas:

> "Tiles are usually half the character size. Ember is 32×32, so tiles are 16×16. This means Ember is exactly 2 tiles tall. That ratio matters for readability."

---

## The Principle: Modular Repetition

A tileset is a collection of small images that combine to form larger environments:

```
Individual tiles (16×16 each):
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│    │ │████│ │▓▓▓▓│ │ ╱╲ │ │ ~~ │
│    │ │████│ │▓▓▓▓│ │╱  ╲│ │~~~~│
│ SKY│ │WALL│ │GRND│ │SLOP│ │WATR│
└────┘ └────┘ └────┘ └────┘ └────┘

Combined into a level:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│    │    │    │    │    │    │    │    │
│    │    │    │    │    │    │    │    │
├────┼────┼────┼────┼────┼────┼────┼────┤
│    │    │████│    │    │████│    │    │
│    │    │████│    │    │████│    │    │
├────┼────┼────┼────┼────┼────┼────┼────┤
│▓▓▓▓│▓▓▓▓│████│▓▓▓▓│▓▓▓▓│████│▓▓▓▓│▓▓▓▓│
│▓▓▓▓│▓▓▓▓│████│▓▓▓▓│▓▓▓▓│████│▓▓▓▓│▓▓▓▓│
└────┴────┴────┴────┴────┴────┴────┴────┘
```

The key insight: players never notice individual tiles. They see "a cave" or "a forest." Good tiles are invisible.

---

## Step-by-Step: Drawing the Ground Tile

### Step 1: The Basic Ground (16×16)

Start with the most important tile — the ground Ember walks on:

```
Ground tile (16×16):

████████████████    ← Surface line (darkest)
▓░▓▓░▓▓▓░▓▓▓░▓▓    ← Top soil (medium + texture)
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ← Soil body (medium)
▓▓░▓▓▓▓░▓▓▓▓▓░▓▓    ← Soil with pebbles
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ← Deep soil (slightly darker)
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
████████████████    ← Bottom (darkest, optional)

Colors: ████ = #2D1B00, ▓ = #5C3A1E, ░ = #7A5230
```

### Step 2: Make It Seamless

The tile must repeat without visible seams. The trick: whatever exits the right edge must enter from the left edge.

```
Seamless test — place 3 tiles side by side:

████████████████│████████████████│████████████████
▓░▓▓░▓▓▓░▓▓▓░▓▓│▓░▓▓░▓▓▓░▓▓▓░▓▓│▓░▓▓░▓▓▓░▓▓▓░▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                 ↑                ↑
          These edges must match perfectly
```

**Technique**: Draw your tile, then in Aseprite use Edit → Tile Mode to preview the repetition in real-time.

### Step 3: Add Variation Tiles

One tile repeated 100 times looks artificial. Create 2-3 variants with different details (pebble, crack, etc.) and mix randomly: AABABCAABA...

### Step 4: Edge Tiles

Ground doesn't just repeat — it has edges where it meets the sky:

```
Tile types needed for a complete ground set:

┌─────┬─────┬─────┐
│ TL  │ TOP │ TR  │   TL = top-left corner
├─────┼─────┼─────┤   TOP = top edge (grass surface)
│ LFT │ MID │ RGT │   MID = interior (fully surrounded)
├─────┼─────┼─────┤   BOT = bottom edge
│ BL  │ BOT │ BR  │
└─────┴─────┴─────┘

Minimum set: 9 tiles for a complete terrain block
```

### Step 5: Platform Tiles

Floating platforms need their own set — they have edges on all sides:

```
Platform (3 tiles wide minimum):

┌──────┬──────────────┬──────┐
│ LEFT │   MIDDLE     │RIGHT │
│ edge │  (repeats)   │ edge │
└──────┴──────────────┴──────┘
```

---

## The Mistake You'll Make

You draw beautiful individual tiles. You place them in a grid. The level looks like a bathroom floor — perfectly regular, obviously tiled. Every 16 pixels, the pattern repeats identically.

Riku zooms out on your level:

> "I can count the tiles. That means the player can too. The goal is to make tiles **disappear** into the environment. Three tricks: variation tiles, scattered props, and breaking the grid with decorations."

### The Fix: Breaking the Grid

```
BEFORE (obvious tiling):

████████████████████████████████████████████████
▓░▓▓░▓▓▓░▓▓▓░▓▓▓░▓▓░▓▓▓░▓▓▓░▓▓▓░▓▓░▓▓▓░▓▓▓░▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ↑ Repeating pattern is obvious

AFTER (broken grid):

████████████████████████████████████████████████
▓░▓▓░▓▓▓░▓▓▓░▓▓▓▓▓▓▓██▓▓▓░▓▓▓░▓▓▓░▓▓░▓▓▓╲▓▓▓░▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╲▓▓▓▓▓▓
  ↑ Variation tiles + props break the repetition
```

Props that break the grid:
- Small rocks (8×8, placed between tiles)
- Grass tufts on the surface (extend above the tile boundary)
- Cracks that span multiple tiles

---

## The Tile Palette

Ember's world is a frozen cavern. The environment palette contrasts with Ember:

| Swatch | Hex | Role |
|---|---|---|
| 1 | `#0D1B2A` | Deepest shadow |
| 2 | `#1B3A4B` | Dark stone |
| 3 | `#3D5A6E` | Medium stone |
| 4 | `#6B8FA3` | Light stone |
| 5 | `#A4C3D2` | Ice accent |
| 6 | `#E8F4F8` | Brightest ice |

> "Environment palette should **contrast** with character. Ember is warm (oranges). World is cool (blues). Ember pops against any background."

---

## Complete Tileset Checklist

For a basic platformer level, you need:

| Category | Tiles | Count |
|---|---|---|
| Ground | Top, middle, bottom, corners (9) + variants (3) | 12 |
| Platforms | Left cap, middle, right cap | 3 |
| Walls | Vertical left, right, interior | 3 |
| Background | Solid dark, texture variant | 2 |
| Props | Rocks, crystals, torches, signs | 4-6 |
| **Total** | | **24-26 tiles** |

That's an entire level from ~25 tiles. Each is 16×16 pixels.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Tile size | 16×16 (half of character's 32×32) |
| Seamless tiling | Right edge must match left edge; top must match bottom |
| Variation | 2-3 variants per tile type to break repetition |
| Edge tiles | 9-tile set for any terrain block (corners + edges + center) |
| Props | Small decorations that break the grid pattern |
| Color contrast | Environment palette should contrast character palette |
| Aseprite tip | Edit → Tile Mode for real-time seamless preview |
| Grid discipline | All tiles align to 16px grid; props can break it |

---

## Exercise: Draw a Ground Tileset

1. Create a 64×64 canvas (4×4 grid of 16×16 tiles)
2. Draw: ground edges (9-tile set), platform caps, 3 variants, 1 prop
3. Test seamlessness: build a small level, place Ember (should be ~2 tiles tall)
4. Save as `tileset-ground.aseprite`

**Success criteria**: Platform layout doesn't look obviously tiled at 100% zoom.

---

## What's Next

Character and world exist. But Ember's outline has staircase patterns and chunky curves. Chapter 5 covers pixel art rules: clean lines, avoiding jaggies, and when to break them.

---

[← Chapter 3: Shape Language](chapter-03-shape-language.md) | [Chapter 5: Pixel Art Rules →](chapter-05-pixel-art-rules.md)
