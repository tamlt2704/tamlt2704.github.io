# Sprite Animation & Pixel Art: A Game Dev Survival Story

You're making your first game — **Ember Quest** — a 2D action-platformer about a tiny fire spirit navigating a frozen world. You have the game engine figured out (Canvas, physics, collision). What you don't have is a character.

You open Photoshop. You draw a blob. It looks like a melted gummy bear. You try to animate it walking. It looks like the blob is having a seizure.

**Riku** (the pixel artist from the isometric series) sees your screen and winces:

> "You're drawing at 1920×1080 and scaling down. You're using anti-aliasing on pixel art. Your walk cycle has 3 frames and no follow-through. The idle pose has no weight. Stop. Let me teach you how sprites actually work — from the first pixel to a full animation sheet."

He opens Aseprite. A 32×32 canvas. A 4-color palette.

> "Constraints are freedom. A small canvas forces you to make every pixel count. Let's start with a single frame. Then we'll make it breathe. Then walk. Then run. Then attack. By the end, you'll have a full character sheet ready for any game engine."

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Game Dev + Aspiring Artist | "I can code physics but I can't draw a circle." |
| **Riku** | Pixel Artist / Mentor | "Every pixel is a decision. No pixel is accidental." |
| **The Blob** | Your first attempt | Formless. Lifeless. Haunts your dreams. |
| **Ember** | The character you'll create | A tiny fire spirit. 32×32. Full of life. |
| **The Smear Frame** | That one trick | Makes 6-frame animations feel like 24. |
| **The Sprite Sheet** | Final deliverable | Every pose, every frame, one PNG. Game-ready. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Aseprite** | Pixel art editor + animation ($20, worth every penny) |
| **Libresprite** | Free/open-source Aseprite fork (alternative) |
| **Piskel** | Free browser-based pixel editor (for quick experiments) |
| **Canvas API** | Rendering sprites in-game (JavaScript) |
| **Tiled** | Placing sprites in a game world (optional) |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Ember needs a new animation for the game
   │
   ▼
  🤔 Riku teaches the art/animation principle behind it
   │
   ▼
  ✏️  You draw it (pixel by pixel)
   │
   ▼
  💥 It looks stiff, floaty, or wrong
   │
   ▼
  🧠 You learn WHY and apply the fix (timing, weight, anticipation)
   │
   ▼
  ⌨️  You implement it in code (sprite sheet → game engine)
   │
   ▼
  📋 Next animation
