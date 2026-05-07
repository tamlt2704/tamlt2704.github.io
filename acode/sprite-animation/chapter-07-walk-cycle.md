# Chapter 7: Walk Cycle — Teaching Ember to Walk

[← Chapter 6: Idle Animation](chapter-06-idle.md) | [Chapter 8: Run Cycle →](chapter-08-run-cycle.md)

---

## The Problem

The player presses right. Ember slides across the screen — feet planted, body rigid, gliding like a ghost. You draw one leg forward, one back. Alternate two frames. It looks like Ember is doing the splits on a treadmill.

Riku pulls up a reference sheet:

> "A walk cycle is the hardest animation to get right. Our brains instantly detect when it's wrong. The secret isn't the legs — it's the **body**. The up-down bob, the weight shift, the arm swing. Get the body right and the legs follow."

---

## The Principle: Four Key Poses

```
The 4 Key Poses (repeated twice = 8-frame cycle):

  CONTACT       DOWN         PASSING       UP
  (heel strike) (lowest)    (one leg)     (highest)

    ██            ██           ██            ██
   ████          ████         ████          ████
   ████          ████         ████          ████
   █  █          █  █          █            █  █
  █    █        █    █         ██          █    █

  Legs spread   Body drops    One leg      Body rises
  front/back    1px lower     passes       1px higher

Body height wave:
         ╭─╮    ╭─╮
    ╭───╯   ╰───╯   ╰───
Frame: 1  2  3  4  5  6  7  8
Pose:  C  D  P  U  C  D  P  U
       (left leg)   (right leg)
```

---

## Step-by-Step: 8-Frame Walk Cycle

### Frame 1 — Contact (Left Foot Forward)

Front foot touches ground. Maximum leg spread:

```
Frame 1 - CONTACT:
        ████
       ██████         ← Flame tilts slightly forward
        ████
       ██████         ← Head at reference height
       ██████
      ████████        ← Arms: left back, right forward
       ██████
        █  █
      ██    ██        ← Legs at max spread
      ▀      ▀        ← Both feet on ground
```

### Frame 2 — Down (Lowest Point)

Front foot takes weight. Body drops 1px:

```
Frame 2 - DOWN:
        ████
       ██████         ← Flame compressed
       ██████         ← Head drops 1px
       ██████
       ██████
       ██████
        █  █
       █    █         ← Front leg bends (absorbing weight)
       ▀    ▀
```

### Frame 3 — Passing (Single Support)

Back leg swings forward past the planted leg:

```
Frame 3 - PASSING:
        ████
       ██████
       ██████         ← Head rising
       ██████
       ██████
        ██
        ██            ← One leg planted, other passing
        ▀
```

### Frame 4 — Up (Highest Point)

Planted leg straightens, pushing body to highest point (+1px):

```
Frame 4 - UP:
       ██████
      ████████        ← Flame stretches (momentum)
       ██████         ← Head at highest (+1px)
       ██████
       ██████
        █  █
       █    █         ← Legs starting to spread
       ▀     ▀
```

### Frames 5-8: Mirror with opposite leg forward.

### Frame Timing

All frames equal: **100-120ms per frame**. Total cycle: ~800ms.

---

## The "Head Stays Level" Trick

> "The head bobs only 1 pixel. More than that looks like bouncing, not walking. Keep the **eyes** at consistent height — the brain tracks eyes, not heads."

---

## The Mistake You'll Make

You draw all 8 frames. Ember looks like it's marching in place — or ice skating. No sense of weight.

Riku points at the feet:

> "Two problems. First: your feet are sliding. When a foot is planted, it must stay in the SAME position for 3-4 frames. If it moves even 1 pixel while 'planted,' the brain sees skating. Second: no weight. The down pose needs compression."

### The Fix: Planted Feet + Weight

```
WRONG (sliding):              RIGHT (planted):
Frame 1: foot at x=10        Frame 1: foot at x=10
Frame 2: foot at x=11 ← NO!  Frame 2: foot at x=10 ← SAME
Frame 3: foot at x=12 ← NO!  Frame 3: foot at x=10 ← SAME
Frame 4: foot lifts           Frame 4: foot lifts
```

Weight indicators: down pose body 1px lower, planted leg slightly bent, minimal head bob.

---

## Walk Cycle Checklist

| Check | Pass? |
|---|---|
| Body bobs exactly 1px up/down | ☐ |
| Planted foot stays in same position | ☐ |
| Arms swing opposite to legs | ☐ |
| Contact = max leg spread | ☐ |
| Down = lowest body position | ☐ |
| Passing = one leg visible | ☐ |
| Up = highest body position | ☐ |
| Loop seamless (frame 8 → frame 1) | ☐ |
| Flame has secondary motion (trails body) | ☐ |

---

## Quick Reference

| Concept | Rule |
|---|---|
| Key poses | Contact → Down → Passing → Up (×2) |
| Frame count | 8 frames (standard) |
| Body bob | 1 pixel maximum |
| Planted foot | Does NOT move until leg lifts |
| Arm swing | Opposite to legs |
| Frame timing | 100-120ms per frame (equal) |
| Head level | Eyes stay consistent height |
| Secondary motion | Flame trails 1-2 frames behind |
| Full cycle | ~800ms |

---

## Exercise: Animate Ember's Walk

1. Create 8 frames: Contact, Down, Passing, Up (×2 for each leg)
2. Add arm swing (1-2 pixel shifts on body sides)
3. Add flame trailing behind on direction changes
4. Set all frames to 100ms
5. Verify: planted feet don't slide, body bobs only 1px
6. Test loop — does frame 8 flow into frame 1?
7. Save as `ember-walk.aseprite`

**Success criteria**: The walk should feel weighted and natural. A viewer should tell which direction Ember is walking without seeing the background move.

---

[← Chapter 6: Idle Animation](chapter-06-idle.md) | [Chapter 8: Run Cycle →](chapter-08-run-cycle.md)
