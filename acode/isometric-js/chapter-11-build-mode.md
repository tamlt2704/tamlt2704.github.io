# Chapter 11: Build Mode

[← Chapter 10: Animated Tiles](chapter-10-animated-tiles.md) | [Chapter 12: Performance →](chapter-12-performance.md)

---

## The Task

Riku sends a mockup: a toolbar at the bottom with building icons. Click one, then click the map to place it. "Like every city builder ever. Ghost preview, green if valid, red if blocked. Drag to place roads."

You've got mouse picking, tile rendering, depth sorting. Now you need a *mode* — a state machine that changes how clicks behave depending on what the player is doing.

## The Build Mode State Machine

Build mode has three states:

```
┌──────────┐   click toolbar   ┌───────────┐   click valid tile   ┌──────────┐
│  IDLE    │ ─────────────────→ │ PREVIEWING│ ────────────────────→ │  PLACED  │
│          │ ←───────────────── │           │ ←──────────────────── │          │
└──────────┘   Escape / right   └───────────┘   animation done      └──────────┘
```

```typescript
// src/game/build-mode.ts
export enum BuildState {
  Idle = 'idle',
  Previewing = 'previewing',
  Placing = 'placing',
}

export interface BuildingDef {
  id: string;
  name: string;
  width: number;   // Grid cells wide
  height: number;  // Grid cells tall
  sprite: HTMLImageElement;
  spriteHeight: number;
  cost: number;
}

export class BuildMode {
  state: BuildState = BuildState.Idle;
  selectedBuilding: BuildingDef | null = null;
  previewX = 0;
  previewY = 0;
  isValidPlacement = false;

  select(building: BuildingDef) {
    this.selectedBuilding = building;
    this.state = BuildState.Previewing;
  }

  cancel() {
    this.selectedBuilding = null;
    this.state = BuildState.Idle;
  }

  updatePreview(gridX: number, gridY: number, grid: GameGrid) {
    if (this.state !== BuildState.Previewing) return;

    this.previewX = gridX;
    this.previewY = gridY;
    this.isValidPlacement = this.checkPlacement(gridX, gridY, grid);
  }

  private checkPlacement(gridX: number, gridY: number, grid: GameGrid): boolean {
    const def = this.selectedBuilding!;

    // Check all cells the building occupies
    for (let dx = 0; dx < def.width; dx++) {
      for (let dy = 0; dy < def.height; dy++) {
        const cx = gridX + dx;
        const cy = gridY + dy;

        // Out of bounds
        if (cx < 0 || cy < 0 || cx >= grid.width || cy >= grid.height) {
          return false;
        }

        // Cell already occupied
        if (grid.isOccupied(cx, cy)) {
          return false;
        }

        // Can't build on water
        if (grid.getTerrain(cx, cy) === Terrain.Water) {
          return false;
        }
      }
    }

    return true;
  }

  confirmPlacement(grid: GameGrid): boolean {
    if (this.state !== BuildState.Previewing) return false;
    if (!this.isValidPlacement) return false;

    const def = this.selectedBuilding!;

    // Mark cells as occupied
    for (let dx = 0; dx < def.width; dx++) {
      for (let dy = 0; dy < def.height; dy++) {
        grid.setOccupied(this.previewX + dx, this.previewY + dy, def.id);
      }
    }

    return true;
  }
}
```

## Ghost Preview Following the Mouse

The ghost preview is the selected building drawn at half opacity, snapped to the grid cell under the cursor:

