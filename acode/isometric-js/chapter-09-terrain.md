# Chapter 9: Terrain

[← Chapter 8: Tile Maps](chapter-08-tile-maps.md) | [Chapter 10: Animated Tiles →](chapter-10-animated-tiles.md)

---

## The Task

The map has grass and water. But where they meet, it's a hard edge — one tile is fully grass, the next is fully water. Real isometric games have smooth transitions: grass fading into sand, dirt blending into water, shoreline tiles.

Riku drew 16 transition tiles for grass-to-water edges. "Figure out which one goes where. I don't want to place each edge tile by hand."

This is **auto-tiling** — automatically choosing the right tile based on what's around it.

## Multiple Terrain Types

First, define terrain types and their base tiles:

```typescript
// src/game/terrain.ts
export enum Terrain {
  Grass = 0,
  Water = 1,
  Dirt = 2,
  Sand = 3,
}

// Base tile IDs in the atlas for each terrain
const BASE_TILES: Record<Terrain, number> = {
  [Terrain.Grass]: 0,
  [Terrain.Water]: 4,
  [Terrain.Dirt]: 8,
  [Terrain.Sand]: 12,
};
```

The terrain grid stores terrain types, not tile IDs. The renderer figures out which specific tile to draw:

```typescript
export class TerrainMap {
  width: number;
  height: number;
  data: Terrain[];

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.data = new Array(width * height).fill(Terrain.Grass);
  }

  get(x: number, y: number): Terrain {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
      return Terrain.Grass; // Default for out-of-bounds
    }
    return this.data[y * this.width + x];
  }

  set(x: number, y: number, terrain: Terrain) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      this.data[y * this.width + x] = terrain;
    }
  }
}
```

## Auto-Tiling: The Neighbor Problem

For each tile, look at its four cardinal neighbors (N, E, S, W). If a neighbor is a different terrain type, we need a transition tile for that edge.

```
         N
         │
    W ── ◇ ── E
         │
         S
```

In isometric, "north" is up-left, "east" is up-right, "south" is down-right, "west" is down-left. But for the bitmask, we use grid directions:

```typescript
function getNeighbors(terrain: TerrainMap, x: number, y: number) {
  return {
    north: terrain.get(x, y - 1),
    east: terrain.get(x + 1, y),
    south: terrain.get(x, y + 1),
    west: terrain.get(x - 1, y),
  };
}
```

## The Bitmask Approach

Encode which edges need transitions as a 4-bit number:

```
Bit 0 (1) = North neighbor is different
Bit 1 (2) = East neighbor is different
Bit 2 (4) = South neighbor is different
Bit 3 (8) = West neighbor is different
```

This gives 16 possible combinations (0–15), each mapping to a specific tile in the transition set:

```typescript
function computeBitmask(
  terrain: TerrainMap,
  x: number,
  y: number,
  targetTerrain: Terrain
): number {
  const current = terrain.get(x, y);
  if (current !== targetTerrain) return -1; // Not this terrain type

  let mask = 0;

  if (terrain.get(x, y - 1) !== current) mask |= 1;  // North
  if (terrain.get(x + 1, y) !== current) mask |= 2;  // East
  if (terrain.get(x, y + 1) !== current) mask |= 4;  // South
  if (terrain.get(x - 1, y) !== current) mask |= 8;  // West

  return mask;
}
```

## Mapping Bitmask to Tile IDs

Each terrain type has a set of 16 tiles — one for each bitmask value:

```typescript
// Tile atlas layout for grass transitions:
// Index 0:  mask 0  = no edges (full grass, surrounded by grass)
// Index 1:  mask 1  = north edge (water to the north)
// Index 2:  mask 2  = east edge
// Index 3:  mask 3  = north + east corner
// Index 4:  mask 4  = south edge
// Index 5:  mask 5  = north + south (channel)
// Index 6:  mask 6  = east + south corner
// Index 7:  mask 7  = north + east + south (peninsula)
// Index 8:  mask 8  = west edge
// Index 9:  mask 9  = north + west corner
// Index 10: mask 10 = east + west (channel)
// Index 11: mask 11 = north + east + west
// Index 12: mask 12 = south + west corner
// Index 13: mask 13 = north + south + west
// Index 14: mask 14 = east + south + west
// Index 15: mask 15 = all edges (island)

const GRASS_TRANSITION_START = 16; // First tile ID for grass transitions

function getAutoTileId(terrain: TerrainMap, x: number, y: number): number {
  const current = terrain.get(x, y);
  const mask = computeBitmask(terrain, x, y, current);

  if (mask === 0) {
    // No transitions needed — use base tile
    return BASE_TILES[current];
  }

  // Offset into the transition tileset for this terrain
  const transitionStart = getTransitionStart(current);
  return transitionStart + mask;
}

function getTransitionStart(terrain: Terrain): number {
  switch (terrain) {
    case Terrain.Grass: return 16;
    case Terrain.Water: return 32;
    case Terrain.Dirt: return 48;
    case Terrain.Sand: return 64;
  }
}
```

