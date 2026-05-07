# Chapter 14: Enemies — Animating Different Body Types

[← Chapter 13: VFX](chapter-13-vfx.md) | [Chapter 15: Environment →](chapter-15-environment.md)

---

## The Problem

You need enemies. You draw a slime — it looks like green Ember without legs. A bat — Ember with wings. A skeleton — white Ember. Every enemy has the same proportions and movement style.

Riku lines them up:

> "They all move the same because you animated them the same way. A slime is a blob that squashes and stretches — no joints. A bat flutters with rapid tiny wing beats. A skeleton is rigid and mechanical. Different body types need fundamentally different animation approaches."

---

## The Principle: Body Type Dictates Animation

```
BLOB (slime):        FLYER (bat):        RIGID (skeleton):
- No skeleton        - Wings drive all   - Stiff joints
- Pure squash/       - Rapid, small      - Limited bend
  stretch              movements         - Mechanical, jerky
- Bouncy             - Body barely moves
```

---

## Enemy 1: Slime (Squash/Stretch Bounce)

No skeleton — movement IS deformation. 16×16 canvas.

### Slime Idle (4 frames): Gentle pulse

```
Frame 1 (rest):    Frame 2 (squash):  Frame 3 (rest):    Frame 4 (stretch):
     ████               ██████            ████              ██
    ██████             ████████           ██████            ████
   ████████           ██████████         ████████          ██████
   ▀▀▀▀▀▀▀▀          ▀▀▀▀▀▀▀▀▀▀        ▀▀▀▀▀▀▀▀         ▀▀▀▀▀▀
  Normal.           Wider+shorter.     Normal.           Taller+narrower.
  100ms             100ms              100ms             100ms
```

### Slime Movement (6 frames): Hop

Slimes don't walk — they hop. Each hop is a mini jump:

```
SQUASH → LAUNCH → AIR → AIR → LAND → SETTLE
80ms     60ms     80ms   80ms   60ms   80ms
```

The slime's SHAPE is the animation. No limbs — just deformation.

---

## Enemy 2: Bat (Wing Flutter)

Rapid small wing movements. Body barely moves. 16×16 canvas.

### Bat Flight (4 frames):

```
Frame 1 (up):     Frame 2 (mid):    Frame 3 (down):   Frame 4 (mid):
  ██      ██         ██    ██                            ██    ██
 ████    ████       ████  ████       ██████████         ████  ████
  ████████           ████████         ████████           ████████
    ████               ████             ████               ████
     ██                 ██               ██                 ██

  60ms              50ms             60ms               50ms
  Total: 220ms (FAST — bats flutter rapidly)
```

Key: body bobs 1px opposite to wings (up when wings down). No separate idle — bats are always flying. Slow the timing for "hover."

---

## Enemy 3: Skeleton (Stiff Walk)

Rigid — bones don't bend. Mechanical, jerky. 24×24 canvas.

### Skeleton Walk (6 frames):

```
   ██     ← skull (doesn't bob — no muscles!)
  ████    ← ribcage
   ██     ← spine
  █  █    ← legs swing like pendulums from hip
 ▀    ▀

Key differences from Ember:
- NO body bob (no muscles to compress)
- Stiff joints (legs swing, don't bend at knee)
- Slower: 100-120ms per frame (heavy, deliberate)
- No secondary motion (no hair/cloth)
```

---

## Enemy 4: Boss (Larger Canvas)

| Aspect | Regular Enemy | Boss |
|---|---|---|
| Canvas | 16-24px | 48-64px |
| Frames per anim | 4-6 | 8-12 |
| Speed | 50-100ms | 100-150ms |
| Anticipation | 1 frame | 3-4 frames (player must react!) |
| Weight | Light/medium | Heavy (slow starts, hard stops) |

Boss attacks telegraph for 300-400ms. Players MUST read and react.

---

## The Mistake You'll Make

All enemies have the same frame count and timing as Ember. Everything feels samey.

Riku compares:

> "If every character moves at the same speed, they feel like palette swaps. The slime should feel BOUNCIER. The skeleton STIFFER. The bat TWITCHIER. Contrast in timing creates diversity."

### The Fix: Timing Creates Personality

```
Character:    Ember     Slime      Bat       Skeleton    Boss
Frame time:   80-100ms  80-100ms   50-60ms   100-120ms   120-150ms
Feel:         Balanced  Bouncy     Twitchy   Mechanical  Heavy
```

---

## Animation Budget Per Enemy

| Animation | Slime | Bat | Skeleton | Boss |
|---|---|---|---|---|
| Idle | 4 (pulse) | 4 (hover) | 2 (sway) | 6 (breathe) |
| Move | 6 (hop) | 4 (fly) | 6 (walk) | 8 (stomp) |
| Attack | 4 (lunge) | 3 (dive) | 5 (swing) | 10 (slam) |
| Hit | 3 (jiggle) | 3 (tumble) | 3 (rattle) | 4 (flinch) |
| Death | 4 (splat) | 4 (fall) | 5 (collapse) | 8 (dramatic) |
| **Total** | **21** | **18** | **22** | **36** |

---

## Quick Reference

| Enemy | Key Trait | Speed | Canvas |
|---|---|---|---|
| Slime | Squash/stretch, no skeleton | 80-100ms | 16×16 |
| Bat | Rapid flutter, static body | 50-60ms | 16×16 |
| Skeleton | Stiff joints, no bob | 100-120ms | 24×24 |
| Boss | Heavy, telegraphed | 120-150ms | 48-64px |

| Concept | Rule |
|---|---|
| Body type = style | Blob=deform, Flyer=wings, Rigid=mechanical |
| Timing = personality | Fast=twitchy, Slow=heavy |
| Boss telegraphs | 3-4 frames obvious wind-up |
| Contrast | Enemies feel different from each other AND player |

---

## Exercise: Animate a Slime and a Bat

**Part A — Slime (16×16):**
1. Idle: 4 frames (squash/stretch pulse)
2. Hop: 6 frames (squash → launch → air → air → land → settle)

**Part B — Bat (16×16):**
1. Flight: 4 frames (wings up → mid → down → mid)
2. Timing: 50-60ms per frame

Save as `enemy-slime.aseprite` and `enemy-bat.aseprite`

**Success criteria**: Slime feels bouncy and grounded. Bat feels twitchy and airborne. They should NOT feel like the same character with different skins.

---

[← Chapter 13: VFX](chapter-13-vfx.md) | [Chapter 15: Environment →](chapter-15-environment.md)
