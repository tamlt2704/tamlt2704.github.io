# Chapter 19: World Generation

[← Ch 18](chapter-18-designer-tools.md) | [Ch 20 →](chapter-20-full-pipeline.md)

---

## Juno's Request

> "We've built individual generators. Now combine them. When you land on a planet, the biome determines terrain, which determines caves, creatures, and loot colors. Everything coherent. A toxic planet shouldn't have ice creatures carrying desert weapons."

---

## The Coherence Problem

```
Without coherence:                With coherence:
Planet: toxic (green)             Planet: toxic (green)
Terrain: ice caves (blue) ✗       Terrain: acid caves (green) ✓
Creatures: desert (brown) ✗       Creatures: slime (green) ✓
Items: ocean (blue) ✗             Items: poison (green) ✓
```

---

## Seed Derivation Tree

```typescript
import { createNoise2D } from 'simplex-noise';
import Alea from 'alea';

function deriveWorldConfig(worldSeed: string) {
  const rng = Alea(worldSeed);
  const types = ['earth','desert','ice','toxic','crystal','lava'];
  const planetType = types[Math.floor(rng() * types.length)];
  return { worldSeed, planetType,
    biomeSeed: worldSeed + '-biome',
    terrainSeed: worldSeed + '-terrain',
    entitySeed: worldSeed + '-entities',
  };
}
```

```
              worldSeed: "drift-42"
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    "-biome"    "-terrain"  "-entities"
         │          │          │
     planetType  heightmap  creatures/items
     palette     caves      placement
```

---

## Biome Map Generation

```typescript
interface BiomeCell { type: string; elevation: number; moisture: number; }

function generateBiomeMap(seed: string, width: number, height: number): BiomeCell[][] {
  const elevNoise = createNoise2D(Alea(seed + '-elev'));
  const moistNoise = createNoise2D(Alea(seed + '-moist'));
  const map: BiomeCell[][] = [];

  for (let y = 0; y < height; y++) {
    map[y] = [];
    for (let x = 0; x < width; x++) {
      const e = (fbm(elevNoise, x*0.02, y*0.02, 5) + 1) / 2;
      const m = (fbm(moistNoise, x*0.015, y*0.015, 4) + 1) / 2;
      map[y][x] = { type: classifyBiome(e, m), elevation: e, moisture: m };
    }
  }
  return map;
}

function classifyBiome(elev: number, moist: number): string {
  if (elev < 0.3) return 'ocean';
  if (elev > 0.8) return 'mountain';
  if (moist > 0.6) return 'swamp';
  if (moist > 0.4) return 'forest';
  if (moist < 0.3) return 'desert';
  return 'plains';
}
```

---

## Entity Placement

```typescript
interface PlacedEntity { x: number; y: number; type: 'creature'|'item'|'structure'; seed: string; biome: string; }

function placeEntities(biomeMap: BiomeCell[][], worldSeed: string, density = 0.02): PlacedEntity[] {
  const rng = Alea(worldSeed + '-entities');
  const entities: PlacedEntity[] = [];
  const w = biomeMap[0].length, h = biomeMap.length;

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const cell = biomeMap[y][x];
      if (cell.type === 'ocean' || cell.type === 'mountain') continue;
      if (rng() > density) continue;

      const roll = rng();
      const type = roll < 0.4 ? 'creature' : roll < 0.7 ? 'item' : 'structure';
      entities.push({ x, y, type, seed: `${worldSeed}-e-${x}-${y}`, biome: cell.type });
    }
  }
  return entities;
}
```

---

## Biome-Coherent Generation

