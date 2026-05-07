# Chapter 1: Drawing Your First Character — 32×32 Pixels of Possibility

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Color & Shading →](chapter-02-color-shading.md)

---

## The Problem

You open Photoshop. New canvas: 1920×1080. You grab a brush and draw... something. It's vaguely humanoid. You scale it down to 32×32 for the game. It becomes an unrecognizable smear of anti-aliased mush.

Riku looks over your shoulder:

> "You're painting a mural and trying to shrink it into a postage stamp. Pixel art doesn't work that way. You start small. Every pixel is a deliberate choice — not a byproduct of scaling."

He closes Photoshop. Opens Aseprite. New canvas: 32×32 pixels. Zoom: 800%.

> "This is your entire world. 1,024 pixels total. Let's make a fire spirit out of them."

---

## The Principle: Silhouette First

Riku draws a filled black shape on the canvas:

> "Before color, before detail — can you read the character from its silhouette alone? If the answer is no, no amount of shading will save it. This is the **squint test**: squint at your screen. If the shape is clear, the design works."

```
The Squint Test:
┌─────────────────────────────────────────────┐
│  GOOD silhouette        BAD silhouette      │
│                                             │
│      ██                    ████             │
│     ████                   ████             │
│    ██████                  ████             │
│     ████                   ████             │
│    ██  ██                  ████             │
│                                             │
│  Clear head, body,       Rectangle.         │
│  legs. Readable.         Could be anything. │
└─────────────────────────────────────────────┘
```

The key insight: at 32×32, you have roughly 5-6 pixels for the head, 10-12 for the torso, and 10-12 for the legs. Every pixel matters.

---

## Step-by-Step: Drawing Ember

### Step 1: Set Up the Canvas

Open Aseprite (or Libresprite/Piskel):
- New file → Width: 32, Height: 32
- Background: Transparent
- Color mode: RGBA

Set your zoom to 600-800% so you can see individual pixels.

### Step 2: Block the Silhouette

Using only black (#000000), draw Ember's silhouette:

```
Canvas (32×32) — Ember's silhouette:

Row 08:          ████
Row 09:         ██████          ← Flame "hair" tip
Row 10:        ████████
Row 11:       ██████████        ← Flame hair widens
Row 12:        ████████
Row 13:         ██████          ← Head (round)
Row 14:        ████████
Row 15:        ████████         ← Head bottom
Row 16:         ██████
Row 17:        ████████         ← Torso top
Row 18:       ██████████
Row 19:       ██████████        ← Torso widest
Row 20:        ████████
Row 21:        ████████         ← Hips
Row 22:        ██  ████
Row 23:       ███   ███         ← Legs apart
Row 24:       ███   ███
Row 25:       ████  ████        ← Feet
```

### Step 3: The Squint Test

Zoom out to 100% (actual game size). Can you tell it's a character? You should see:
- A distinct head with flame-like protrusion on top
- A body with clear torso
- Two legs, grounded

If it reads as a blob, your proportions are off. Common fix: make the head larger relative to body (big-head style reads better at small sizes).

### Step 4: Refine the Outline

Switch from filled silhouette to a 1-pixel outline:

```
Outline only (zoomed in, each char = 1 pixel):

        . X X .
      . X . . X .
    . X . . . . X .        ← Flame tip
      X . . . . X
      X . . . . X          ← Head
      . X . . X .
      X . . . . X          ← Torso
      X . . . . X
      X . . . . X
      . X . . X .          ← Waist
      X .    . X
      X .    . X            ← Legs
      X X    X X            ← Feet

X = outline pixel, . = will be filled with color later
```

### Step 5: Fill with Base Color

Pick a single orange (#FF6B35) and fill the interior. Don't worry about shading yet — that's Chapter 2.

---

## The Mistake You'll Make

You draw Ember. At 800% zoom it looks okay. At actual game size, the flame hair blends into the head. The legs look like a single column.

> "You're designing for the zoomed-in view. Players see the zoomed-out version. Always check at 1x. If details disappear at 1x, they don't exist."

### The Fix

- **Exaggerate proportions**: Flame hair 3-4px above head, not 1-2
- **Increase contrast**: 1-pixel gap between head and flame
- **Widen stance**: Legs 2-3 pixels apart, not 1

```
Before fix:              After fix:

     ██                      ██
    ████                    ████
    ████  ← hair blends    ██████
    ████     into head       ████   ← clear gap
    ████                    ██████  ← distinct head
     ██                      ████
    ████                    ██████
    ████                    ██████
    ████                     ████
    ████  ← legs merge      ██  ██  ← clear separation
    ████                   ███  ███
```

---

## Why 32×32?

| Canvas Size | Use Case |
|---|---|
| 8×8 | Tiny icons (64 pixels — extreme constraint) |
| 16×16 | Classic NES-style (256 pixels) |
| **32×32** | **Modern indie standard (1,024 pixels)** |
| 48×48 | Detailed characters (2,304 pixels) |
| 64×64 | Large/boss characters (4,096 pixels) |

> "32×32 is the sweet spot. Big enough to show personality, small enough that every pixel is intentional."

Your canvas is 32×32, but Ember doesn't fill it all — leave 4-6px padding for flame effects extending upward, attack animations sideways, and jump squash downward.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Canvas size | 32×32 for Ember (standard indie size) |
| Workflow | Silhouette → Outline → Base color |
| Squint test | If unreadable at 1x zoom, redesign |
| Proportions | Exaggerate for readability (big head, wide stance) |
| Padding | Leave 4-6px margin for animation overflow |
| Tools | Pencil tool (1px), no anti-aliasing, no blur |
| Zoom | Work at 600-800%, check at 100% constantly |

---

## Exercise: Draw Ember's Idle Pose

1. Create a 32×32 canvas in Aseprite (or Piskel if free)
2. Using only black, draw Ember's silhouette following the proportions above
3. Apply the squint test — zoom to 100% and check readability
4. Refine: exaggerate the flame hair, widen the stance
5. Add a 1-pixel outline in dark brown (#3D1C00)
6. Fill with base orange (#FF6B35)
7. Save as `ember-idle-frame1.aseprite`

**Success criteria**: At 100% zoom, you can clearly identify a character with a flame on its head, a body, and two legs. It should NOT look like a rectangle or a blob.

---

## What's Next

Ember exists — but it's flat. A single color with an outline. It looks like a Flash game from 2004. In Chapter 2, Riku introduces color theory for pixel art: limited palettes, hue shifting, and how to make 4 colors feel like 40.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Color & Shading →](chapter-02-color-shading.md)
