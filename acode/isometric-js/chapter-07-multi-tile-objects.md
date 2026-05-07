# Chapter 7: Multi-Tile Objects

[← Chapter 6: Depth Sorting](chapter-06-depth-sorting.md) | [Chapter 8: Tile Maps →](chapter-08-tile-maps.md)

---

## The Task

Riku's town hall is a 2×2 building. His factory is 3×2. His cathedral is 2×3 and three stories tall. These aren't single-tile sprites anymore — they span multiple grid cells and tower above the ground.

"I drew one big sprite for the town hall. It covers four tiles. Where do I anchor it? How does depth sorting work? And how do I prevent the player from placing another building on top of it?"

Three problems. Let's solve them in order.

## Buildings with Footprints

A multi-tile building occupies a rectangular area on the grid. Define it with a footprint:

```typescript
// src/game/buildings.ts
interface BuildingDef {
  id: string;
  name: string;
  sprite: string;           // Sprite key or atlas ID
  footprint: {
    width: number;          // Tiles wide (along x-axis)
    height: number;         // Tiles deep (along y-axis)
  };
  spriteWidth: number;      // Pixel width of the full sprite
  spriteHeight: number;     // Pixel height of the full sprite
}

const BUILDINGS: Record<string, BuildingDef> = {
  townHall: {
    id: 'townHall',
    name: 'Town Hall',
    sprite: 'building_townhall',
    footprint: { width: 2, height: 2 },
    spriteWidth: 128,
    spriteHeight: 128,
  },
  factory: {
    id: 'factory',
    name: 'Factory',
    sprite: 'building_factory',
    footprint: { width: 3, height: 2 },
    spriteWidth: 192,
    spriteHeight: 160,
  },
  house: {
    id: 'house',
    name: 'House',
    sprite: 'building_house',
    footprint: { width: 1, height: 1 },
    spriteWidth: 64,
    spriteHeight: 80,
  },
};
```

## The Anchor Tile

Every multi-tile building has one tile that "owns" it — the **anchor**. This is the tile used for:
- Placement position (where the player clicks)
- Depth sorting (determines draw order)
- Data storage (which grid cell references the building)

Convention: the anchor is the **top-left** tile of the footprint (minimum x, minimum y):

```
Footprint of a 2×2 building:

  Grid:
    (3,4) (4,4)
    (3,5) (4,5)

  Anchor = (3, 4) — top-left corner

  Isometric view:
         ◇         ← (3,4) anchor
       ◇   ◇
     ◇   ◇   ◇
       ◇   ◇
         ◇         ← (4,5) bottom-right
```

But for depth sorting, the anchor should be the tile closest to the viewer — the **bottom-right** corner of the footprint. Why? Because the building should be drawn when we reach its frontmost tile:

```typescript
interface PlacedBuilding {
  def: BuildingDef;
  anchorX: number;    // Top-left grid position
  anchorY: number;
  // Sort position = bottom-right of footprint
  get sortX(): number { return this.anchorX + this.def.footprint.width - 1; }
  get sortY(): number { return this.anchorY + this.def.footprint.height - 1; }
}
```

Actually, the simplest approach: draw the building when the diagonal loop reaches the **bottom-right** tile of its footprint. This ensures everything behind it has already been drawn.

## Drawing Multi-Tile Sprites

A 2×2 building's sprite is wider and taller than a single tile. The sprite covers the entire footprint area:

```typescript
function drawBuilding(
  ctx: CanvasRenderingContext2D,
  building: PlacedBuilding,
  offsetX: number,
  offsetY: number
) {
  const def = building.def;

  // The draw position is based on the anchor tile (top-left of footprint)
  // But we need to figure out where the sprite's top-left pixel goes
  const { screenX, screenY } = cartToIso(building.anchorX, building.anchorY);

  // For a multi-tile footprint, the sprite is wider:
  // Width covers footprint.width tiles going right + footprint.height tiles going left
  // The anchor's iso position is the top of the diamond cluster

  // Calculate the bounding box of the footprint in screen space
  const topIso = cartToIso(building.anchorX, building.anchorY);
  const rightIso = cartToIso(building.anchorX + def.footprint.width - 1, building.anchorY);
  const leftIso = cartToIso(building.anchorX, building.anchorY + def.footprint.height - 1);
  const bottomIso = cartToIso(
    building.anchorX + def.footprint.width - 1,
    building.anchorY + def.footprint.height - 1
  );

  // The sprite's top-center aligns with the top of the footprint diamond
  const spriteCenterX = topIso.screenX + offsetX;
  const footprintTopY = topIso.screenY + offsetY - TILE_H / 2;

  // Extra height above the footprint
  const footprintPixelH = (bottomIso.screenY - topIso.screenY) + TILE_H;
  const extraH = def.spriteHeight - footprintPixelH;

  const drawX = spriteCenterX - def.spriteWidth / 2;
  const drawY = footprintTopY - extraH;

  const sprite = sprites.get(def.sprite);
  if (sprite) {
    ctx.drawImage(sprite, drawX, drawY, def.spriteWidth, def.spriteHeight);
  }
}
```

