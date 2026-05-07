# Chapter 13: Pathfinding

[← Chapter 12: Performance](chapter-12-performance.md) | [Chapter 14: Camera & Zoom →](chapter-14-camera-zoom.md)

---

## The Task

Riku delivers a character spritesheet: a tiny person with 4-directional walk animations. "They should walk from their house to the shop. Around buildings, not through them."

You need pathfinding. The classic choice for grid-based games: A*.

## A* on the Isometric Grid

A* finds the shortest path between two points on a grid, avoiding obstacles. The algorithm works on the *grid* (cartesian coordinates), not screen coordinates. The isometric projection is only for rendering.

```typescript
// src/engine/pathfinding.ts
interface GridNode {
  x: number;
  y: number;
  g: number;  // Cost from start
  h: number;  // Heuristic (estimated cost to end)
  f: number;  // g + h
  parent: GridNode | null;
}

export function findPath(
  grid: GameGrid,
  startX: number,
  startY: number,
  endX: number,
  endY: number
): { x: number; y: number }[] | null {
  const open: GridNode[] = [];
  const closed: Set<string> = new Set();

  const start: GridNode = {
    x: startX, y: startY,
    g: 0,
    h: heuristic(startX, startY, endX, endY),
    f: 0,
    parent: null,
  };
  start.f = start.g + start.h;
  open.push(start);

  while (open.length > 0) {
    // Find node with lowest f score
    open.sort((a, b) => a.f - b.f);
    const current = open.shift()!;

    // Reached the goal
    if (current.x === endX && current.y === endY) {
      return reconstructPath(current);
    }

    closed.add(`${current.x},${current.y}`);

    // Check all 4 neighbors (or 8 for diagonal movement)
    for (const [dx, dy] of NEIGHBORS) {
      const nx = current.x + dx;
      const ny = current.y + dy;
      const key = `${nx},${ny}`;

      // Skip if out of bounds, blocked, or already visited
      if (!grid.inBounds(nx, ny)) continue;
      if (!grid.isWalkable(nx, ny)) continue;
      if (closed.has(key)) continue;

      const moveCost = (dx !== 0 && dy !== 0) ? 1.414 : 1; // Diagonal costs more
      const g = current.g + moveCost;
      const h = heuristic(nx, ny, endX, endY);

      const existing = open.find(n => n.x === nx && n.y === ny);
      if (existing) {
        if (g < existing.g) {
          existing.g = g;
          existing.f = g + existing.h;
          existing.parent = current;
        }
      } else {
        open.push({ x: nx, y: ny, g, h, f: g + h, parent: current });
      }
    }
  }

  return null; // No path found
}

// 4-directional neighbors
const NEIGHBORS = [
  [0, -1], [1, 0], [0, 1], [-1, 0],
];

// 8-directional (uncomment for diagonal movement)
// const NEIGHBORS = [
//   [0, -1], [1, -1], [1, 0], [1, 1],
//   [0, 1], [-1, 1], [-1, 0], [-1, -1],
// ];

function heuristic(ax: number, ay: number, bx: number, by: number): number {
  // Manhattan distance for 4-dir, Chebyshev for 8-dir
  return Math.abs(ax - bx) + Math.abs(ay - by);
}

function reconstructPath(node: GridNode): { x: number; y: number }[] {
  const path: { x: number; y: number }[] = [];
  let current: GridNode | null = node;

  while (current) {
    path.unshift({ x: current.x, y: current.y });
    current = current.parent;
  }

  return path;
}
```

## Walkable vs Blocked Tiles

The grid needs to know what's walkable:

```typescript
// src/game/game-grid.ts (addition)
export class GameGrid {
  // ... existing code ...

  isWalkable(x: number, y: number): boolean {
    if (!this.inBounds(x, y)) return false;

    const terrain = this.getTerrain(x, y);
    if (terrain === Terrain.Water) return false;
    if (terrain === Terrain.Mountain) return false;

    // Buildings block movement (except roads)
    const occupant = this.getOccupant(x, y);
    if (occupant && occupant !== 'road') return false;

    return true;
  }

  inBounds(x: number, y: number): boolean {
    return x >= 0 && y >= 0 && x < this.width && y < this.height;
  }
}
```

