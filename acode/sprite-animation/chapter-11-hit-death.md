# Chapter 11: Hit Reaction & Death — Making Damage Feel Real

[← Chapter 10: Attack](chapter-10-attack.md) | [Chapter 12: Transitions →](chapter-12-transitions.md)

---

## The Problem

An enemy hits Ember. The health bar goes down. Ember keeps walking. No reaction. No feedback. The player doesn't realize they took damage until they're dead.

Riku watches you take damage three times without noticing:

> "Hit feedback is the most important animation in your game. If the player can't FEEL getting hit, they can't learn to avoid it. A hit needs three things: a **flash** (instant visual), a **pose** (physical reaction), and **recovery** (return to normal)."

---

## The Principle: Impact → Reaction → Recovery

```
Event:    HIT!     REACT      RECOVER     NORMAL
Frame:     1       2-3         4-5          6+
Time:     40ms    160ms       160ms         →

Visual:   WHITE    KNOCKBACK   BLINK        NORMAL
          FLASH    POSE        (invuln)     (idle)
```

---

## Hit Reaction: 5 Frames

### Frame 1: Impact Flash (40ms)

Ember turns completely white for 1 frame. Every pixel = #FFFFFF:

```
Frame 1 - WHITE FLASH:
  ████████
  ████████         All pixels become solid white.
  ████████         No detail. Pure flash.
  ████████         Highest contrast against any background.
  ████████
```

### Frame 2-3: Knockback (80ms each)

Body recoils away from the hit source:

```
Frame 2 - KNOCKBACK:
           ████
          ██████      ← Flame whips toward hit direction
          ██████      ← Head snaps back
           ████       ← Body arches AWAY from hit
          ██████
           █  █       ← Feet leave ground slightly
          ▀  ▀
```

### Frame 4-5: Recovery (80ms each)

Body returns to neutral. Combined with invincibility blink.

---

## Invincibility Blink

After hit reaction, toggle visibility every 60ms for ~1 second:

```
Frame:  1    2    3    4    5    6    7    8 ...
Show:   ON   off  ON   off  ON   off  ON   ON
Time:   60ms each

Total blink: ~500-1000ms
Pattern: alternate visible/invisible
End: stay visible (blink stops)
```

---

## Death Animation: 6 Frames

Death is the ultimate hit reaction. It needs to feel significant:

```
Frame 1: White flash — 40ms
Frame 2: Extreme knockback — 100ms
Frame 3: DRAMATIC PAUSE (held in air) — 150ms  ← The secret weapon
Frame 4: Body begins breaking apart — 100ms
Frame 5: Particle burst (4-6 pieces scatter) — 100ms
Frame 6: Particles fade out — 150ms

Total: ~640ms
```

### The Dramatic Pause (Frame 3)

> "The pause before the character falls is what makes death dramatic instead of instant. It's the moment where the player goes 'oh no.' Without it, death is just poof-gone."

```
Frame 3 - FREEZE:       Frame 5 - BURST:

  ████████                 ·  · ·
   ████████              ·  ·   · ·
  ████████                · ·  ·  ·
   ████████                ·  · ·
  (held in air)          (pieces scatter)
```

---

## The Mistake You'll Make

The hit reaction plays but doesn't feel impactful. The knockback is too subtle — 1 pixel lean is invisible at game speed.

Riku hits Ember and shrugs:

> "Exaggerate everything. Knockback should move 3-4 pixels. The flash must be unmissable. And you're missing **hit stop** — freezing the game for 2-3 frames on impact. That's what makes hits register."

### The Fix: Exaggeration + Hit Stop

```
WITHOUT hit stop:              WITH hit stop:
Frame: 1  2  3  4  5          Frame: 1  2  3  4  5  6  7
       H  K  K  R  I                H  F  F  F  K  K  R
       (flows past)                 ↑  ↑─────↑
                                    hit FREEZE (50ms)
                                    Impact REGISTERS.
```

Hit stop is code (Chapter 20), but the impact frame should look good held for extra time.

---

## Complete Hit Feedback Stack

| Layer | Effect | Duration |
|---|---|---|
| Hit stop | Game freeze | 50-80ms |
| White flash | Solid white silhouette | 40ms |
| Knockback | Body arches away | 160ms |
| Screen shake | Camera jolts | 100ms |
| Invincibility blink | Toggle visibility | 500-1000ms |

All layers stack simultaneously.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Flash | 1 frame, all-white silhouette (40ms) |
| Knockback | 2-3 frames, 3-4px offset, arch away from hit |
| Recovery | 1-2 frames returning to idle |
| Blink | 60ms on/off for 0.5-1s |
| Death pause | Hold knockback 100-150ms before dissolve |
| Death particles | Break into 4-8 pieces that scatter |
| Exaggeration | More is better — subtle = invisible |
| Direction | Knockback opposite to hit source |

---

## Exercise: Animate Hit and Death

**Part A — Hit Reaction (5 frames):**
1. Frame 1: White flash (all white) — 40ms
2. Frame 2-3: Knockback (3-4px offset, arched back) — 80ms each
3. Frame 4-5: Recovery (returning to neutral) — 80ms each

**Part B — Death (6 frames):**
1. Frame 1: White flash — 40ms
2. Frame 2: Extreme knockback — 100ms
3. Frame 3: Dramatic pause (held in air) — 150ms
4. Frame 4: Breaking apart — 100ms
5. Frame 5: Particle burst — 100ms
6. Frame 6: Fade out — 150ms

Save as `ember-hit.aseprite` and `ember-death.aseprite`

**Success criteria**: The hit should make you wince. The death should feel dramatic and final.

---

[← Chapter 10: Attack](chapter-10-attack.md) | [Chapter 12: Transitions →](chapter-12-transitions.md)