```

This series is **half art, half code**. You'll learn to draw sprites AND implement them. Every chapter produces both a visual asset and working game code.

---

## The Roadmap

### Part 1: Drawing — "Make a Character"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Draw a single pixel character"        │ Canvas size, silhouette, readability at small scale
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "It looks flat and lifeless"           │ Color theory — palettes, shading, hue shifting
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Give it personality"                  │ Shape language — round=friendly, sharp=dangerous
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Draw the environment tiles"           │ Tileset creation — ground, walls, props, consistency
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Sub-pixel rendering looks blurry"     │ Pixel art rules — no anti-aliasing, clean lines, jaggies
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Animation Principles — "Make It Move"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Animation                          │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Idle — make it breathe"               │ Idle animation — subtle motion, 4-6 frames, looping
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Walk cycle"                           │ Walk animation — contact, passing, weight, 6-8 frames
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Run cycle"                            │ Run vs walk — lean, airtime, fewer ground frames
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Jump — up and down"                   │ Jump animation — anticipation, apex, squash & stretch
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Attack — sword slash"                 │ Attack animation — wind-up, strike, follow-through, smear
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Advanced Animation — "Make It Feel"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Animation                          │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Hit reaction and death"               │ Impact frames — freeze frame, knockback, particles
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Transitions feel jarring"             │ Transition frames — blend between states smoothly
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Effects: fire, dust, sparkles"        │ VFX sprites — particles, loops, additive blending
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Enemies need different movement"      │ Character variety — slime bounce, bat flutter, boss
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Animate the environment"              │ World animation — torches, water, grass sway, parallax
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Implementation — "Put It in the Game"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Export the sprite sheet"              │ Sprite sheets — packing, atlas, JSON metadata
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Render sprites in Canvas/JS"          │ Sprite renderer — drawImage, clipping, frame timing
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "State machine: idle→run→jump→attack"  │ Animation state machine — transitions, interrupts, priority
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Flip, tint, scale at runtime"         │ Runtime manipulation — mirror, palette swap, flash white
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Ship it: the full character in-game    │ Polish — screen shake, hit stop, juice, game feel
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The 12 Principles of Animation (Pixel Art Edition)

Disney's 12 principles, adapted for sprites:

| Principle | Pixel Art Application |
|---|---|
| **Squash & Stretch** | Ember squishes on landing, stretches on jump |
| **Anticipation** | Crouch before jump, wind-up before attack |
| **Staging** | Clear silhouette — readable at 32×32 |
| **Straight Ahead / Pose to Pose** | Key poses first, then in-betweens |
| **Follow-through** | Hair/cape keeps moving after body stops |
| **Ease In / Ease Out** | More frames at start/end of motion, fewer in middle |
| **Arcs** | Arms swing in arcs, not straight lines |
| **Secondary Action** | Ember's flame flickers while walking |
| **Timing** | 6 frames = snappy. 12 frames = smooth. 3 frames = frantic. |
| **Exaggeration** | Push poses further than reality — it reads better small |
| **Solid Drawing** | Consistent volume — character doesn't grow/shrink between frames |
| **Appeal** | Simple, readable, memorable design |

You don't need all 12 in every animation. But you'll use at least 4-5 in every one.

---

## What You'll Create

By Chapter 20, you'll have a complete character sheet:

```
┌─────────────────────────────────────────────────────────────────┐
│  EMBER — Sprite Sheet (32×32 per frame)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Idle (6 frames):      🔥 🔥 🔥 🔥 🔥 🔥                       │
│  Walk (8 frames):      🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥                 │
│  Run (6 frames):       🔥 🔥 🔥 🔥 🔥 🔥                       │
│  Jump (5 frames):      🔥 🔥 🔥 🔥 🔥                           │
│  Attack (7 frames):    🔥 🔥 🔥 🔥 🔥 🔥 🔥                    │
│  Hit (3 frames):       🔥 🔥 🔥                                  │
│  Death (8 frames):     🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥                 │
│                                                                  │
│  VFX — dust (4f), fire trail (6f), slash arc (4f)               │
│  Enemies — slime (idle 4f, move 6f), bat (fly 4f)              │
│  Environment — torch (4f), water (8f), grass (4f)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Plus the JavaScript code to render it all in a game engine.

---

## Sprite Sheet Anatomy

A sprite sheet is a single image containing all frames:

```
┌────┬────┬────┬────┬────┬────┐
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │  ← Idle (row 0)
├────┼────┼────┼────┼────┼────┼────┬────┐
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │ F7 │ F8 │  ← Walk (row 1)
├────┼────┼────┼────┼────┼────┼────┼────┘
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │  ← Run (row 2)
├────┼────┼────┼────┼────┤
│ F1 │ F2 │ F3 │ F4 │ F5 │  ← Jump (row 3)
└────┴────┴────┴────┴────┘

Each cell: 32×32 pixels
Total sheet: 256×128 pixels (tiny file!)
```

In code, you clip a rectangle from the sheet to show one frame:

```javascript
ctx.drawImage(
  spriteSheet,
  frameX * 32, frameY * 32,  // source position (which frame)
  32, 32,                     // source size
  x, y,                       // destination on screen
  32, 32                      // destination size
);
```

---

## The Code Side (Preview)

