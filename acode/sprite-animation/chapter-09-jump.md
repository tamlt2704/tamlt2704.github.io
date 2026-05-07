# Chapter 9: Jump Animation — Defying Gravity with Style

[← Chapter 8: Run Cycle](chapter-08-run-cycle.md) | [Chapter 10: Attack →](chapter-10-attack.md)

---

## The Problem

The player presses jump. Ember moves upward. The idle animation keeps playing. It looks like an invisible elevator lifting a statue. You try a single "arms up" frame. Now it looks like alien abduction.

Riku draws five quick sketches:

> "A jump isn't one pose — it's a **story**. Anticipation, launch, apex, fall, land. Five acts. The crouch tells players 'I'm about to go up.' The spread at apex says 'I'm at the top.' Without these cues, the jump feels disconnected."

---

## The Principle: Squash and Stretch

```
  SQUASH        STRETCH       NORMAL        STRETCH       SQUASH
  (crouch)      (launch)      (apex)        (fall)        (land)

  ██████          ██            ████           ██          ██████
  ██████          ██            ████           ██          ██████
   ████           ██            ████           ██           ████
   ████           ██           █    █          ██           ████
  ██████          ██           █    █          ██          ██████

  Wide+short    Narrow+tall   Normal       Narrow+tall   Wide+short
```

Volume stays the same — it just redistributes. Squash = wide/short. Stretch = narrow/tall.

---

## The 5 Key Poses

### Pose 1: Anticipation (Crouch) — 60-80ms

Body goes DOWN before going up. Telegraphs the action:

```
        ████
       ██████         ← Flame compressed
      ████████        ← Body SQUASHED (wider, shorter)
      ████████
      ██ ████ ██      ← Arms pulled back
      ████████        ← Legs bent deeply
       ▀▀▀▀▀▀        ← Feet flat, gripping ground
```

### Pose 2: Launch (Blast Off) — 60ms

Explosive upward. Body stretches vertically:

```
      ████████
     ██████████       ← Flame EXPLODES upward
        ████          ← Body STRETCHED (narrow, tall)
        ████
         ██
         ██           ← Legs extending down
         ▀▀           ← Toes leaving ground
```

### Pose 3: Apex (Hang Time) — 100-120ms

Top of jump. Body relaxes. Hold this LONGER than physics suggests:

```
       ██████
      ████████        ← Flame floats (weightless)
       ██████         ← Normal proportions
        ████
       █    █         ← Arms slightly raised
       ▀    ▀         ← Feet dangling
```

### Pose 4: Fall (Descending) — 60ms

Gravity takes over. Body stretches down, bracing:

```
        ████
       ██████         ← Flame swept UP (opposite to motion)
        ████          ← Body stretches vertically
        ████
        ████          ← Legs pulled up (bracing)
         ▀▀
```

### Pose 5: Land (Impact Squash) — 80ms

Maximum compression. Wider squash than the anticipation:

```
       ██████         ← Flame compressed
     ██████████       ← Body SQUASHED (widest point)
      ████████
      ██    ██        ← Legs bent absorbing impact
     ▀▀▀▀  ▀▀▀▀      ← Feet WIDE (stability)
```

---

## The Full Timeline

```
Pose:     1         2        3         4        5
Name:   CROUCH → LAUNCH → APEX   → FALL   → LAND
Time:    80ms     60ms    120ms     60ms     80ms
Shape:   squash   stretch  normal  stretch  squash
Flame:   down     up/big   float    up      compressed
```

Add 2-3 recovery frames after landing (body rises back to idle).

---

## Connecting to Physics

The animation matches the physics curve but doesn't control it:

```
Height
  │        ╭───╮         ← APEX (pose 3) — hold while near top
  │      ╱       ╲
  │    ╱           ╲     ← FALL (pose 4) — during descent
  │╱                 ╲
  ├─────────────────────── Ground
  ↑         ↑          ↑
  LAUNCH    APEX       LAND
```

Pose 1 plays BEFORE physics launches. Pose 5 plays on ground collision.

---

## The Mistake You'll Make

The jump looks mechanical. No flow between poses. Landing feels disconnected.

Riku plays it frame by frame:

> "Two issues. First: anticipation is too long — 200ms feels laggy. Keep it to 60ms max. Second: no **recovery** after landing. You go from squash to standing instantly. Add 2 frames where the body slowly rises."

### The Fix

```
Land (squash) → Recovery 1 → Recovery 2 → Idle

  ████████       ██████        ████          ████
  ████████       ██████       ██████        ██████
  ██    ██       ██  ██        █  █          █  █
  ████████       ██████       ██  ██        ██  ██

  Max squash     Rising...    Almost up     Standing
```

---

## Hang Time: The Secret

> "In real physics, the apex is instantaneous. In games, we hold the apex pose for 100-150ms. It gives players a sense of control at the top. Every great platformer does this."

---

## Quick Reference

| Concept | Rule |
|---|---|
| Key poses | Anticipation → Launch → Apex → Fall → Land |
| Squash & stretch | Crouch/land = wide+short; launch/fall = narrow+tall |
| Anticipation | 40-80ms max (snappy, not laggy) |
| Apex hold | 100-150ms (longer than physics suggests) |
| Landing recovery | 2-3 frames returning to idle |
| Flame | Opposite to motion direction |
| Volume | Same mass, just redistributed |
| Total poses | 5 key + 2-3 recovery = 7-8 frames |

---

## Exercise: Animate Ember's Jump

1. Create 7 frames:
   - Frame 1: Anticipation (squash) — 60ms
   - Frame 2: Launch (stretch) — 60ms
   - Frame 3: Apex (relaxed) — 120ms
   - Frame 4: Fall (stretch down) — 60ms
   - Frame 5: Land (squash, wider than crouch) — 80ms
   - Frames 6-7: Recovery (rising back to idle) — 80ms each
2. Verify squash frames are wider, stretch frames are taller
3. Flame trails opposite to motion
4. Save as `ember-jump.aseprite`

**Success criteria**: Even without background movement, a viewer should tell the character jumped — the poses alone communicate the arc.

---

[← Chapter 8: Run Cycle](chapter-08-run-cycle.md) | [Chapter 10: Attack →](chapter-10-attack.md)
