# Chapter 8: Run Cycle — Speed Through Motion

[← Chapter 7: Walk Cycle](chapter-07-walk-cycle.md) | [Chapter 9: Jump →](chapter-09-jump.md)

---

## The Problem

The player holds shift to run. You speed up the walk from 100ms to 50ms per frame. It looks like a Benny Hill sketch. You add more frames. Now it's a smooth fast walk, but still doesn't feel like running.

Riku stops your playback:

> "Running isn't fast walking. It's a completely different motion. In a walk, one foot is always on the ground. In a run, there's a moment where **both feet are off the ground** — the flight phase. That's what makes it feel fast."

---

## The Principle: Walk vs. Run

```
WALK: One foot always grounded
Frame:  1    2    3    4    5    6
Feet:   LR   L    L    LR   R    R
        both one  one  both one  one

RUN: Both feet leave the ground
Frame:  1    2    3    4    5    6
Feet:   L    -    R    -    L    -
        one  NONE one  NONE one  NONE
             AIR!      AIR!      AIR!
```

The flight phase is what the brain reads as running.

---

## Step-by-Step: 6-Frame Run Cycle

### Key Differences from Walk

| Element | Walk | Run |
|---|---|---|
| Body lean | Upright (0-5°) | Forward (15-25°) |
| Arm swing | Small | Large, pumping |
| Body bob | 1px | 2px |
| Flight phase | None | Both feet airborne |
| Knee lift | Low | High |

### Frame 1 — Push Off (80ms)

Back leg drives body forward. Maximum extension:

```
       ██████
      ████████        ← Flame swept BACK (speed!)
       ██████
       ██████         ← Body leaning forward ~20°
       ██████
         █  █
          █  ██       ← Back leg fully extended
          ▀    ▀
```

### Frame 2 — Flight Phase (60ms)

Both feet off ground. THE frame that says "running":

```
      ████████
     ██████████       ← Flame trails behind
      ████████
      ████████        ← Body at highest point
       ██████
        █  █
        █  █          ← Both legs tucked
     ~~~~~~~~~~~      ← GAP between feet and ground!
```

### Frame 3 — Contact (80ms)

Front foot strikes ground. Body begins to lower:

```
       ██████
      ████████        ← Flame still trailing
       ██████
       ██████         ← Body descending
       ██████
        █  █
       █    █         ← Front leg reaching down
       ▀     ▀        ← Contact!
```

### Frames 4-6: Mirror with opposite leg.

### Frame Timing

| Frame | Duration | Why |
|---|---|---|
| 1 (Push) | 80ms | Ground contact — slightly longer |
| 2 (Flight) | 60ms | Airborne — fast! |
| 3 (Contact) | 80ms | Ground contact |
| 4-6 | Mirror | Same pattern |

Total cycle: 440ms (walk was 800ms — almost twice as fast).

---

## The Flame Tells the Story

```
IDLE:           WALK:           RUN:
  ████            ████           ████████
 ██████          ██████        ████████████
  ████            ████          ████████

Straight up.    Slight trail.   Swept far back.
```

> "The flame is your cheat code for speed. Pointed up = still. Swept back = fast."

---

## The Mistake You'll Make

The run looks fast but Ember floats — no impact, no weight. The flight phase looks the same height as ground phases.

Riku pauses on the contact frame:

> "You're missing **impact**. When the foot hits ground in a run, the body compresses briefly. And your flight body is at the same height as ground phases. It needs to be HIGHER. Exaggerate the difference."

### The Fix: Height Contrast

```
WRONG (even height):            RIGHT (variation):
Frame:  1    2    3             Frame:  1    2    3
Body:   ──── ──── ────         Body:   ─╮   ╭─   ─╮
                                        ╰───╯     ╰──
Height: same same same         Height: low  HIGH  mid
```

Push frame: lowest (compressed). Flight: highest (+2px). Contact: middle.

---

## Speed Through Fewer Frames

Counter-intuitive: fewer frames = faster feeling.

```
8 frames: Smooth but doesn't feel fast
6 frames: Good balance (Ember's run)
4 frames: Very fast (dash)
2 frames: Extreme speed (teleport)
```

The brain fills in gaps. Fewer frames = more gaps = brain assumes speed.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Key difference | Flight phase (both feet airborne) |
| Frame count | 6 frames |
| Body lean | 15-25° forward |
| Flight phase | Body at highest, legs tucked |
| Push phase | Body at lowest, back leg extended |
| Frame timing | 60-80ms (faster than walk's 100ms) |
| Total cycle | ~440ms (walk ~800ms) |
| Flame | Swept back horizontally |
| Impact | Contact frame shows compression |
| Speed trick | Fewer frames = feels faster |

---

## Exercise: Animate Ember's Run

1. Create 6 frames: Push, Flight, Contact (×2 for each leg)
2. Flight frame body 2px higher than push frame
3. Sweep flame back horizontally in all frames
4. Add forward lean (15-20°)
5. Set timing: 80, 60, 80, 80, 60, 80ms
6. Compare with walk — run should feel distinctly faster
7. Save as `ember-run.aseprite`

**Success criteria**: A viewer should identify this as running (not fast walking) from a single still frame, thanks to the lean and leg positions.

---

[← Chapter 7: Walk Cycle](chapter-07-walk-cycle.md) | [Chapter 9: Jump →](chapter-09-jump.md)