## Converting Grid Path to Screen Movement

A* gives you a list of grid cells. The character needs to move smoothly between them in screen space:

```typescript
// src/game/character.ts
const TILE_W = 64;
const TILE_H = 32;

export class Character {
  gridX: number;
  gridY: number;
  screenX: number;
  screenY: number;

  private path: { x: number; y: number }[] = [];
  private pathIndex = 0;
  private moveProgress = 0;
  private speed = 2; // Tiles per second

  private fromX = 0;
  private fromY = 0;
  private toX = 0;
  private toY = 0;

  constructor(startX: number, startY: number) {
    this.gridX = startX;
    this.gridY = startY;
    const screen = cartToIso(startX, startY);
    this.screenX = screen.screenX;
    this.screenY = screen.screenY;
  }

  setPath(path: { x: number; y: number }[]) {
    if (path.length < 2) return;

    this.path = path;
    this.pathIndex = 0;
    this.startNextSegment();
  }

  private startNextSegment() {
    if (this.pathIndex >= this.path.length - 1) {
      // Arrived at destination
      this.path = [];
      return;
    }

    const from = this.path[this.pathIndex];
    const to = this.path[this.pathIndex + 1];

    const fromScreen = cartToIso(from.x, from.y);
    const toScreen = cartToIso(to.x, to.y);

    this.fromX = fromScreen.screenX;
    this.fromY = fromScreen.screenY;
    this.toX = toScreen.screenX;
    this.toY = toScreen.screenY;
    this.moveProgress = 0;
  }

  update(dt: number) {
    if (this.path.length === 0) return;

    this.moveProgress += this.speed * dt;

    if (this.moveProgress >= 1) {
      // Arrived at next waypoint
      this.pathIndex++;
      this.gridX = this.path[this.pathIndex].x;
      this.gridY = this.path[this.pathIndex].y;

      this.startNextSegment();
    }

    // Interpolate screen position
    const t = Math.min(this.moveProgress, 1);
    this.screenX = this.fromX + (this.toX - this.fromX) * t;
    this.screenY = this.fromY + (this.toY - this.fromY) * t;
  }

  get isMoving(): boolean {
    return this.path.length > 0;
  }

  get depthValue(): number {
    // For depth sorting: use interpolated grid position
    return this.gridX + this.gridY + this.moveProgress;
  }
}
```

## Animating the Character Sprite

The character has directional walk frames. Pick the direction based on movement:

```typescript
// src/game/character-animator.ts
export enum Direction {
  South = 0,  // Down-right in iso
  West = 1,   // Down-left in iso
  North = 2,  // Up-left in iso
  East = 3,   // Up-right in iso
}

export class CharacterAnimator {
  private frameWidth = 32;
  private frameHeight = 48;
  private framesPerDirection = 4;
  private frameDuration = 0.15;
  private elapsed = 0;
  private frame = 0;
  direction: Direction = Direction.South;

  update(dt: number, isMoving: boolean, dx: number, dy: number) {
    if (!isMoving) {
      this.frame = 0; // Idle frame
      this.elapsed = 0;
      return;
    }

    // Determine direction from movement delta
    this.direction = this.getDirection(dx, dy);

    // Advance animation frame
    this.elapsed += dt;
    if (this.elapsed >= this.frameDuration) {
      this.elapsed -= this.frameDuration;
      this.frame = (this.frame + 1) % this.framesPerDirection;
    }
  }

  private getDirection(dx: number, dy: number): Direction {
    // In isometric space:
    // Moving +x on grid = East (up-right on screen)
    // Moving +y on grid = South (down-right on screen)
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? Direction.East : Direction.West;
    }
    return dy > 0 ? Direction.South : Direction.North;
  }

  getSourceRect(): { sx: number; sy: number; sw: number; sh: number } {
    return {
      sx: this.frame * this.frameWidth,
      sy: this.direction * this.frameHeight,
      sw: this.frameWidth,
      sh: this.frameHeight,
    };
  }
}
```