```typescript
// sprite.ts — Sprite animation engine
class SpriteAnimator {
  private frame = 0;
  private elapsed = 0;
  
  constructor(
    private sheet: HTMLImageElement,
    private frameWidth: number,
    private frameHeight: number,
    private animations: Record<string, AnimationDef>,
    private currentAnim: string = 'idle',
  ) {}

  update(dt: number) {
    const anim = this.animations[this.currentAnim];
    this.elapsed += dt;
    
    if (this.elapsed >= anim.frameDuration) {
      this.elapsed = 0;
      this.frame++;
      if (this.frame >= anim.frameCount) {
        this.frame = anim.loop ? 0 : anim.frameCount - 1;
      }
    }
  }

  draw(ctx: CanvasRenderingContext2D, x: number, y: number, flip = false) {
    const anim = this.animations[this.currentAnim];
    const srcX = (anim.startFrame + this.frame) * this.frameWidth;
    const srcY = anim.row * this.frameHeight;

    ctx.save();
    if (flip) {
      ctx.scale(-1, 1);
      x = -x - this.frameWidth;
    }
    ctx.drawImage(
      this.sheet,
      srcX, srcY, this.frameWidth, this.frameHeight,
      x, y, this.frameWidth, this.frameHeight,
    );
    ctx.restore();
  }

  play(name: string) {
    if (this.currentAnim !== name) {
      this.currentAnim = name;
      this.frame = 0;
      this.elapsed = 0;
    }
  }
}
```

---

## Prerequisites

### Aseprite ($20) or Libresprite (free)

```bash
# Aseprite — buy from https://www.aseprite.org/ or compile from source
# Libresprite — free fork
# Piskel — free in-browser: https://www.piskelapp.com/
```

Aseprite is the industry standard for pixel art animation. The onion skinning, frame management, and export tools are worth the $20. But Libresprite/Piskel work for learning.

### Canvas Setup (for code chapters)

```bash
mkdir ember-quest && cd ember-quest
npm init -y
npm install -D vite typescript
```

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Ember Quest</title>
  <style>
    * { margin: 0; }
    body { background: #1a1a2e; overflow: hidden; }
    canvas {
      display: block;
      image-rendering: pixelated;  /* CRITICAL for pixel art */
      image-rendering: crisp-edges;
    }
  </style>
</head>
<body>
  <canvas id="game"></canvas>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

The `image-rendering: pixelated` CSS is critical — without it, the browser anti-aliases your pixel art into blurry mush when scaled up.

### Verify: Draw a Sprite Frame

```typescript
// src/main.ts
const canvas = document.getElementById('game') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;

canvas.width = 256;
canvas.height = 256;
canvas.style.width = '512px';   // 2x scale
canvas.style.height = '512px';

// Draw Ember as a simple placeholder (we'll replace with real art)
ctx.fillStyle = '#ff6600';
ctx.fillRect(12, 8, 8, 8);    // head
ctx.fillStyle = '#ff3300';
ctx.fillRect(10, 16, 12, 12); // body
ctx.fillRect(10, 28, 4, 4);   // left leg
ctx.fillRect(18, 28, 4, 4);   // right leg

// If you see an orange blob at 2x scale with crisp pixels — you're ready
```

```bash
npx vite
```

---

## Art vs. Code: The Two Tracks

This series alternates between art and code:

| Chapter Type | What You Do |
|---|---|
| **Art chapters** (1-5, 6-15) | Open Aseprite, draw pixels, learn animation principles |
| **Code chapters** (16-20) | Open your editor, implement the sprite engine |
| **Both** | Every art chapter includes a "test it in-game" section |

You don't need to be a great artist. You need to understand:
- Why 6 frames feels snappy and 12 feels smooth
- Why anticipation makes attacks feel powerful
- Why silhouette matters more than detail at 32×32
- How to export and render efficiently

The art gets better with practice. The principles are what this series teaches.

---

[Next: Chapter 1 — Your First Character (32×32) →](chapter-01-first-character.md)