```typescript
// src/game/build-renderer.ts
const TILE_W = 64;
const TILE_H = 32;

export function renderBuildPreview(
  ctx: CanvasRenderingContext2D,
  buildMode: BuildMode,
  camera: Camera
) {
  if (buildMode.state !== BuildState.Previewing) return;
  if (!buildMode.selectedBuilding) return;

  const def = buildMode.selectedBuilding;
  const { screenX, screenY } = cartToIso(buildMode.previewX, buildMode.previewY);

  const drawX = screenX - camera.x + worldOffsetX - TILE_W / 2;
  const drawY = screenY - camera.y + worldOffsetY - def.spriteHeight + TILE_H / 2;

  // Tint green or red based on validity
  ctx.save();
  ctx.globalAlpha = 0.6;

  if (buildMode.isValidPlacement) {
    // Green tint: draw normally then overlay green
    ctx.drawImage(def.sprite, drawX, drawY);
    ctx.globalCompositeOperation = 'source-atop';
    ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
    ctx.fillRect(drawX, drawY, def.sprite.width, def.spriteHeight);
  } else {
    // Red tint
    ctx.drawImage(def.sprite, drawX, drawY);
    ctx.globalCompositeOperation = 'source-atop';
    ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
    ctx.fillRect(drawX, drawY, def.sprite.width, def.spriteHeight);
  }

  ctx.restore();

  // Draw grid highlight under the building footprint
  renderFootprintHighlight(ctx, buildMode, camera);
}

function renderFootprintHighlight(
  ctx: CanvasRenderingContext2D,
  buildMode: BuildMode,
  camera: Camera
) {
  const def = buildMode.selectedBuilding!;
  const color = buildMode.isValidPlacement
    ? 'rgba(0, 200, 0, 0.4)'
    : 'rgba(200, 0, 0, 0.4)';

  for (let dx = 0; dx < def.width; dx++) {
    for (let dy = 0; dy < def.height; dy++) {
      const gx = buildMode.previewX + dx;
      const gy = buildMode.previewY + dy;
      const { screenX, screenY } = cartToIso(gx, gy);

      const sx = screenX - camera.x + worldOffsetX;
      const sy = screenY - camera.y + worldOffsetY;

      // Draw diamond highlight
      ctx.beginPath();
      ctx.moveTo(sx, sy - TILE_H / 2);
      ctx.lineTo(sx + TILE_W / 2, sy);
      ctx.lineTo(sx, sy + TILE_H / 2);
      ctx.lineTo(sx - TILE_W / 2, sy);
      ctx.closePath();
      ctx.fillStyle = color;
      ctx.fill();
    }
  }
}
```

## Wiring Up Input Events

The build mode responds to mouse movement, clicks, and keyboard:

```typescript
// src/game/build-input.ts
export function setupBuildInput(
  canvas: HTMLCanvasElement,
  buildMode: BuildMode,
  camera: Camera,
  grid: GameGrid
) {
  canvas.addEventListener('mousemove', (e) => {
    if (buildMode.state !== BuildState.Previewing) return;

    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left + camera.x - worldOffsetX;
    const screenY = e.clientY - rect.top + camera.y - worldOffsetY;

    // Convert screen position to grid coordinates
    const gridPos = isoToCart(screenX, screenY);
    const gx = Math.floor(gridPos.x);
    const gy = Math.floor(gridPos.y);

    buildMode.updatePreview(gx, gy, grid);
  });

  canvas.addEventListener('click', (e) => {
    if (buildMode.state !== BuildState.Previewing) return;

    if (buildMode.isValidPlacement) {
      buildMode.confirmPlacement(grid);
      // Stay in preview mode for rapid placement
      // (player can keep clicking to place more)
    }
  });

  canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    buildMode.cancel();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      buildMode.cancel();
    }
  });
}
```

## Drag to Place Roads

Roads are different — you drag across multiple tiles in one gesture. This needs continuous placement mode:

```typescript
// src/game/road-placer.ts
export class RoadPlacer {
  private isDragging = false;
  private placedThisDrag: Set<string> = new Set();

  startDrag() {
    this.isDragging = true;
    this.placedThisDrag.clear();
  }

  endDrag() {
    this.isDragging = false;
  }

  onTileHover(gridX: number, gridY: number, grid: GameGrid) {
    if (!this.isDragging) return;

    const key = `${gridX},${gridY}`;
    if (this.placedThisDrag.has(key)) return; // Already placed here this drag

    if (!grid.isOccupied(gridX, gridY) && grid.getTerrain(gridX, gridY) !== Terrain.Water) {
      grid.setOccupied(gridX, gridY, 'road');
      this.placedThisDrag.add(key);
    }
  }
}
```

