# Procedural Game Assets: A No-Artist Survival Story

You're building a game. You can't draw. You can't afford an artist. You have code.

**The realization:** some of the most iconic games — Minecraft, Spelunky, Dwarf Fortress, No Man's Sky, Dead Cells — generate their worlds, textures, and even characters with algorithms. Not because they couldn't hire artists, but because procedural generation creates infinite variety from finite rules.

You're making **Drift** — a roguelike space exploration game. Every run is different. Different planets. Different terrain. Different creatures. Different color palettes. You need hundreds of unique assets, and you need them generated at runtime.

Your friend **Juno** (a game designer) lays out the scope:

> "Each planet needs unique terrain — some rocky, some organic, some crystalline. Each has creatures that look like they belong there. The color palette shifts per biome. The UI elements match. And it all needs to feel cohesive, not random noise."

She pauses:

> "Oh, and we need it to run at 60fps. No pre-rendered assets. Everything generated on the fly from a seed. Same seed = same world. Different seed = different world. Deterministic randomness."

You open your editor. Time to make the computer draw for you.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Game Dev (can't draw) | "Math is my paintbrush." |
| **Juno** | Game Designer | "Random isn't interesting. Controlled chaos is." |
| **The Noise Function** | Your best friend | Turns numbers into organic-looking patterns. |
| **The Seed** | Determinism | Same input = same output. Always. |
| **The Uncanny Valley** | That one bug | Generated creature looks almost right... but wrong enough to be creepy. |
| **Pure Random** | The enemy | `Math.random()` makes garbage. Noise makes worlds. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **HTML5 Canvas** | Pixel-level rendering |
| **TypeScript** | Type-safe generation code |
| **Simplex/Perlin Noise** | Organic randomness (terrain, textures) |
| **Wave Function Collapse** | Tile-based generation (maps, dungeons) |
| **L-Systems** | Plant/tree generation (branching structures) |
| **Cellular Automata** | Cave systems, organic shapes |
| **PRNG (seeded)** | Deterministic randomness |
| **OffscreenCanvas** | Generate assets without blocking the main thread |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 The game needs a new type of asset (terrain, creature, item)
   │
   ▼
  🤔 You learn the algorithm that generates it
   │
   ▼
  ⌨️  You implement it
   │
   ▼
  💥 It looks too random, too uniform, or too slow
   │
   ▼
  🧠 You tune the parameters until it looks intentional
   │
   ▼
  📋 Next asset type
```

No concept shows up before you need it. You won't hear about Perlin noise until flat random looks terrible. You won't touch Wave Function Collapse until hand-placing tiles doesn't scale. You won't learn L-systems until you need trees that look like trees.

The need comes first. The algorithm follows.

---

## The Roadmap

### Part 1: Foundations — "Noise, Not Random"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Asset                              │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Generate a starfield background"      │ Seeded PRNG, determinism, pixel manipulation
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Terrain that looks organic"           │ Perlin/Simplex noise — 1D, 2D, octaves, frequency
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Planet surface textures"              │ Noise → color mapping, thresholds, biomes
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Heightmaps and contour lines"         │ 2D noise as elevation, gradient mapping, erosion
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Color palettes that feel cohesive"    │ Procedural color — HSL manipulation, harmony rules, seeded palettes
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Shapes & Structures — "Build Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Asset                              │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Cave systems and dungeons"            │ Cellular automata — rules, iterations, connectivity
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Tile maps that make sense"            │ Wave Function Collapse — constraints, propagation, backtracking
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Trees, plants, coral"                 │ L-Systems — grammars, recursion, branching
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Rocks, crystals, asteroids"           │ Polygon generation — convex hulls, subdivision, Voronoi
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Space stations and buildings"         │ Grammar-based generation — rooms, corridors, modular pieces
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Creatures & Characters — "Grow Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Asset                              │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Alien creatures from a seed"          │ Body plan generation — symmetry, limbs, proportions
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Pixel art sprites (no drawing)"       │ Procedural pixel art — mirroring, noise masks, outlines
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Faces, icons, emblems"                │ Composable parts — eyes, mouths, accessories, layering
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Procedural animation"                 │ Wiggle, bounce, sway — math-driven motion without frames
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Weapons, items, loot"                 │ Modular item generation — blade + hilt + gem, stat-driven visuals
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Ship It"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Generation takes 200ms per asset"     │ Performance — caching, OffscreenCanvas, Web Workers
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Export as sprite sheets / PNG"        │ Asset pipeline — render to texture, atlas packing, export
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Make it tweakable (designer tools)"   │ Parameter UI — sliders, live preview, seed browser
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Combine everything into a world"      │ World generation — biome blending, entity placement, coherence
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ "Infinite variety from one algorithm"  │ The full pipeline — seed → world → assets → game
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Core Insight: Noise, Not Random

```javascript
// BAD: Pure random — looks like TV static
for (let x = 0; x < 256; x++) {
  for (let y = 0; y < 256; y++) {
    const value = Math.random(); // no spatial relationship
    setPixel(x, y, value);
  }
}

// GOOD: Noise — looks like terrain, clouds, organic matter
for (let x = 0; x < 256; x++) {
  for (let y = 0; y < 256; y++) {
    const value = noise(x * 0.02, y * 0.02); // nearby pixels are similar
    setPixel(x, y, value);
  }
}
```

```
Math.random():              Noise:
██░█░██░░█░██░█░            ░░░▒▒▓▓██████▓▓▒▒░░
░█░██░█░█░░█░░██            ░░▒▒▓▓████████▓▓▒▒░
█░░█░░██░█░█░█░█            ░▒▒▓▓██████████▓▓▒░
░██░█░░█░██░░█░░            ▒▒▓▓████████████▓▓▒
(TV static)                 (terrain/clouds)
```

Noise gives you **spatial coherence** — nearby points have similar values. That's what makes generated terrain look like terrain instead of garbage.

---

## Deterministic Randomness: Seeds

```javascript
// Same seed = same world. Every time.
const world1 = generateWorld(seed: 42);    // always the same planet
const world2 = generateWorld(seed: 1337);  // always a different planet

// Share a seed = share a world
// "Check out seed 42, it has a cool crystal biome"
```

A seeded PRNG (pseudorandom number generator) produces the same sequence of "random" numbers given the same starting seed. This means:

- Players can share worlds by sharing seeds
- You can reproduce bugs ("it crashes on seed 7291")
- Saves are tiny (just store the seed + player changes)

---

## What You'll Generate

| Asset | Algorithm | Result |
|---|---|---|
| Starfield | Seeded random + brightness distribution | ✨ Unique star patterns |
| Planet terrain | Multi-octave noise + biome thresholds | 🌍 Mountains, oceans, forests |
| Cave systems | Cellular automata (4-5 rule) | 🕳️ Organic cave networks |
| Tile maps | Wave Function Collapse | 🗺️ Coherent dungeon layouts |
| Trees/plants | L-Systems | 🌳 Branching structures |
| Rocks/crystals | Voronoi + subdivision | 💎 Angular natural shapes |
| Creatures | Symmetry + noise masks | 👾 Alien body plans |
| Pixel sprites | Mirror + noise + outline | 🤖 Spaceship/character silhouettes |
| Color palettes | HSL harmony + seed | 🎨 Cohesive per-biome colors |
| Items/weapons | Modular composition | ⚔️ Blade + hilt + enchantment |
| Animations | Math functions (sin, bounce) | 🔄 Wiggle, sway, pulse |

All from code. No Photoshop. No Aseprite. No artist.

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Procedural Asset Pipeline                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input:  seed (number)                                       │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────┐                                        │
│  │  Seeded PRNG    │  (deterministic random stream)          │
│  └────────┬────────┘                                        │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Noise (Simplex) │  │  Rules (WFC/CA) │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│            │                    │                            │
│            ▼                    ▼                            │
│  ┌──────────────────────────────────────┐                   │
│  │         Generator Functions           │                   │
│  │  terrain() creatures() items()        │                   │
│  └────────────────────┬─────────────────┘                   │
│                        │                                     │
│                        ▼                                     │
│  ┌──────────────────────────────────────┐                   │
│  │         Canvas Renderer               │                   │
│  │  (pixels → ImageData → texture)       │                   │
│  └────────────────────┬─────────────────┘                   │
│                        │                                     │
│                        ▼                                     │
│  Output: game-ready sprites, textures, maps                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### TypeScript + Vite

```bash
mkdir drift-procgen && cd drift-procgen
npm init -y
npm install -D vite typescript
```

### Noise Library

```bash
npm install simplex-noise
```

### Starter Setup

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Drift — Procedural Assets</title>
  <style>
    body { margin: 0; background: #0a0a0f; display: flex; flex-wrap: wrap; gap: 8px; padding: 16px; }
    canvas { image-rendering: pixelated; border: 1px solid #222; }
  </style>
</head>
<body>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

### Verify: Generate Your First Texture

```typescript
// src/main.ts
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea'; // seeded PRNG

// Seeded noise
const prng = Alea(42);  // seed = 42
const noise = createNoise2D(prng);

// Create a canvas
const canvas = document.createElement('canvas');
canvas.width = 128;
canvas.height = 128;
canvas.style.width = '256px';
canvas.style.height = '256px';
document.body.appendChild(canvas);

const ctx = canvas.getContext('2d')!;
const imageData = ctx.createImageData(128, 128);

// Generate terrain texture
for (let x = 0; x < 128; x++) {
  for (let y = 0; y < 128; y++) {
    const value = (noise(x * 0.03, y * 0.03) + 1) / 2; // 0-1
    
    // Map noise to terrain colors
    let r, g, b;
    if (value < 0.35) { r = 30; g = 60; b = 120; }       // deep water
    else if (value < 0.4) { r = 50; g = 100; b = 160; }   // shallow water
    else if (value < 0.45) { r = 194; g = 178; b = 128; } // sand
    else if (value < 0.7) { r = 34; g = 120; b = 50; }    // grass
    else if (value < 0.85) { r = 80; g = 80; b = 70; }    // rock
    else { r = 220; g = 220; b = 230; }                    // snow

    const i = (y * 128 + x) * 4;
    imageData.data[i] = r;
    imageData.data[i + 1] = g;
    imageData.data[i + 2] = b;
    imageData.data[i + 3] = 255;
  }
}

ctx.putImageData(imageData, 0, 0);
```

Install the PRNG:
```bash
npm install alea simplex-noise
```

```bash
npx vite
```

If you see a terrain-like texture with water, grass, and mountains — generated entirely from code — you're ready.

Change the seed from `42` to `1337`. Completely different terrain. Same algorithm.

---

## Who This Is For

- Game devs who can't draw (or don't want to)
- Developers who want infinite variety without infinite assets
- Anyone building roguelikes, sandbox games, or generative art
- People who think math is more fun than Photoshop

---

[Next: Chapter 1 — Seeded Randomness & Starfields →](chapter-01-seeded-starfield.md)
