# Chapter 13: VFX Sprites — Dust, Fire, and Sparkles

[← Chapter 12: Transitions](chapter-12-transitions.md) | [Chapter 14: Enemies →](chapter-14-enemies.md)

---

## The Problem

Ember runs, jumps, attacks. The animations are smooth. But something's missing. It feels too clean — like a character in a vacuum. Real movement creates disturbance.

Riku adds a single dust puff to the landing. Suddenly the jump feels twice as impactful.

> "VFX are seasoning. The character animation is the meal. But with the right effects, everything feels 10x more alive. Dust says 'this ground is real.' Fire trails say 'this is made of flame.'"

---

## The Principle: One-Shot vs. Looping

```
ONE-SHOT (play once, disappear):     LOOPING (repeat until stopped):
- Dust puff (landing)                - Fire trail (while running)
- Slash arc (attack)                 - Torch flame (environment)
- Explosion (enemy death)            - Floating particles (ambient)
- Sparkle burst (item pickup)        - Water ripple

Trigger → Play → Destroy            Start → Loop → Stop → Destroy
```

---

## Core VFX Set

### VFX 1: Dust Puff (16×16, 4 frames, one-shot)

```
Frame 1 (spawn):    Frame 2 (expand):   Frame 3 (spread):   Frame 4 (fade):
     ··                 ····               · ·· ·              ·    ·
    ····               ······             ··    ··
     ··                 ····               · ·· ·                 ·

  Small, dense.      Expanding.         Thinning.           Fading.
  60ms               80ms               80ms                60ms
```

Colors: 2-3 gray/brown values. Spawn at Ember's feet on landing.

### VFX 2: Fire Trail (8×8, 3 frames, loop ×1)

```
Frame 1:          Frame 2:          Frame 3:
    ██                ██               ·
   ████              ██··             ··
    ██               ····              ·

  Bright.          Flickering.      Fading.
  50ms             50ms             50ms
```

Spawn one particle every 3-4 frames at feet while running. Each plays once, disappears.

### VFX 3: Slash Arc (32×32, 3 frames, one-shot)

```
Frame 1 (appear):    Frame 2 (full):      Frame 3 (fade):
      ╭──╮              ╭────────╮            ╭ ─ ─ ╮
    ╱      ╲          ╱            ╲
   │        │        │   FULL ARC   │        fading...
    ╲      ╱          ╲            ╱
      ╰──╯              ╰────────╯            ╰ ─ ─ ╯

  40ms               40ms                 60ms
```

Colors: white core + light blue edge. Overlaid during attack frames 3-5.

### VFX 4: Sparkle Burst (24×24, 4 frames, one-shot)

Particles radiate outward from center. 40ms, 60ms, 80ms, 80ms.

### VFX 5: Explosion (32×32, 5 frames, one-shot)

Flash → expand → maximum → break apart → dissipate. Colors: white center → yellow → orange → red outward.

---

## The Mistake You'll Make

You add VFX to everything. Dust on every step. Fire trail constantly. Sparkles on idle. The screen is a mess.

Riku turns off half your effects:

> "VFX should **punctuate**, not narrate. Dust on LANDING is punctuation — marks a moment. Dust on every STEP is narration — constant noise. Effects appear at **state changes**, not during sustained states."

### The Fix: Trigger Points

```
WRONG (constant):               RIGHT (punctuation):
Running: dust every frame       Running: fire trail only
Landing: dust+sparkle+shake     Landing: dust puff (one burst)
Walking: dust every step        Walking: nothing

Effects mark MOMENTS:
- Landing (air → ground)
- Attack impact (swing → hit)
- Direction change (left → right)
- Speed change (walk → run)
```

---

## VFX Layering (Z-Order)

```
Layer 4: Foreground effects (dust in front of character)
Layer 3: Character (Ember)
Layer 2: Behind effects (fire trail behind character)
Layer 1: Background
```

---

## Sprite Sheet Organization

Keep VFX separate from character sprites:

```
VFX sprite sheet:
┌──┬──┬──┬──┐  Row 1: Dust puff (4 × 16×16)
├─┬─┬─┤        Row 2: Fire trail (3 × 8×8)
├────┬────┬────┤ Row 3: Slash arc (3 × 32×32)
├───┬───┬───┬───┤ Row 4: Sparkle (4 × 24×24)
├────┬────┬────┬────┬────┤ Row 5: Explosion (5 × 32×32)
```

---

## Quick Reference

| Effect | Type | Frames | Size | Trigger |
|---|---|---|---|---|
| Dust puff | One-shot | 4 | 16×16 | Landing, direction change |
| Fire trail | Loop ×1 | 3 | 8×8 | Every 3-4 frames while running |
| Slash arc | One-shot | 3 | 32×32 | Attack frames 3-5 |
| Sparkle | One-shot | 4 | 24×24 | Item pickup |
| Explosion | One-shot | 5 | 32×32 | Enemy death |

| Concept | Rule |
|---|---|
| Punctuation | Effects at state changes, not constant |
| Layering | Some behind character, some in front |
| Colors | Match game palette |
| Timing | Fast spawn, slower fade |
| Separate sheet | VFX on own sprite sheet |

---

## Exercise: Create Ember's VFX Set

1. Dust puff (4 frames, 16×16): small → expand → spread → fade
2. Fire trail (3 frames, 8×8): bright → flicker → fade (Ember's colors)
3. Slash arc (3 frames, 32×32): appear → full → fade (white/blue)
4. Save as `ember-vfx.aseprite` (one file, multiple tags)

**Test**: Overlay on character animations. Does it enhance without overwhelming?

**Success criteria**: Effects feel like they belong. Colors match palette. They enhance, not compete.

---

[← Chapter 12: Transitions](chapter-12-transitions.md) | [Chapter 14: Enemies →](chapter-14-enemies.md)