A simpler approach that works for most cases — align the sprite's bottom-center with the footprint's bottom vertex:

```typescript
function drawBuildingSimple(
  ctx: CanvasRenderingContext2D,
  building: PlacedBuilding,
  offsetX: number,
  offsetY: number
) {
  const def = building.def;

  // Bottom-right tile of footprint determines the "front" of the building
  const frontX = building.anchorX + def.footprint.width - 1;
  const frontY = building.anchorY + def.footprint.height - 1;
  const { screenX, screenY } = cartToIso(frontX, frontY);

  // Sprite bottom-center aligns with the bottom vertex of the front tile
  const drawX = screenX + offsetX - def.spriteWidth / 2;
  const drawY = screenY + offsetY + TILE_H / 2 - def.spriteHeight;

  const sprite = sprites.get(def.sprite);
  if (sprite) {
    ctx.drawImage(sprite, drawX, drawY, def.spriteWidth, def.spriteHeight);
  }
}
```

## Integrating with Depth Sorting

Draw the building when the diagonal loop reaches its sort position (bottom-right tile):

```typescript
// Build a lookup: which buildings need to draw at which sort position?
function buildRenderMap(buildings: PlacedBuilding[]): Map<string, PlacedBuilding> {
  const map = new Map<string, PlacedBuilding>();
  for (const b of buildings) {
    const sortX = b.anchorX + b.def.footprint.width - 1;
    const sortY = b.anchorY + b.def.footprint.height - 1;
    map.set(`${sortX},${sortY}`, b);
  }
  return map;
}

function renderWorld(grid: Grid, buildings: PlacedBuilding[]) {
  const renderMap = buildRenderMap(buildings);

  for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= grid.width || y >= grid.height) continue;

      // Draw ground tile
      drawGroundTile(x, y);

      // Draw building if this is its sort position
      const building = renderMap.get(`${x},${y}`);
      if (building) {
        drawBuildingSimple(ctx, building, worldOffsetX, worldOffsetY);
      }
    }
  }
}
```

## Collision and Placement Checking

Before placing a building, check that all tiles in its footprint are free:

```typescript
// src/game/placement.ts
export class PlacementSystem {
  private occupied: boolean[][];

  constructor(gridWidth: number, gridHeight: number) {
    this.occupied = Array.from({ length: gridWidth }, () =>
      Array(gridHeight).fill(false)
    );
  }

  canPlace(anchorX: number, anchorY: number, def: BuildingDef, grid: Grid): boolean {
    for (let dx = 0; dx < def.footprint.width; dx++) {
      for (let dy = 0; dy < def.footprint.height; dy++) {
        const tx = anchorX + dx;
        const ty = anchorY + dy;

        // Out of bounds?
        if (tx < 0 || tx >= grid.width || ty < 0 || ty >= grid.height) {
          return false;
        }

        // Already occupied?
        if (this.occupied[tx][ty]) {
          return false;
        }

        // On water or other unbuildable terrain?
        const tile = grid.getTile(tx, ty);
        if (tile === 'water') {
          return false;
        }
      }
    }
    return true;
  }

  place(anchorX: number, anchorY: number, def: BuildingDef) {
    for (let dx = 0; dx < def.footprint.width; dx++) {
      for (let dy = 0; dy < def.footprint.height; dy++) {
        this.occupied[anchorX + dx][anchorY + dy] = true;
      }
    }
  }

  remove(anchorX: number, anchorY: number, def: BuildingDef) {
    for (let dx = 0; dx < def.footprint.width; dx++) {
      for (let dy = 0; dy < def.footprint.height; dy++) {
        this.occupied[anchorX + dx][anchorY + dy] = false;
      }
    }
  }
}
```

## Ghost Preview

Show the building footprint before placing — green if valid, red if blocked:

```typescript
function drawGhostFootprint(
  ctx: CanvasRenderingContext2D,
  anchorX: number,
  anchorY: number,
  def: BuildingDef,
  canPlace: boolean,
  offsetX: number,
  offsetY: number
) {
  const color = canPlace
    ? 'rgba(0, 255, 100, 0.3)'
    : 'rgba(255, 50, 50, 0.3)';
  const stroke = canPlace
    ? 'rgba(0, 255, 100, 0.8)'
    : 'rgba(255, 50, 50, 0.8)';

  for (let dx = 0; dx < def.footprint.width; dx++) {
    for (let dy = 0; dy < def.footprint.height; dy++) {
      const { screenX, screenY } = cartToIso(anchorX + dx, anchorY + dy);
      const cx = screenX + offsetX;
      const cy = screenY + offsetY;

      ctx.beginPath();
      ctx.moveTo(cx, cy - TILE_H / 2);
      ctx.lineTo(cx + TILE_W / 2, cy);
      ctx.lineTo(cx, cy + TILE_H / 2);
      ctx.lineTo(cx - TILE_W / 2, cy);
      ctx.closePath();

      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }
}
```

