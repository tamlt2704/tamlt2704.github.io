# Chapter 5: Pixel Art Rules — Clean Lines and When to Break Them

[← Chapter 4: Tilesets](chapter-04-tilesets.md) | [Chapter 6: Idle Animation →](chapter-06-idle.md)

---

## The Problem

You zoom into Ember's outline. Some curves look smooth, others look like staircases. The diagonal on the flame has inconsistent steps. You used the line tool for some edges and hand-drew others.

Riku zooms to 1600%:

> "Pixel art has rules — not suggestions. At this resolution, every pixel is visible. A misplaced pixel isn't hidden by anti-aliasing. It screams."

---

## Rule 1: No Anti-Aliasing

Anti-aliasing adds semi-transparent pixels to smooth edges. In pixel art, this creates blur:

```
WRONG (anti-aliased):           RIGHT (clean):
  . . ░ █ █ ░ . .              . . . █ █ . . .
  . ░ █ █ █ █ ░ .              . . █ █ █ █ . .
  ░ █ █ █ █ █ █ ░              . █ █ █ █ █ █ .

  ░ = semi-transparent          No in-between values.
  Looks blurry at 1x.           Crisp at any zoom.
```

In Aseprite: Anti-aliasing OFF on all tools. Use Pencil, never Brush.

---

## Rule 2: Avoiding Jaggies (Staircase Lines)

Jaggies are diagonals with inconsistent step lengths:

```
JAGGY (bad):                    SMOOTH (good):
  X . . . . .                   X . . . . .
  . X . . . .                   . X . . . .
  . . X . . .                   . . X X . .
  . . . X . .                   . . . . X X
  . . . . X .                   . . . . . .
  . . . . . X

  Steps: 1,1,1,1,1             Steps: 1,2,2
  Staircase.                    Smooth curve.
```

Rule: step lengths should change **gradually**. Good: `1, 2, 2, 1`. Bad: `1, 3, 1, 2`.

---

## Rule 3: No Doubles

Two pixels on a diagonal that create a bump:

```
DOUBLES (bad):                  FIXED:
  . . X . . .                   . . X . . .
  . . X X . .  ← double!       . . . X . .
  . . . X . .                   . . . . X .
  . . . X X .  ← double!       . . . . . X
  . . . . X .
```

Doubles break line flow. The most common pixel art mistake.

---

## Rule 4: No Orphan Pixels

Isolated single pixels look like noise. Pixels should connect to neighbors:

```
ORPHANS (bad):                  CLUSTERED (good):
  . . X . . X .                 . . X X . . .
  . X . . X . .                 . X X . . . .
  X . . X . . X                 X X . . X X .

  Scattered = noise.            Groups = intentional.
```

Exception: sparkles, stars, and intentional texture dots.

---

## Rule 5: Clean Curves

Curves need symmetric step patterns:

```
Circle (12px diameter):
        X X X X
      X X . . X X
    X X . . . . X X
    X . . . . . . X
    X X . . . . X X
      X X . . X X
        X X X X

Pattern: 4, 2, 1, 1, 2, 4 (symmetric around midpoint!)
```

---

## Applying Rules to Ember

```
BEFORE (violations):             AFTER (clean):
      . X X . .                    . . X X . .
    . X X . X X .  ← double     . X X . . X X .
    X . . . . . X                X . . . . . . X
    X . . . . X .  ← orphan     X . . . . . . X
    . X . . X . .                . X . . . . X .
    X . . . X . .  ← jaggy      . X . . . X . .
    X . .  . X .                 X . .    . . X
```

---

## When to Break the Rules

> "Know the rules so you can break them **on purpose**. Accidental = mistake. Intentional = style."

| Rule | When to Break |
|---|---|
| No AA | Dithering patterns for texture |
| Consistent width | Thicker outlines for emphasis |
| No jaggies | Organic textures (bark, rough stone) |
| No orphans | Sparkles, snow, particle effects |
| Clean curves | Damaged/rough surfaces |

---

## Dithering: Controlled Rule-Breaking

```
Solid shading:              Dithered:
████████░░░░░░░░            ████████░█░█░░░░
████████░░░░░░░░            █░██████░░█░░█░░

Hard edge.                  Gradual transition.
                            Creates a "third color."
```

Use sparingly — adds texture but can look noisy.

---

## Quick Reference

| Rule | Description | Common Violation |
|---|---|---|
| No AA | All pixels fully opaque or transparent | Using brush instead of pencil |
| No jaggies | Gradual step changes on diagonals | Random steps (1,3,1,2) |
| No doubles | No 2px bumps on diagonals | Not checking diagonal lines |
| Clusters | Pixels connect to neighbors | Scattered singles |
| Clean curves | Symmetric step patterns | Asymmetric arcs |
| Intentional | Only break rules on purpose | Accidental sloppiness |

---

## Exercise: Clean Up Ember's Lines

1. Zoom to 1600% and audit every outline pixel
2. Remove doubles on diagonal lines
3. Ensure curves have symmetric step patterns
4. Remove orphan pixels (unless intentional flame sparks)
5. Check outline width is consistent (1px everywhere)
6. Compare before/after at 100% — clean version looks "sharper"
7. Save as `ember-clean.aseprite`

**Bonus**: Draw a 32×32 circle with no jaggies or doubles.

---

## What's Next

Ember is drawn, shaded, shaped, and clean. A beautiful single frame. But it's frozen. In Chapter 6, we bring Ember to life with the simplest animation: breathing. Four frames. Subtle motion. The idle.

---

[← Chapter 4: Tilesets](chapter-04-tilesets.md) | [Chapter 6: Idle Animation →](chapter-06-idle.md)