## 8-Bit Bitmask (Corner Tiles)

The 4-bit approach handles edges but not corners. For smoother transitions, use 8 neighbors (including diagonals):

```
NW  N  NE
 ╲  │  ╱
  W ◇ E
 ╱  │  ╲
SW  S  SE
```

8 bits = 256 possible combinations. That's a lot of tiles. In practice, you only need corners when both adjacent edges are the same terrain:

```typescript
function computeFullBitmask(terrain: TerrainMap, x: number, y: number): number {
  const current = terrain.get(x, y);
  let mask = 0;

  // Cardinals
  const n = terrain.get(x, y - 1) !== current;
  const e = terrain.get(x + 1, y) !== current;
  const s = terrain.get(x, y + 1) !== current;
  const w = terrain.get(x - 1, y) !== current;

  if (n) mask |= 1;
  if (e) mask |= 2;
  if (s) mask |= 4;
  if (w) mask |= 8;

  // Diagonals (only matter if both adjacent cardinals are same terrain)
  if (!n && !e && terrain.get(x + 1, y - 1) !== current) mask |= 16;  // NE
  if (!e && !s && terrain.get(x + 1, y + 1) !== current) mask |= 32;  // SE
  if (!s && !w && terrain.get(x - 1, y + 1) !== current) mask |= 64;  // SW
  if (!w && !n && terrain.get(x - 1, y - 1) !== current) mask |= 128; // NW

  return mask;
}
```

Most games use a lookup table that maps the 256 values to a smaller set of ~47 unique tiles (the "Wang tile" set). Riku doesn't need to draw 256 tiles — many combinations look identical.

```typescript
// Simplified: map 8-bit mask to one of 47 tile variants
const AUTOTILE_LOOKUP: Record<number, number> = {
  0: 0,    // Full tile, no edges
  1: 1,    // North edge only
  2: 2,    // East edge only
  3: 3,    // North + East edges
  // ... (47 entries total)
  255: 46, // Island (all edges + all corners)
};
```

## Rendering with Auto-Tiles

```typescript
function renderTerrain(
  terrain: TerrainMap,
  atlas: TileAtlas,
  offsetX: number,
  offsetY: number
) {
  for (let sum = 0; sum < terrain.width + terrain.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= terrain.width || y >= terrain.height) continue;

      const tileId = getAutoTileId(terrain, x, y);
      const { screenX, screenY } = cartToIso(x, y);

      atlas.drawTile(
        ctx,
        tileId,
        screenX + offsetX - TILE_W / 2,
        screenY + offsetY - TILE_H / 2
      );
    }
  }
}
```

## Caching Auto-Tile Results

Computing bitmasks every frame is wasteful. Cache the resolved tile IDs and only recompute when terrain changes:

```typescript
export class AutoTileCache {
  private cache: number[];
  private width: number;
  private height: number;
  private dirty = true;

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.cache = new Array(width * height).fill(0);
  }

  invalidate() {
    this.dirty = true;
  }

  invalidateAt(x: number, y: number) {
    // Invalidate this tile and all neighbors (their edges changed too)
    this.dirty = true; // Simple approach: recompute all
  }

  resolve(terrain: TerrainMap): number[] {
    if (!this.dirty) return this.cache;

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        this.cache[y * this.width + x] = getAutoTileId(terrain, x, y);
      }
    }

    this.dirty = false;
    return this.cache;
  }
}
```

## Elevation: Drawing Tiles at Different Heights

Riku wants hills. A tile at elevation 1 draws higher on screen than a tile at elevation 0:

```typescript
export class ElevationMap {
  width: number;
  height: number;
  data: number[]; // 0 = ground level, 1 = one step up, etc.

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.data = new Array(width * height).fill(0);
  }

  get(x: number, y: number): number {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) return 0;
    return this.data[y * this.width + x];
  }

  set(x: number, y: number, elevation: number) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      this.data[y * this.width + x] = Math.max(0, elevation);
    }
  }
}
```

Each elevation step shifts the tile up by a fixed amount:

```typescript
const ELEVATION_HEIGHT = 16; // Pixels per elevation level

function drawTileWithElevation(
  x: number,
  y: number,
  tileId: number,
  elevation: number,
  offsetX: number,
  offsetY: number
) {
  const { screenX, screenY } = cartToIso(x, y);

  // Shift up by elevation
  const elevOffset = elevation * ELEVATION_HEIGHT;

  atlas.drawTile(
    ctx,
    tileId,
    screenX + offsetX - TILE_W / 2,
    screenY + offsetY - TILE_H / 2 - elevOffset
  );
}
```

## Elevation Side Faces

When a tile is higher than its neighbor, you see the "cliff" side. Draw a colored rectangle to represent the side face:

```typescript
function drawElevationSides(
  x: number,
  y: number,
  elevation: number,
  terrain: TerrainMap,
  elevationMap: ElevationMap,
  offsetX: number,
  offsetY: number
) {
  const { screenX, screenY } = cartToIso(x, y);
  const cx = screenX + offsetX;
  const cy = screenY + offsetY;
  const elevOffset = elevation * ELEVATION_HEIGHT;

  // Check south neighbor (visible face going down-right)
  const southElev = elevationMap.get(x, y + 1);
  if (elevation > southElev) {
    const diff = (elevation - southElev) * ELEVATION_HEIGHT;
    ctx.beginPath();
    ctx.moveTo(cx, cy + TILE_H / 2 - elevOffset);
    ctx.lineTo(cx + TILE_W / 2, cy - elevOffset);
    ctx.lineTo(cx + TILE_W / 2, cy - elevOffset + diff);
    ctx.lineTo(cx, cy + TILE_H / 2 - elevOffset + diff);
    ctx.closePath();
    ctx.fillStyle = '#5a3d1a'; // Cliff color
    ctx.fill();
    ctx.strokeStyle = '#3d2a10';
    ctx.stroke();
  }

  // Check east neighbor (visible face going down-left)
  const eastElev = elevationMap.get(x + 1, y);
  if (elevation > eastElev) {
    const diff = (elevation - eastElev) * ELEVATION_HEIGHT;
    ctx.beginPath();
    ctx.moveTo(cx, cy + TILE_H / 2 - elevOffset);
    ctx.lineTo(cx - TILE_W / 2, cy - elevOffset);
    ctx.lineTo(cx - TILE_W / 2, cy - elevOffset + diff);
    ctx.lineTo(cx, cy + TILE_H / 2 - elevOffset + diff);
    ctx.closePath();
    ctx.fillStyle = '#4a2d10';
    ctx.fill();
    ctx.strokeStyle = '#3d2a10';
    ctx.stroke();
  }
}
```

## Putting It Together

```typescript
function renderTerrain() {
  const tileIds = autoTileCache.resolve(terrainMap);

  for (let sum = 0; sum < terrainMap.width + terrainMap.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= terrainMap.width || y >= terrainMap.height) continue;

      const elevation = elevationMap.get(x, y);
      const tileId = tileIds[y * terrainMap.width + x];

      // Draw cliff sides first (they're behind the tile surface)
      if (elevation > 0) {
        drawElevationSides(x, y, elevation, terrainMap, elevationMap, worldOffsetX, worldOffsetY);
      }

      // Draw the tile surface
      drawTileWithElevation(x, y, tileId, elevation, worldOffsetX, worldOffsetY);
    }
  }
}
```

## Riku's Reaction

The lake has smooth grass-to-water transitions. The hill rises with visible cliff faces. Auto-tiling picks the right edge tile automatically.

Riku: "The water looks dead. In the reference games, water shimmers. And buildings have smoke coming out of chimneys."

You: "Animated tiles. We cycle through sprite frames on a timer."

Riku: "How hard is that?"

You: "Not hard. But we need to decouple animation speed from the game loop frame rate."

## What You Built

- **Terrain types** — enum-based terrain with base tile mapping
- **4-bit bitmask** — encode edge transitions from cardinal neighbors
- **8-bit bitmask** — include diagonal corners for smoother transitions
- **Auto-tile resolution** — bitmask → tile ID lookup
- **Tile cache** — avoid recomputing bitmasks every frame
- **Elevation** — vertical offset per tile with configurable height
- **Cliff faces** — draw side geometry when elevation changes

Terrain looks natural with smooth transitions. Next: making water shimmer and chimneys smoke with animated tiles.

---

[← Chapter 8: Tile Maps](chapter-08-tile-maps.md) | [Chapter 10: Animated Tiles →](chapter-10-animated-tiles.md)
