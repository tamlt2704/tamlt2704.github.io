# Chapter 6: Idle Animation — Making Ember Breathe

[← Chapter 5: Pixel Art Rules](chapter-05-pixel-art-rules.md) | [Chapter 7: Walk Cycle →](chapter-07-walk-cycle.md)

---

## The Problem

Ember is a beautiful still image. You put it in the game. It stands there. Motionless. Like a cardboard cutout. You try bobbing the whole sprite up and down 2 pixels. Now it looks like a pogo stick.

Riku watches:

> "An idle animation isn't about big movement. It's about **life**. Living things are never perfectly still — they breathe, shift weight, their hair moves. The goal is so subtle that players don't notice it, but they'd notice if it stopped."

---

## The Principle: Subtle Cyclical Motion

```
4-frame breathe cycle (sine wave):

Frame:    1       2       3       4       (→ 1)
Motion:  REST → INHALE → FULL → EXHALE → REST...

Body:    normal   +1px    +1px    normal
Flame:   normal   +1px    +2px    +1px
Timing:  200ms   150ms   200ms   150ms

Total cycle: 700ms (~1.4 breaths/second)
```

Key: the **flame** moves more than the body. Fire is lighter — it reacts more.

---

## Step-by-Step: 4-Frame Idle

### Frame 1 — Rest (Base Pose)

Your existing Ember drawing. Neutral position.

### Frame 2 — Inhale (Body Rises)

- Body shifts UP 1px (select body, move up)
- Flame stretches UP 1px
- Shoulders rise slightly

```
Frame 2 (INHALE):
       ████████
      ██████████       ← Flame +1px
       ████████
       ████████        ← Head +1px
       ████████
       ██████          ← Body +1px (chest expands)
       ████████
        ██  ██
       ███  ███        ← Feet STAY PLANTED!
```

**Critical**: Feet do NOT move. Only the upper body rises.

### Frame 3 — Full Breath (Peak)

- Flame extends another 1px (now +2px total)
- Body stays at +1px
- Flame tip shifts 1px sideways (flicker)

### Frame 4 — Exhale (Settling)

- Flame at +1px (settling back)
- Body returns to normal
- Flame tip shifts opposite direction

---

## Onion Skinning

Shows previous/next frames as transparent overlays while you draw:

```
With onion skinning ON:
  ░░░░  ████  ░░░░       ░ = ghost frames (30% opacity)
 ░░░░░ ██████ ░░░░░      █ = current frame (solid)
  ░░░░  ████  ░░░░
```

In Aseprite: press F3 or click the onion skin icon in the timeline.

---

## Frame Timing

Not all frames equal duration:

| Frame | Duration | Why |
|---|---|---|
| 1 (Rest) | 200ms | Pause at bottom |
| 2 (Inhale) | 150ms | Inhale slightly faster |
| 3 (Full) | 200ms | Pause at top |
| 4 (Exhale) | 150ms | Matches inhale |

---

## The Mistake You'll Make

The animation looks jittery. The loop has a visible "pop" where frame 4 jumps to frame 1.

Riku plays at half speed:

> "Two problems. Frame 4 doesn't match frame 1 closely enough — there's a 1-pixel jump at the loop point. And you're moving too many things at once. Only 2-3 elements should move, at different rates."

### The Fix: Seamless Loop + Offset Timing

**Seamless loop**: Frame 4 must transition smoothly to Frame 1. If Frame 1 is rest, Frame 4 should be *almost* at rest.

**Offset timing**: Not everything moves in sync:

```
Frame:     1      2      3      4
Body:      0     +1     +1      0     ← moves on frame 2
Flame:     0     +1     +2     +1     ← moves every frame (lighter)
Eyes:      0      0     blink   0     ← occasional blink (separate)
```

The flame leads, the body follows. This creates organic feel.

---

## Expanding to 6 Frames

Six frames feels smoother:

```
Frame:  1     2     3     4     5     6
Body:   0    +1    +1    +1     0     0
Flame:  0    +1    +1    +2    +1     0
Time:  200   150   150   200   150   150  = 1000ms
```

For 32×32, 4-6 frames is the sweet spot.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Frame count | 4 minimum, 6 for smoother |
| Motion amount | 1-2 pixels maximum |
| Feet | NEVER move during idle |
| Flame/hair | Moves more than body (lighter) |
| Timing | Vary duration (150-200ms) |
| Loop | Frame N must flow seamlessly to Frame 1 |
| Onion skinning | Always on while animating |
| Offset | Different elements move on different frames |
| Total cycle | 700-1000ms |

---

## Exercise: Animate Ember's Idle

1. Create a 4-frame idle animation
2. Frame 1: Rest. Frame 2: Body +1px, flame +1px. Frame 3: Body +1px, flame +2px. Frame 4: Body normal, flame +1px.
3. Set durations: 200, 150, 200, 150ms
4. Enable onion skinning, verify smooth transitions
5. Test loop point: does frame 4→1 pop? Fix if needed.
6. Save as `ember-idle.aseprite`

**Bonus**: Add a blink every 3-4 cycles (separate layer). Blink = 2 frames: eyes closed (80ms) → eyes open.

**Success criteria**: At normal speed, the animation feels alive but not distracting. A player can stare at it for 10 seconds without the loop becoming obvious.

---

[← Chapter 5: Pixel Art Rules](chapter-05-pixel-art-rules.md) | [Chapter 7: Walk Cycle →](chapter-07-walk-cycle.md)
