# Chapter 10: Attack Animation — The Art of the Smear Frame

[← Chapter 9: Jump](chapter-09-jump.md) | [Chapter 11: Hit & Death →](chapter-11-hit-death.md)

---

## The Problem

Ember needs to fight. You draw a sword slash: sword back, then sword forward. Two frames. It looks like a PowerPoint slide transition. You add frames in between — sword at 45°, 90°, 135°. Now it's smooth but slow. A 6-frame attack at 100ms each takes 600ms. In a fast platformer, that's death.

Riku grabs your mouse:

> "An attack isn't smooth motion — it's **anticipation, then explosion**. The wind-up is slow and readable. The strike is so fast it's almost invisible. That's where smear frames come in — the pixel art equivalent of motion blur."

---

## The Principle: Three Phases

```
Phase:      WIND-UP        STRIKE      FOLLOW-THROUGH
Frames:     2-3 frames     1-2 frames  2-3 frames
Timing:     slow (100ms)   FAST (40ms) medium (80ms)

            ╭──────╮╭╮╭────────╮
Timeline:   │ SLOW ││F││ MEDIUM │
            ╰──────╯╰╯╰────────╯
                     ↑
              1-2 frames. Blink and you miss it.
              That's what makes it feel FAST.
```

---

## Step-by-Step: 7-Frame Sword Slash

### Frames 1-2: Wind-Up (100ms each)

Ember pulls the sword back. Body rotates away from attack direction:

```
Frame 2 - WIND-UP PEAK:

        ████
       ██████         ← Flame compressed (storing energy)
        ████
      ████████        ← Body twisted, shoulder back
       ██████
        ████
       ██████
      ████████             ╲
        █  █                ╲  ← Sword at max backswing
       █    █                ╲
```

### Frame 3: THE SMEAR FRAME (40ms!)

The magic frame. The sword moves so fast it becomes a streak:

```
Frame 3 - SMEAR:

        ████
       ██████
        ████
       ██████
       ██████
        ████
       ██████
      ████████
   ═══════════════    ← SMEAR: sword is a horizontal STREAK!
       █    █            Not a sword shape — a BLUR.
       ▀    ▀
```

The smear frame is NOT a realistic sword position. It's an IMPRESSION of speed.

### Frame 4: Strike Impact (40ms)

Sword at full extension. Damage happens here:

```
Frame 4 - IMPACT:

        ████
       ██████         ← Flame whips forward
        ████
       ██████
       ██████         ← Body fully rotated forward
        ████
  ╱    ██████
 ╱    ████████        ← Sword at full extension
╱      █  █
      █    █
```

### Frames 5-7: Follow-Through (80ms each)

Sword continues past target, body recovers to idle.

---

## Smear Frame Rules

```
REALISTIC frame:              SMEAR frame:

     │                        ═══════════════
     │   ← recognizable       ↑
     │      sword shape       A STREAK connecting
     │                        start and end positions.
```

1. **Use the weapon's color** — the streak should match the sword
2. **Connect start to end** — bridges where weapon was and where it ends up
3. **Exaggerate length** — bigger smear = faster feeling
4. **Only 1-2 frames** — longer and it looks like a weird shape, not motion

---

## The Mistake You'll Make

You draw the smear. Play the animation. It doesn't feel fast. Everything is at 100ms per frame.

Riku points at your timeline:

> "The smear needs to be FAST. 40ms maximum. If it's on screen for 100ms, the brain processes it as a shape rather than motion. The contrast between slow wind-up and fast strike IS the feeling of speed."

### The Fix: Extreme Timing Contrast

```
WRONG (even timing):
Frame:  1     2     3     4     5     6     7
Time:   100   100   100   100   100   100   100  = 700ms

RIGHT (contrast):
Frame:  1     2     3     4     5     6     7
Time:   100   100   40    40    80    80    80   = 520ms
              ↑     ↑↑
              slow  FAST!  ← The contrast creates impact
```

---

## Attack Variations

| Attack | Smear Shape | Wind-Up |
|---|---|---|
| Horizontal slash | ═══ (horizontal streak) | Sword pulled back |
| Overhead slam | ║ (vertical streak) | Sword raised high |
| Uppercut | ╱ (diagonal streak) | Fist pulled down |
| Stab/thrust | →→→ (horizontal point) | Arm pulled back |
| Spin attack | Full arc | Body coils |

---

## Quick Reference

| Concept | Rule |
|---|---|
| Three phases | Wind-up (slow) → Strike (fast) → Follow-through (medium) |
| Smear frame | Streak connecting start/end (1-2 frames, 40ms) |
| Strike timing | 40-50ms per frame (blink-fast) |
| Wind-up timing | 80-100ms per frame (readable) |
| Total frames | 6-7 for a complete attack |
| Total time | 400-550ms |
| Timing contrast | Slow + fast = feeling of speed |
| Body rotation | Away during wind-up, toward on strike |
| Flame | Compressed in wind-up, whips forward on strike |

---

## Exercise: Animate Ember's Attack

1. Create a 7-frame attack animation:
   - Frames 1-2: Wind-up (100ms) — body coils, sword back
   - Frame 3: Smear (40ms) — horizontal streak
   - Frame 4: Impact (40ms) — full extension
   - Frames 5-7: Follow-through (80ms) — overshoot, return
2. The smear should be a streak, NOT a recognizable sword
3. Add flame reaction: compressed in wind-up, whips on strike
4. Save as `ember-attack.aseprite`

**Test**: Show someone the animation. Ask "does this feel fast?" If they say "it's okay," make the smear bigger and faster.

**Success criteria**: The strike should feel almost invisible — you know it happened because of the wind-up and follow-through, but the actual hit is a blur.

---

[← Chapter 9: Jump](chapter-09-jump.md) | [Chapter 11: Hit & Death →](chapter-11-hit-death.md)