## Tall Sprites That Extend Above

Riku's cathedral is 2×3 tiles wide and 4 tiles tall visually. The sprite is 192×256 pixels. Most of that height is above the footprint:

```
     ┌─────────┐
     │  ⛪     │  ← Sprite extends far above
     │  │ │    │
     │  │ │    │     spriteHeight = 256
     │  ├─┤    │
     │ ╱◇◇◇╲  │  ← Footprint starts here
     │╱◇◇◇◇◇╲ │     footprint = 2×3
     │╲◇◇◇◇◇╱ │     footprintPixelH ≈ 80
     │ ╲◇◇◇╱  │
     └─────────┘     extraH = 256 - 80 = 176
```

The draw function handles this automatically — the sprite is positioned so its bottom aligns with the footprint's bottom vertex, and the rest extends upward.

## The Building Manager

```typescript
// src/game/buildings.ts
export class BuildingManager {
  buildings: PlacedBuilding[] = [];
  private placement: PlacementSystem;

  constructor(gridWidth: number, gridHeight: number) {
    this.placement = new PlacementSystem(gridWidth, gridHeight);
  }

  tryPlace(anchorX: number, anchorY: number, defId: string, grid: Grid): boolean {
    const def = BUILDINGS[defId];
    if (!def) return false;

    if (!this.placement.canPlace(anchorX, anchorY, def, grid)) {
      return false;
    }

    this.placement.place(anchorX, anchorY, def);
    this.buildings.push({
      def,
      anchorX,
      anchorY,
      get sortX() { return this.anchorX + this.def.footprint.width - 1; },
      get sortY() { return this.anchorY + this.def.footprint.height - 1; },
    });

    return true;
  }

  removeAt(gridX: number, gridY: number): boolean {
    const idx = this.buildings.findIndex(b => {
      return (
        gridX >= b.anchorX &&
        gridX < b.anchorX + b.def.footprint.width &&
        gridY >= b.anchorY &&
        gridY < b.anchorY + b.def.footprint.height
      );
    });

    if (idx === -1) return false;

    const building = this.buildings[idx];
    this.placement.remove(building.anchorX, building.anchorY, building.def);
    this.buildings.splice(idx, 1);
    return true;
  }

  getBuildingAt(gridX: number, gridY: number): PlacedBuilding | null {
    return this.buildings.find(b => {
      return (
        gridX >= b.anchorX &&
        gridX < b.anchorX + b.def.footprint.width &&
        gridY >= b.anchorY &&
        gridY < b.anchorY + b.def.footprint.height
      );
    }) ?? null;
  }
}
```

## Putting It Together

```typescript
const buildingManager = new BuildingManager(grid.width, grid.height);

// Place some buildings
buildingManager.tryPlace(2, 2, 'townHall', grid);
buildingManager.tryPlace(5, 3, 'factory', grid);
buildingManager.tryPlace(1, 6, 'house', grid);
buildingManager.tryPlace(2, 6, 'house', grid);  // Adjacent house

// In render:
function render() {
  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  const renderMap = buildRenderMap(buildingManager.buildings);

  for (let sum = 0; sum < grid.width + grid.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= grid.width || y >= grid.height) continue;

      drawGroundTile(x, y);

      const building = renderMap.get(`${x},${y}`);
      if (building) {
        drawBuildingSimple(ctx, building, worldOffsetX, worldOffsetY);
      }
    }
  }

  // Ghost preview if in build mode
  if (buildMode && input.hoveredTile) {
    const def = BUILDINGS[selectedBuilding];
    const valid = placement.canPlace(input.hoveredTile.x, input.hoveredTile.y, def, grid);
    drawGhostFootprint(ctx, input.hoveredTile.x, input.hoveredTile.y, def, valid, worldOffsetX, worldOffsetY);
  }

  ctx.restore();
}
```

## Riku's Reaction

The town hall sits on its 2×2 footprint. The factory spans 3×2. Depth sorting works — buildings behind render behind. The ghost preview shows green when placement is valid, red when blocked.

Riku: "I don't want to hard-code every building position. I want to design the map in Tiled and export it."

You: "Tiled exports JSON. We can parse layers — ground tiles, object placements, decorations. All from a file."

## What You Built

- **Building footprints** — width × height in grid cells
- **Anchor tile** — top-left of footprint for placement, bottom-right for sort order
- **Multi-tile sprite drawing** — align sprite bottom with footprint's front vertex
- **Collision checking** — verify all footprint tiles are free before placing
- **Ghost preview** — green/red overlay showing valid/invalid placement
- **Building manager** — place, remove, and query buildings

Multi-tile objects render correctly and don't overlap. Next: loading entire maps from Tiled instead of building them in code.

---

[← Chapter 6: Depth Sorting](chapter-06-depth-sorting.md) | [Chapter 8: Tile Maps →](chapter-08-tile-maps.md)