Wire it into the input system:

```typescript
const roadPlacer = new RoadPlacer();

canvas.addEventListener('mousedown', (e) => {
  if (e.button !== 0) return;
  if (buildMode.selectedBuilding?.id !== 'road') return;

  roadPlacer.startDrag();
  // Place on the initial tile too
  roadPlacer.onTileHover(buildMode.previewX, buildMode.previewY, grid);
});

canvas.addEventListener('mousemove', (e) => {
  if (buildMode.selectedBuilding?.id === 'road') {
    roadPlacer.onTileHover(buildMode.previewX, buildMode.previewY, grid);
  }
});

canvas.addEventListener('mouseup', () => {
  roadPlacer.endDrag();
});
```

## Road Auto-Tiling

When you place a road, it should connect to adjacent roads visually. Each road tile checks its neighbors and picks the right sprite:

```typescript
// src/game/road-autotile.ts
export function getRoadSpriteIndex(grid: GameGrid, x: number, y: number): number {
  // Check 4 cardinal neighbors
  const n = grid.isRoad(x, y - 1) ? 1 : 0;
  const e = grid.isRoad(x + 1, y) ? 1 : 0;
  const s = grid.isRoad(x, y + 1) ? 1 : 0;
  const w = grid.isRoad(x - 1, y) ? 1 : 0;

  // 4-bit bitmask → 16 possible road sprites
  return (n << 3) | (e << 2) | (s << 1) | w;
}
```

The road spritesheet has 16 tiles (one for each combination of N/E/S/W connections). Index 0 is isolated, index 15 is a 4-way intersection.

## Cancel and Undo

Right-click or Escape cancels build mode. But what about undoing a misplaced building?

```typescript
// src/game/build-history.ts
interface PlacementAction {
  type: 'place';
  buildingId: string;
  gridX: number;
  gridY: number;
  width: number;
  height: number;
}

export class BuildHistory {
  private actions: PlacementAction[] = [];
  private maxHistory = 50;

  record(action: PlacementAction) {
    this.actions.push(action);
    if (this.actions.length > this.maxHistory) {
      this.actions.shift();
    }
  }

  undo(grid: GameGrid): PlacementAction | null {
    const action = this.actions.pop();
    if (!action) return null;

    // Clear the cells this building occupied
    for (let dx = 0; dx < action.width; dx++) {
      for (let dy = 0; dy < action.height; dy++) {
        grid.clearOccupied(action.gridX + dx, action.gridY + dy);
      }
    }

    return action;
  }
}
```

Bind Ctrl+Z:

```typescript
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'z') {
    e.preventDefault();
    buildHistory.undo(grid);
  }
});
```

## Riku's Reaction

You demo the build mode. Click a house icon, green ghost follows the cursor, click to place. Drag to lay roads. Escape to cancel. Ctrl+Z to undo.

Riku: "This is actually starting to feel like a game. But... I placed 500 buildings and it's running at 12 FPS. We need to talk about performance."

You: "Yeah. 500 `drawImage` calls per frame. Time to bring in the big guns."

## What You Built

- **State machine** — Idle → Previewing → Placed, clean transitions
- **Ghost preview** — semi-transparent building snapped to grid
- **Valid/invalid visualization** — green footprint for valid, red for blocked
- **Placement validation** — bounds checking, occupancy, terrain rules
- **Road dragging** — continuous placement with deduplication
- **Road auto-tiling** — 4-bit bitmask selects correct sprite
- **Undo system** — Ctrl+Z removes last placed building
- **Cancel** — Escape or right-click exits build mode

The player can build. But the renderer can't keep up. Next chapter: making it fast.

---

[← Chapter 10: Animated Tiles](chapter-10-animated-tiles.md) | [Chapter 12: Performance →](chapter-12-performance.md)