```typescript
function generateEntityForBiome(entity: PlacedEntity, planetType: string): HTMLCanvasElement {
  if (entity.type === 'creature') {
    const creature = generateCreature(entity.seed);
    adaptCreatureToplanet(creature, planetType, Alea(entity.seed + '-adapt'));
    const biomeColors: Record<string,  [number,number,number]> = {
      forest:[40,120,50], desert:[160,130,60], swamp:[60,90,40], plains:[100,140,60],
    };
    creature.color = biomeColors[entity.biome] || creature.color;
    return renderCreature(creature, 64);
  }
  if (entity.type === 'item') return renderWeapon(generateWeapon(entity.seed));
  return generateStation(entity.seed, 20, 15); // structure
}
```

---

## Chunk-Based World Loading

```typescript
interface Chunk { x: number; y: number; biomeMap: BiomeCell[][]; entities: PlacedEntity[]; terrain: HTMLCanvasElement; }

class ChunkManager {
  private chunks = new Map<string, Chunk>();
  private chunkSize = 32;
  constructor(private worldSeed: string) {}

  getChunk(cx: number, cy: number): Chunk {
    const key = `${cx},${cy}`;
    if (this.chunks.has(key)) return this.chunks.get(key)!;
    const seed = `${this.worldSeed}-chunk-${cx}-${cy}`;
    const biomeMap = generateBiomeMap(seed, this.chunkSize, this.chunkSize);
    const entities = placeEntities(biomeMap, seed);
    const terrain = renderBiomeMap(biomeMap, this.chunkSize, this.chunkSize);
    const chunk = { x: cx, y: cy, biomeMap, entities, terrain };
    this.chunks.set(key, chunk);
    return chunk;
  }

  getVisible(px: number, py: number, radius = 2): Chunk[] {
    const cx = Math.floor(px / this.chunkSize), cy = Math.floor(py / this.chunkSize);
    const chunks: Chunk[] = [];
    for (let dy = -radius; dy <= radius; dy++)
      for (let dx = -radius; dx <= radius; dx++)
        chunks.push(this.getChunk(cx+dx, cy+dy));
    return chunks;
  }

  prune(px: number, py: number, maxDist = 5): void {
    const cx = Math.floor(px / this.chunkSize), cy = Math.floor(py / this.chunkSize);
    for (const [key, chunk] of this.chunks)
      if (Math.abs(chunk.x-cx) + Math.abs(chunk.y-cy) > maxDist) this.chunks.delete(key);
  }
}
```

---

## Visual Result

```
Generated world (seed: "drift-42"):
┌────────────────────────────────────────────────┐
│░░░░░▓▓▓████████████████████████▓▓▓░░░░░░░░░░│
│░░░▓▓███ forest ████ plains ███▓▓░░░░░░░░░░░░│
│░░▓███ 🌳🐛 ████ 🌿🦎 ███▓░░░░░░░░░░░░░│
│░░▓████████████████████████████████▓░░░░░░░░░░│
│░░░▓▓▓████████████████████████▓▓▓░░░░░░░░░░░░│
└────────────────────────────────────────────────┘
  ░=ocean ▓=shore █=land  Entities placed per biome
```

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| Biome noise scale | Region size | "0.01-0.02 for continents" |
| Entity density | Population | "0.02=sparse, 0.05=busy" |
| Chunk size | Granularity | "32 tiles = good balance" |
| View radius | Loaded area | "2-3 chunks each direction" |

**Juno's golden rule:**

> "Player should guess a creature's biome from its color. If you can't tell, coherence is too loose."

---

## Exercises

1. **Biome transitions:** Blend colors over 3-5 tiles at borders using distance interpolation.

2. **Points of interest:** 2-3 structures per chunk with thematically appropriate entities nearby.

3. **World minimap:** 16×16 chunks as colored pixels by dominant biome.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Seed derivation | `worldSeed + '-subsystem'` for independent streams |
| Biome map | Elevation + moisture → classification |
| Entity placement | Density per tile, type weighted by biome |
| Coherence | Biome → creature colors, item themes |
| Chunks | Generate on demand, cache, prune distant |

---

[← Ch 18](chapter-18-designer-tools.md) | [Ch 20 →](chapter-20-full-pipeline.md)