## Multiple NPCs with Staggered Movement

A city needs multiple characters walking around. Spawn them with random destinations:

```typescript
// src/game/npc-manager.ts
export class NPCManager {
  private npcs: Character[] = [];
  private grid: GameGrid;
  private rethinkInterval = 3; // Seconds between new path decisions

  constructor(grid: GameGrid) {
    this.grid = grid;
  }

  spawnNPC(x: number, y: number) {
    const npc = new Character(x, y);
    this.npcs.push(npc);
    this.assignRandomPath(npc);
  }

  update(dt: number) {
    for (const npc of this.npcs) {
      npc.update(dt);

      // When NPC arrives, wait a bit then pick a new destination
      if (!npc.isMoving) {
        npc.idleTime = (npc.idleTime ?? 0) + dt;
        if (npc.idleTime >= this.rethinkInterval * (0.5 + Math.random())) {
          this.assignRandomPath(npc);
          npc.idleTime = 0;
        }
      }
    }
  }

  private assignRandomPath(npc: Character) {
    // Pick a random walkable tile as destination
    const dest = this.findRandomWalkable();
    if (!dest) return;

    const path = findPath(this.grid, npc.gridX, npc.gridY, dest.x, dest.y);
    if (path && path.length > 1) {
      npc.setPath(path);
    }
  }

  private findRandomWalkable(): { x: number; y: number } | null {
    // Try up to 20 random positions
    for (let i = 0; i < 20; i++) {
      const x = Math.floor(Math.random() * this.grid.width);
      const y = Math.floor(Math.random() * this.grid.height);
      if (this.grid.isWalkable(x, y)) {
        return { x, y };
      }
    }
    return null;
  }

  getAll(): Character[] {
    return this.npcs;
  }
}
```

## Rendering NPCs with Depth Sorting

NPCs need to sort with buildings. Use their interpolated grid position for depth:

```typescript
// In the render loop
function renderWorld() {
  // Collect all renderable objects with depth values
  const renderables: Renderable[] = [];

  // Add buildings
  for (const building of buildings) {
    renderables.push({
      depth: building.gridX + building.gridY,
      render: () => renderBuilding(building),
    });
  }

  // Add NPCs
  for (const npc of npcManager.getAll()) {
    renderables.push({
      depth: npc.depthValue,
      render: () => renderCharacter(npc),
    });
  }

  // Sort by depth and render
  renderables.sort((a, b) => a.depth - b.depth);
  for (const r of renderables) {
    r.render();
  }
}
```

## Performance: Caching Paths

A* is expensive. Don't recalculate every frame:

```typescript
// Only recalculate when the grid changes
let pathCacheVersion = 0;

function onBuildingPlaced() {
  pathCacheVersion++;
  // NPCs with invalid paths will recalculate on next update
}

// In NPC update: if path passes through a now-blocked tile, recalculate
function validatePath(npc: Character, grid: GameGrid): boolean {
  for (const node of npc.remainingPath) {
    if (!grid.isWalkable(node.x, node.y)) return false;
  }
  return true;
}
```

## Riku's Reaction

Little people wander the streets, walking around buildings, following roads. The city feels alive.

Riku: "Love it. But I need to zoom in to see the detail on my sprites. And zoom out to see the whole city. Can we add zoom?"

You: "Zoom. Scale transforms, anchor point math, and updating the mouse picking. Let's go."

## What You Built

- **A* pathfinding** — shortest path on a grid with obstacles
- **Walkability rules** — water and buildings block, roads allow
- **Smooth movement** — interpolate between grid cells in screen space
- **Directional animation** — pick sprite row based on movement direction
- **NPC manager** — spawn multiple characters with random wandering
- **Depth integration** — NPCs sort correctly with buildings
- **Path caching** — avoid recalculating every frame

The city has life. Next: letting the player zoom in to appreciate it.

---

[← Chapter 12: Performance](chapter-12-performance.md) | [Chapter 14: Camera & Zoom →](chapter-14-camera-zoom.md)
