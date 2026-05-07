# Chapter 2: Color & Shading — Making Flat Pixels Feel Alive

[← Chapter 1: First Character](chapter-01-first-character.md) | [Chapter 3: Shape Language →](chapter-03-shape-language.md)

---

## The Problem

Ember exists. A silhouette with a base orange fill. But it looks like a traffic cone. Flat. Lifeless. You try adding darker orange for shadows and lighter orange for highlights. Now it looks like a traffic cone with gradients.

Riku shakes his head:

> "You're shading with brightness only — darker = shadow, lighter = highlight. That's how 3D renderers think. Pixel artists think in **hue shifts**. Your shadows aren't just darker orange — they're pushed toward red or purple. Your highlights aren't just lighter orange — they're pushed toward yellow."

He pulls up a color ramp:

> "Four colors. That's all Ember needs. But the right four colors."

---

## The Principle: Hue Shifting

Traditional shading takes one color and adjusts brightness:

```
BAD: Brightness-only shading
┌─────────────────────────────────────────────┐
│  Dark Orange → Orange → Light Orange        │
│  #8B4513      #FF6B35   #FFB380             │
│                                             │
│  Same hue (orange), different brightness.   │
│  Looks flat and digital.                    │
└─────────────────────────────────────────────┘
```

Hue-shifted shading rotates the hue as you go lighter/darker:

```
GOOD: Hue-shifted shading
┌─────────────────────────────────────────────┐
│  Dark Red  →  Orange  →  Yellow             │
│  #8B2252     #FF6B35    #FFD93D             │
│                                             │
│  Shadow shifts toward red/purple.           │
│  Highlight shifts toward yellow.            │
│  Looks warm, organic, alive.               │
└─────────────────────────────────────────────┘
```

This mimics how real light works: warm highlights (sunlight is yellow), cool shadows (ambient light is blue/purple).

---

## Ember's Palette: 6 Colors

Riku builds Ember's palette:

| Swatch | Hex | Role | Hue Shift |
|---|---|---|---|
| 1 | `#1A0A2E` | Darkest outline | Deep purple (cool shadow) |
| 2 | `#8B2252` | Dark shadow | Red-purple |
| 3 | `#CC4422` | Mid shadow | Red-orange |
| 4 | `#FF6B35` | Base / midtone | Orange (core color) |
| 5 | `#FFAA22` | Highlight | Orange-yellow |
| 6 | `#FFD93D` | Brightest spot | Yellow (warm highlight) |

```
The palette ramp (dark → light):

  ██  ██  ██  ██  ██  ██
  1   2   3   4   5   6
  ↑               ↑
  Cool            Warm
  (purple)        (yellow)
```

> "Six colors for the entire character. Constraints force you to be intentional about where every shade goes."

---

## Step-by-Step: Shading Ember

### Step 1: Establish Light Direction

Pick a light source. For platformers, top-left is standard:

```
   ☀️ Light source (top-left)
    ↘
    ┌──────────┐
    │ HL  mid  │  HL = highlight (colors 5-6)
    │ mid  SH  │  mid = base (color 4)
    │ mid  SH  │  SH = shadow (colors 2-3)
    └──────────┘
```

### Step 2: Apply Base Color

Fill Ember entirely with color 4 (#FF6B35). This is your starting point.

### Step 3: Add Shadows (Bottom-Right)

Using color 3 (#CC4422), shade areas facing away from light: right side of head, bottom of torso, inner legs, underside of flame.

### Step 4: Add Highlights (Top-Left)

Using color 5 (#FFAA22), highlight where light hits: top-left of head, top of flame, left shoulder.

### Step 5: Brightest Spot

Using color 6 (#FFD93D), place 1-2 pixels at flame tip and top-left of head. Use sparingly.

### Step 6: Deepest Shadows

Using color 2 (#8B2252), add 1-2 pixels in deepest crevices: neck area, between legs, under flame overlap.

---

## The Mistake You'll Make

You shade Ember. It looks... muddy. The shadows and highlights blend together. You can't tell where the light is coming from.

Riku points at your work:

> "You're using too many in-between values. Pixel art needs **contrast**. Look at your shadow edge — you've got color 4, then 3, then 2 in a gradient. That's three pixels of transition on a 6-pixel-wide body. There's no room for gradients at this scale."

### The Fix: Hard Edges, Not Gradients

At 32×32, shading should be **chunky**, not smooth:

```
BAD: Gradient shading          GOOD: Chunky shading

  5 5 4 4 3 3 2 2             5 5 5 4 4 3 3 2
  5 4 4 4 3 3 2 2             5 5 4 4 4 3 2 2
  5 4 4 3 3 2 2 2             5 5 4 4 3 3 2 2
  4 4 3 3 3 2 2 2             5 4 4 4 3 2 2 2

  Every row transitions        Clear zones of light
  gradually. Looks muddy.      and shadow. Reads well.
```

Rule: Each shade should occupy a **cluster** of pixels, not a single-pixel strip.

---

## Material Indication Through Color

Different materials use different shading:

| Material | Style | Why |
|---|---|---|
| Flame hair | High contrast, yellow tips | Fire glows |
| Body | Medium contrast, smooth zones | Soft light falloff |
| Eyes | Flat white + dark pupil | Eyes catch light |
| Feet | Low contrast, darker | Less light reaches them |

---

## Palette Constraints

| Palette Size | Best For |
|---|---|
| 2-3 colors | Tiny sprites (8×8, 16×16) |
| **4-6 colors** | **32×32 characters (Ember)** |
| 8-12 colors | 48×48+ characters |
| 16+ colors | Large illustrations |

> "More colors doesn't mean better art. At 32×32, you don't have the pixel real estate to justify 16 shades."

---

## Quick Reference

| Concept | Rule |
|---|---|
| Hue shifting | Shadows → cool (red/purple), Highlights → warm (yellow) |
| Palette size | 4-6 colors for a 32×32 character |
| Light direction | Pick one (top-left standard), stay consistent |
| Shadow placement | Opposite side from light source |
| Shading style | Chunky clusters, not gradients |
| Brightest pixel | Use sparingly (1-2 pixels max) |
| Material variation | Different contrast levels for different materials |
| Outline color | Darkest palette color, not pure black |

---

## Exercise: Shade Ember

1. Open your `ember-idle-frame1.aseprite` from Chapter 1
2. Create Ember's 6-color palette (use the hex values above or create your own hue-shifted ramp)
3. Replace the flat orange fill with proper shading:
   - Light source: top-left
   - Shadows: bottom-right areas (colors 2-3)
   - Highlights: top-left areas (colors 5-6)
4. Apply material variation: flame hair gets more contrast than the body
5. Zoom to 100% — does the shading help readability or hurt it?
6. Save as `ember-shaded.aseprite`

**Success criteria**: At 100% zoom, Ember should look three-dimensional. You should be able to tell where the light is coming from. The flame should look like it glows.

---

## What's Next

Ember has form and depth now. But it still looks generic — it could be any fire character. In Chapter 3, Riku teaches shape language: how to give Ember a personality through the shapes you choose. Round vs. angular. Heavy vs. light. Friendly vs. dangerous.

---

[← Chapter 1: First Character](chapter-01-first-character.md) | [Chapter 3: Shape Language →](chapter-03-shape-language.md)
