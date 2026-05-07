# Chapter 7: Wave Function Collapse

[← Ch 6](chapter-06-caves.md) | [Ch 8 →](chapter-08-lsystems.md)

---

## Juno's Request

> "I need tile-based maps — space station interiors, planet surfaces with paths. Hand-placing tiles doesn't scale. I want to define which tiles can go next to each other, then let the algorithm figure out valid layouts."

---

## The Concept

WFC treats map generation as constraint satisfaction:

```
1. Every cell starts with ALL possible tiles (superposition)
2. Pick the cell with fewest options (lowest entropy)
3. Collapse it: randomly choose one valid tile
4. Propagate: remove invalid options from neighbors
5. Repeat until done (or contradiction → retry)
```

---

## Defining Tiles and Adjacency

```typescript
import Alea from 'alea';

interface Tile {
  id: number; name: string; color: [number,number,number]; weight: number;
  validNeighbors: { up: number[]; down: number[]; left: number[]; right: number[] };
}

const TILES: Tile[] = [
  { id: 0, name: 'grass', color: [34,139,34], weight: 3,
    validNeighbors: { up:[0,1], down:[0,1], left:[0,1], right:[0,1] } },
  { id: 1, name: 'path-edge', color: [139,119,80], weight: 2,
    validNeighbors: { up:[0,1,2], down:[0,1,2], left:[0,1,2], right:[0,1,2] } },
  { id: 2, name: 'path', color: [180,160,100], weight: 1,
    validNeighbors: { up:[1,2], down:[1,2], left:[1,2], right:[1,2] } },
  { id: 3, name: 'water', color: [30,80,140], weight: 2,
    validNeighbors: { up:[3,4], down:[3,4], left:[3,4], right:[3,4] } },
  { id: 4, name: 'shore', color: [140,160,100], weight: 1,
    validNeighbors: { up:[0,3,4], down:[0,3,4], left:[0,3,4], right:[0,3,4] } },
];
```

---

## The WFC Algorithm

```typescript
type Cell = Set<number>;

function initGrid(w: number, h: number, tileCount: number): Cell[] {
  const all = new Set(Array.from({length: tileCount}, (_, i) => i));
  return Array.from({length: w * h}, () => new Set(all));
}

function findLowestEntropy(cells: Cell[], rng: () => number): number {
  let min = Infinity, candidates: number[] = [];
  for (let i = 0; i < cells.length; i++) {
    if (cells[i].size <= 1) continue;
    if (cells[i].size < min) { min = cells[i].size; candidates = [i]; }
    else if (cells[i].size === min) candidates.push(i);
  }
  return candidates.length === 0 ? -1 : candidates[Math.floor(rng() * candidates.length)];
}

function collapse(cell: Cell, tiles: Tile[], rng: () => number): void {
  let total = 0;
  for (const id of cell) total += tiles[id].weight;
  let roll = rng() * total;
  for (const id of cell) {
    roll -= tiles[id].weight;
    if (roll <= 0) { cell.clear(); cell.add(id); return; }
  }
  const first = cell.values().next().value!;
  cell.clear(); cell.add(first);
}

function propagate(cells: Cell[], idx: number, w: number, h: number, tiles: Tile[]): boolean {
  const stack = [idx];
  const dirs: [number,number,keyof Tile['validNeighbors']][] = [[0,-1,'up'],[0,1,'down'],[-1,0,'left'],[1,0,'right']];

  while (stack.length > 0) {
    const i = stack.pop()!;
    const x = i % w, y = Math.floor(i / w);

    for (const [dx, dy, dir] of dirs) {
      const nx = x+dx, ny = y+dy;
      if (nx < 0 || nx >= w || ny < 0 || ny >= h) continue;
      const ni = ny * w + nx;
      const prev = cells[ni].size;

      const valid = new Set<number>();
      for (const tid of cells[i])
        for (const vid of tiles[tid].validNeighbors[dir]) valid.add(vid);

      for (const tid of cells[ni]) if (!valid.has(tid)) cells[ni].delete(tid);
      if (cells[ni].size === 0) return false;
      if (cells[ni].size < prev) stack.push(ni);
    }
  }
  return true;
}
```

---

## Running WFC

```typescript
function runWFC(w: number, h: number, tiles: Tile[], seed: string | number, maxAttempts = 10): number[] | null {
  const rng = Alea(seed);
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const cells = initGrid(w, h, tiles.length);
    let success = true;
    while (true) {
      const idx = findLowestEntropy(cells, rng);
      if (idx === -1) break;
      collapse(cells[idx], tiles, rng);
      if (!propagate(cells, idx, w, h, tiles)) { success = false; break; }
    }
    if (success) return cells.map(c => c.values().next().value!);
  }
  return null;
}
```

---

## Rendering

```typescript
function renderWFC(result: number[], w: number, h: number, tiles: Tile[], tileSize = 8): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = w * tileSize; canvas.height = h * tileSize;
  const ctx = canvas.getContext('2d')!;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const [r,g,b] = tiles[result[y*w+x]].color;
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(x*tileSize, y*tileSize, tileSize, tileSize);
    }
  }
  return canvas;
}
```

---

## Visual Result

```
WFC output (paths connect, water has shores, no invalid adjacencies):
┌────────────────────────────────────────┐
│████████████████████████████████████████│
│████████░░░░████████████████████████████│
│██████░░▒▒▒▒░░████████████▓▓▓▓████████│
│██████░░▒▒▒▒░░██████████▓▓░░░░▓▓██████│
│████████░░▒▒░░░░░░░░████▓▓░░░░▓▓██████│
│████████████░░▒▒▒▒░░████▓▓▓▓▓▓████████│
│████████████████████████████████████████│
└────────────────────────────────────────┘
```

---

## Handling Contradictions

WFC can fail when propagation eliminates all options. Strategies:
1. **Retry** with different random choices (usually works in 3-5 attempts)
2. **Backtracking** — undo last collapse, try different tile
3. **Relaxed rules** — add wildcard tile connecting to everything

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| Tile weights | Frequency of each tile | "Grass=3, path=1 → mostly grass" |
| Grid size | Map dimensions | "20×20 for rooms, 50×50 for overworld" |
| Max attempts | Retry budget | "5-10. If 10 fails, rules are too tight" |

---

## Exercises

1. **Space station tileset:** Define tiles for corridor, room-floor, wall, door. Set adjacency so corridors connect rooms through doors. Generate a 15×15 layout.

2. **Weighted biomes:** Modify tile weights by y-position — ice tiles preferred at top, desert at bottom.

3. **Animated generation:** Render after each collapse step. Uncollapsed cells show as gray (darker = fewer options).

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Superposition | Each cell starts with all possible tiles |
| Entropy | Fewer options = lower entropy = collapse next |
| Collapse | Pick one tile (weighted random) |
| Propagation | Remove invalid options from neighbors recursively |
| Contradiction | Zero valid options → backtrack or retry |
| Weights | Higher weight = tile appears more often |

---

[← Ch 6](chapter-06-caves.md) | [Ch 8 →](chapter-08-lsystems.md)
