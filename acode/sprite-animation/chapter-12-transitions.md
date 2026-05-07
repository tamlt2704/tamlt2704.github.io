# Chapter 12: Transitions — Smoothing the Gaps Between States

[← Chapter 11: Hit & Death](chapter-11-hit-death.md) | [Chapter 13: VFX →](chapter-13-vfx.md)

---

## The Problem

You wire up animations. Idle plays. Press right — instantly Ember is mid-stride. Jump — one frame running, next frame apex pose. Every state change "pops."

Riku watches:

> "You've built animations as isolated loops. But in a game, they flow into each other. Idle to run needs 1-2 frames where the body shifts from relaxed to leaning. These **transition frames** separate amateur from professional."

---

## The Principle: In-Betweens for State Changes

```
WITHOUT transitions (popping):
  IDLE ────── ┃ ────── RUN     (instant cut, jarring)

WITH transitions (smooth):
  IDLE ── LEAN ── PUSH OFF ── RUN
           ↑         ↑
      Transition frames (1-2 each)
```

---

## The Transition Map

Not every state change needs the same treatment:

| FROM → TO | Frames | Why |
|---|---|---|
| Idle → Run | 2 | Body shifts weight, leans |
| Run → Idle (skid) | 2-3 | Deceleration |
| Walk → Run | 1 | Increase lean |
| Jump → Fall | 1 | Apex pose (already exists) |
| Fall → Land | 0 | Impact is instant (good!) |
| Any → Attack | 0 | Attacks interrupt instantly |
| Any → Hit | 0 | Hits interrupt instantly |

Key: **not all transitions need frames**. Attacks and hits should interrupt immediately.

---

## Key Transitions

### Idle → Run (2 frames, 60ms each)

```
IDLE:              TRANS 1 (lean):     TRANS 2 (push):     RUN:

   ██████            ██████             ██████            ██████
  ████████          ████████           ████████          ████████
   ██████            ██████            ██████            ██████
   ██████           ██████            ██████            ██████
    █  █              █  █             █   █             █   ██
   █    █            █    █           █     █           █      ▀

  Standing.         Tilts forward.   First step.        Full run.
```

### Run → Idle (3 frames — Skid Stop, 80ms each)

```
RUN → SKID 1 → SKID 2 → SKID 3 → IDLE

       Lean back,    Settling,     Almost still,   Standing.
       dust puff!    decelerating  weight centered
```

Add dust particles on SKID 1 for polish.

### Jump Apex (1 frame)

The apex frame bridges "going up" and "coming down" — it already exists in your jump animation (Chapter 9, Pose 3).

---

## The Mistake You'll Make

You add transitions everywhere. Every action feels sluggish. Press jump — wait 120ms for transition. Press attack — wait 80ms. Unresponsive.

Riku frowns:

> "You're adding transitions where they don't belong. Rule: **player-initiated actions should feel instant**. Jump, attack, dash — interrupt immediately. Transitions are for **cosmetic state changes** only."

### The Fix: Priority System

```
INTERRUPT IMMEDIATELY (no transition):
- Attack (button → attack NOW)
- Jump (button → jump NOW)
- Hit (damage → react NOW)

USE TRANSITIONS (cosmetic):
- Idle → Run (holding direction)
- Run → Idle (released direction)
- Rise → Fall (physics state change)
```

If the player pressed a button, respond instantly. If the engine changed states, smooth it.

---

## Transition Frame Budget

| Transition | Extra Frames |
|---|---|
| Idle → Run | 2 |
| Run → Idle (skid) | 3 |
| Walk → Run | 1 |
| Run → Walk | 1 |
| Land → Idle | (reuse jump recovery) |
| **Total** | **~7-9 extra frames** |

Manageable on top of your core animations.

---

## Quick Reference

| Concept | Rule |
|---|---|
| Purpose | Bridge states to prevent "popping" |
| Frame count | 1-3 per transition |
| Timing | 60-80ms per frame |
| Player actions | Interrupt instantly (no transition) |
| Cosmetic only | Transitions for state changes, not inputs |
| Idle → Run | 2 frames (lean + first step) |
| Run → Idle | 2-3 frames (skid) |
| Attack/Hit | 0 transition frames |
| Budget | ~7-9 extra frames total |

---

## Exercise: Draw Transition Frames

1. Idle → Run: 2 frames (progressive lean + weight shift)
2. Run → Idle: 3 frames (skid, decelerate, settle)
3. Walk → Run: 1 frame (lean increase)
4. Test: play [last frame of A] → [transition] → [first frame of B]
5. Save as `ember-transitions.aseprite`

**Test sequence**: Idle (4f) → Trans (2f) → Run (6f) → Trans (3f) → Idle (4f). Should feel like one continuous motion.

**Success criteria**: State changes should be invisible — you can't point to the exact frame where "idle ends and run begins."

---

[← Chapter 11: Hit & Death](chapter-11-hit-death.md) | [Chapter 13: VFX →](chapter-13-vfx.md)
