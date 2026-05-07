# Chapter 20: Full Pipeline

[← Ch 19](chapter-19-world-generation.md)

---

## Juno's Request

> "We did it. All the pieces work. Now show me the whole thing — one seed, and out comes an entire game world. Planets, terrain, caves, creatures, items, colors, animations. Document the architecture so future-us can extend it."

> "Seed 42. Go."

---

## The Complete Pipeline

```
                         SEED: 42
                           │
                           ▼
                    SEEDED PRNG (Alea)
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      NOISE LAYER     RULES LAYER    GRAMMAR LAYER
      (Simplex 2D)    (CA, WFC)      (L-Systems)
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                  GENERATOR FUNCTIONS
     generatePlanet() generateCave() generateCreature()
                           │
                           ▼
                    COHERENCE LAYER
     Planet type → palette → creature colors → item themes
                           │
                           ▼
                   PERFORMANCE LAYER
          Cache → Workers → LOD → Lazy loading
                           │
                           ▼
                       RENDERER
          Canvas 2D → ImageData → Animation → Screen
```

---

## The Master Generator

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

interface DriftWorld { seed: string; galaxy: Galaxy; currentPlanet: Planet; }
interface Galaxy { planets: PlanetSummary[]; starfield: HTMLCanvasElement; }
interface Planet { type: string; texture: HTMLCanvasElement; palette: Palette; terrain: ChunkManager; }

function generateDriftWorld(seed: string): DriftWorld {
  const galaxy = generateGalaxy(seed);
  const currentPlanet = generateFullPlanet(`${seed}-planet-0`);
  return { seed, galaxy, currentPlanet };
}

function generateGalaxy(seed: string): Galaxy {
  const rng = Alea(seed + '-galaxy');
  const count = 8 + Math.floor(rng() * 12);
  const planets: PlanetSummary[] = [];
  for (let i = 0; i < count; i++) {
    const pSeed = `${seed}-planet-${i}`;
    const pRng = Alea(pSeed);
    const types = ['earth','desert','ice','toxic','crystal','lava'];
    planets.push({
      seed: pSeed, name: generatePlanetName(pSeed),
      type: types[Math.floor(pRng()*types.length)],
      position: { x: rng()*800, y: rng()*600 },
    });
  }
  return { planets, starfield: renderStarfield(generateStarfield(seed+'-stars', 800, 600), 800, 600) };
}

function generateFullPlanet(seed: string): Planet {
  const rng = Alea(seed);
  const types = ['earth','desert','ice','toxic','crystal','lava'];
  const type = types[Math.floor(rng()*types.length)];
  return {
    type,
    texture: generatePlanetTexture(seed+'-tex', 128),
    palette: generatePlanetPalette(seed+'-pal', type),
    terrain: new ChunkManager(seed+'-terrain'),
  };
}
```

---

## Architecture Recap

```
Ch │ System                │ Role
───┼───────────────────────┼─────────────────────────────
01 │ Seeded PRNG           │ Deterministic randomness
02 │ Simplex Noise         │ Organic patterns
03 │ Planet Textures       │ Orbit-view previews
04 │ Heightmaps            │ Elevation + erosion
05 │ Color Palettes        │ Per-planet color identity
06 │ Cellular Automata     │ Cave systems
07 │ Wave Function Collapse│ Tile-based maps
08 │ L-Systems             │ Trees, plants, coral
09 │ Voronoi/Polygons      │ Rocks, crystals, asteroids
10 │ BSP Generation        │ Buildings, stations
11 │ Creature Generation   │ Alien fauna
12 │ Pixel Sprites         │ Ships, characters
13 │ Composable Parts      │ Faces, icons, emblems
14 │ Math Animation        │ Motion without sprite sheets
15 │ Item Generation       │ Weapons, loot
16 │ Performance           │ Caching, workers, LOD
17 │ Export                │ Sprite sheets, atlases
18 │ Designer Tools        │ Parameter UI, presets
19 │ World Generation      │ Combining all systems
20 │ Full Pipeline         │ The complete picture
```

---

## Extending the System

Every new generator follows the same pattern:

```typescript
// 1. Define params  2. Generate  3. Adapt to biome  4. Register in pipeline
function generateNewAsset(seed: string): HTMLCanvasElement {
  const rng = Alea(seed);
  const noise = createNoise2D(rng);
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(W, H);
  // ... fill pixels ...
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

| Extension Ideas | Algorithm | Use Case |
|----------------|-----------|----------|
| Weather | Particles + noise | Rain, snow, sandstorms |
| Music | Markov chains | Per-biome ambient |
| Quests | Graph generation | Procedural missions |
| Nebulae | Layered noise + gradients | Space backgrounds |

---

## The Seed Promise

```typescript
const WORLD_SEED = 'drift-42';
// Share a seed = share a universe
// Bug reports include the seed
// Saves are tiny: { seed, playerX, playerY, inventory, discovered }
```

---

## What We Learned

1. **Noise > Random** — Spatial coherence makes terrain, not garbage
2. **Seeds = Determinism** — Same input, same output. Always.
3. **Parameters = Variety** — One algorithm + different params = infinite assets
4. **Coherence = Design** — Planet type flows to every element
5. **Cache Everything** — Generate once, draw many times
6. **Math = Animation** — Sin, lerp, springs replace sprite sheets
7. **Modular = Scalable** — Combine parts for combinatorial variety
8. **Constraints = Quality** — Rules prevent garbage output

---

## Exercises

1. **New planet type:** Add "mechanical" — grid-aligned noise, angular creatures, cyan/gray items, antenna L-systems with 90° angles.

2. **Seed explorer:** One page showing everything a seed produces: galaxy map, planet thumbnails, creature gallery, item gallery, terrain sample.

3. **Determinism test:** Generate world from seed, serialize key properties, regenerate, assert equality. Proves multiplayer seed sharing works.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Pipeline | Seed → PRNG → Noise/Rules → Generators → Coherence → Cache → Render |
| Seed derivation | `worldSeed + '-subsystem'` for independent streams |
| Coherence | Planet type determines palette, creatures, items |
| Extension | Params → Generate → Adapt → Register |
| The promise | One number → infinite, reproducible, coherent world |

---

## Final Words

You started with `Math.random()` and a blank canvas. Now you have a complete procedural generation pipeline that creates entire game worlds from a single seed. No artist required. Just algorithms, noise, and rules.

Juno approves.

> "Ship it."

---

[← Ch 19](chapter-19-world-generation.md)
