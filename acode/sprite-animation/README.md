# Sprite Animation & Pixel Art

Your character looks like a melted gummy bear. Its walk cycle looks like a seizure. Learn to draw and animate pixel art sprites from scratch — then implement them in a game engine.

## The Story

You're building **Ember Quest** — a 2D platformer about a fire spirit. You have the engine. You don't have a character. This series teaches both the art (drawing, animation principles) and the code (sprite sheets, state machines, game feel). Half Aseprite, half JavaScript.

## Chapters

### Part 1: Drawing — Make a Character

| # | The Task | What You Learn |
|---|---------|----------------|
| 01 | Draw a single pixel character | Canvas size, silhouette, readability |
| 02 | It looks flat and lifeless | Color — palettes, shading, hue shifting |
| 03 | Give it personality | Shape language — round, sharp, weight |
| 04 | Draw environment tiles | Tilesets — ground, walls, props |
| 05 | Sub-pixel looks blurry | Pixel art rules — no AA, clean lines |

### Part 2: Animation Principles — Make It Move

| # | The Animation | What You Learn |
|---|--------------|----------------|
| 06 | Idle — make it breathe | Subtle motion, 4-6 frames, looping |
| 07 | Walk cycle | Contact, passing, weight, 6-8 frames |
| 08 | Run cycle | Lean, airtime, fewer ground frames |
| 09 | Jump — up and down | Anticipation, apex, squash & stretch |
| 10 | Attack — sword slash | Wind-up, strike, follow-through, smear frames |

### Part 3: Advanced — Make It Feel

| # | The Animation | What You Learn |
|---|--------------|----------------|
| 11 | Hit reaction and death | Impact, freeze frame, knockback |
| 12 | Transitions feel jarring | Blend frames between states |
| 13 | Effects: fire, dust, sparkles | VFX sprites, particles, loops |
| 14 | Enemies need different movement | Slime bounce, bat flutter, boss |
| 15 | Animate the environment | Torches, water, grass, parallax |

### Part 4: Implementation — Put It in the Game

| # | The Task | What You Learn |
|---|---------|----------------|
| 16 | Export the sprite sheet | Packing, atlas, JSON metadata |
| 17 | Render sprites in Canvas/JS | drawImage, clipping, frame timing |
| 18 | State machine: idle→run→jump | Animation states, transitions, priority |
| 19 | Flip, tint, scale at runtime | Mirror, palette swap, flash white |
| 20 | Ship it: full character in-game | Screen shake, hit stop, juice |

## Key Insight

You don't need to be a great artist. You need to understand:
- Why 6 frames feels snappy and 12 feels smooth
- Why anticipation makes attacks feel powerful
- Why silhouette matters more than detail at 32×32
- How to export and render efficiently

## Prerequisites

- **Aseprite** ($20) or **Libresprite** (free) or **Piskel** (browser)
- **Vite + TypeScript** (for code chapters)
- `image-rendering: pixelated` (the most important CSS property for pixel art)
