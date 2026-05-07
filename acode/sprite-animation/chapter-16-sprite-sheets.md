# Chapter 16: Sprite Sheets — From Aseprite to Game-Ready Assets

[← Chapter 15: Environment](chapter-15-environment.md) | [Chapter 17: Renderer →](chapter-17-renderer.md)

---

## The Problem

You have 15+ Aseprite files. Ember alone has 54 frames across 8 files. You can't load 54 individual PNGs at runtime — that's 54 HTTP requests and texture binds.

Riku opens Aseprite's export dialog:

> "Everything goes into one image — a **sprite sheet**. All frames in a grid. One file to load, one texture to bind. A JSON file tells the engine where each frame lives."

---

## The Principle: Atlas Packing

```
Sprite sheet layout (Ember):

┌────┬────┬────┬────┬────┬────┬────┬────┐
│ I1 │ I2 │ I3 │ I4 │ I5 │ I6 │    │    │  Row 0: Idle (6)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ W1 │ W2 │ W3 │ W4 │ W5 │ W6 │ W7 │ W8 │  Row 1: Walk (8)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ R1 │ R2 │ R3 │ R4 │ R5 │ R6 │    │    │  Row 2: Run (6)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ J1 │ J2 │ J3 │ J4 │ J5 │ J6 │ J7 │    │  Row 3: Jump (7)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ A1 │ A2 │ A3 │ A4 │ A5 │ A6 │ A7 │    │  Row 4: Attack (7)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ H1 │ H2 │ H3 │ H4 │ H5 │    │    │    │  Row 5: Hit (5)
├────┼────┼────┼────┼────┼────┼────┼────┤
│ D1 │ D2 │ D3 │ D4 │ D5 │ D6 │    │    │  Row 6: Death (6)
└────┴────┴────┴────┴────┴────┴────┴────┘

Each cell = 32×32. Sheet = 256×224 pixels.
```

---

## Step-by-Step: Exporting

### Step 1: Organize with Tags

In Aseprite, select frame ranges and create tags:
- Frames 1-6 → Tag: "idle"
- Frames 7-14 → Tag: "walk"
- etc.

Tags tell the exporter where each animation starts/ends.

### Step 2: Export Sprite Sheet

File → Export Sprite Sheet:
- Sheet Type: By Rows
- Columns: 8
- Border Padding: 0
- Spacing: 1 (prevents texture bleeding)
- Output File: `ember-sheet.png`
- JSON Data: `ember-sheet.json`

### Step 3: The JSON Metadata

```json
{
  "frames": [
    { "filename": "idle 0", "frame": {"x":0,"y":0,"w":32,"h":32}, "duration": 200 },
    { "filename": "idle 1", "frame": {"x":33,"y":0,"w":32,"h":32}, "duration": 150 }
  ],
  "meta": {
    "frameTags": [
      { "name": "idle", "from": 0, "to": 5, "direction": "forward" },
      { "name": "walk", "from": 6, "to": 13, "direction": "forward" },
      { "name": "run", "from": 14, "to": 19, "direction": "forward" }
    ],
    "size": { "w": 256, "h": 224 }
  }
}
```

### Step 4: Verify

Open the PNG. Check: no frames cut off, no overlap, transparent background, reasonable file size (5-15KB for 256×224).

---

## The Mistake You'll Make

Some frames show a 1-pixel bleed from adjacent frames — a sliver of the next frame's edge.

Riku checks your settings:

> "Texture bleeding happens when the GPU samples at frame edges and grabs the neighbor. Fix: add 1px spacing between frames in the export."

```
WITHOUT spacing:              WITH 1px spacing:
┌────┬────┬────┐              ┌────┐ ┌────┐ ┌────┐
│ F1 │ F2 │ F3 │              │ F1 │ │ F2 │ │ F3 │
└────┴────┴────┘              └────┘ └────┘ └────┘
Frames touch. Bleed risk.     1px gap. Safe.
```

---

## Packing Strategies

| Strategy | Pros | Cons |
|---|---|---|
| Fixed grid | Simple math, easy to debug | Wastes space on empty cells |
| Trimmed | Smaller file, tight packing | Needs offset data in JSON |
| Per-character sheets | Clean organization | Multiple files to load |

For Ember Quest: fixed grid (simple) with one sheet per character.

---

## File Size Optimization

| Technique | Savings |
|---|---|
| Indexed color (8-bit palette) | 50-70% |
| PNG optimization (optipng) | 10-20% |
| Power-of-2 dimensions | GPU performance |

Ember's sheet: ~15KB unoptimized → ~4KB after indexed + pngquant. Pixel art is tiny.

---

## Quick Reference

| Concept | Rule |
|---|---|
| One sheet per character | All animations in one PNG |
| JSON metadata | Frame positions, sizes, durations |
| Tags | Label animations before export |
| Layout | By Rows (one animation per row) |
| Spacing | 1px between frames (prevents bleeding) |
| Color mode | Indexed (8-bit) for smallest size |
| Power of 2 | Pad to 256×256 or 512×512 |
| Naming | `character-sheet.png` + `character-sheet.json` |

---

## Export Checklist

| Check | ☐ |
|---|---|
| All animations present (idle, walk, run, jump, attack, hit, death) | |
| JSON frameTags correct (from/to indices) | |
| Frame durations match intended timing | |
| No frames cut off or overlapping | |
| Transparent background | |
| 1px spacing enabled | |
| File size < 20KB | |

---

## Exercise: Export Ember's Complete Sheet

1. Combine all Ember animations into one Aseprite file with tags
2. Export: By Rows, 8 columns, 1px spacing
3. Output: `ember-sheet.png` + `ember-sheet.json`
4. Verify JSON frameTags match your animations
5. Open PNG at 100% — confirm all frames present
6. Export VFX separately: `vfx-sheet.png` + `vfx-sheet.json`

**Success criteria**: Two files (PNG + JSON) contain everything needed to render Ember in a game engine.

---

[← Chapter 15: Environment](chapter-15-environment.md) | [Chapter 17: Renderer →](chapter-17-renderer.md)
