# Procedural Game Assets

Can't draw. Can't afford an artist. Can code. Generate infinite game assets from algorithms — terrain, creatures, items, sprites, maps — all from a single seed number.

## The Story

You're building **Drift** — a roguelike space exploration game. Every run needs different planets, terrain, creatures, and color palettes. You need hundreds of unique assets generated at runtime. Same seed = same world. Different seed = different world. No Photoshop. No Aseprite. Just math.

## Chapters

### Part 1: Noise, Not Random

| # | The Asset | What You Learn |
|---|----------|----------------|
| 01 | Starfield background | Seeded PRNG, determinism, pixel manipulation |
| 02 | Organic terrain | Perlin/Simplex noise, octaves, frequency |
| 03 | Planet surface textures | Noise → color mapping, biomes |
| 04 | Heightmaps and contours | 2D noise as elevation, erosion |
| 05 | Cohesive color palettes | HSL manipulation, harmony rules |

### Part 2: Shapes & Structures

| # | The Asset | What You Learn |
|---|----------|----------------|
| 06 | Cave systems | Cellular automata, connectivity |
| 07 | Tile maps that make sense | Wave Function Collapse |
| 08 | Trees, plants, coral | L-Systems, branching |
| 09 | Rocks, crystals, asteroids | Voronoi, polygon subdivision |
| 10 | Space stations, buildings | Grammar-based generation |

### Part 3: Creatures & Characters

| # | The Asset | What You Learn |
|---|----------|----------------|
| 11 | Alien creatures from a seed | Body plans, symmetry, limbs |
| 12 | Pixel art sprites (no drawing) | Mirroring, noise masks, outlines |
| 13 | Faces, icons, emblems | Composable parts, layering |
| 14 | Procedural animation | Math-driven motion (sin, bounce) |
| 15 | Weapons, items, loot | Modular composition, stat-driven visuals |

### Part 4: Production

| # | The Problem | What You Learn |
|---|------------|----------------|
| 16 | Generation takes 200ms | Caching, OffscreenCanvas, Web Workers |
| 17 | Export as sprite sheets | Render to texture, atlas packing |
| 18 | Designer tools (tweakable) | Parameter UI, live preview, seed browser |
| 19 | Combine into a world | Biome blending, entity placement |
| 20 | Infinite variety, one algorithm | Full pipeline: seed → world → game |

## Core Insight

`Math.random()` makes TV static. Noise makes terrain. The difference is spatial coherence — nearby points have similar values.

## Prerequisites

```bash
npm install simplex-noise alea
npm install -D vite typescript
```
