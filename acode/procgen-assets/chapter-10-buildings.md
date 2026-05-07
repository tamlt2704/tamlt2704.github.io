# Chapter 10: Buildings

[← Ch 9](chapter-09-rocks-crystals.md) | [Ch 11 →](chapter-11-creatures.md)

---

## Juno's Request

> "Space stations. Outposts. Alien ruins. I need floor plans — rooms connected by corridors, with logical layouts. A station should have a bridge, crew quarters, engineering. Binary Space Partition — split a rectangle recursively, then connect the pieces."

---

## BSP: Binary Space Partition

```
1. Start with a large rectangle
2. Split it (H or V) into two halves
3. Recursively split each half
4. Place a room inside each leaf
5. Connect sibling rooms with corridors
```

---

## Implementation

```typescript
import Alea from 'alea';

interface Rect { x: number; y: number; w: number; h: number; }
interface BSPNode { bounds: Rect; room?: Rect; left?: BSPNode; right?: BSPNode; }

function splitBSP(bounds: Rect, rng: () => number, minSize = 8, depth = 0, maxDepth = 5): BSPNode {
  const node: BSPNode = { bounds };
  if (depth >= maxDepth || (bounds.w < minSize*2 && bounds.h < minSize*2)) {
    const pad = 1;
    const rw = minSize + Math.floor(rng() * (bounds.w - minSize - pad*2));
    const rh = minSize + Math.floor(rng() * (bounds.h - minSize - pad*2));
    const rx = bounds.x + pad + Math.floor(rng() * (bounds.w - rw - pad*2));
    const ry = bounds.y + pad + Math.floor(rng() * (bounds.h - rh - pad*2));
    node.room = { x: rx, y: ry, w: rw, h: rh };
    return node;
  }

  const vertical = bounds.w > bounds.h ? true : bounds.h > bounds.w ? false : rng() > 0.5;
  if (vertical) {
    const split = Math.floor(bounds.w * (0.3 + rng() * 0.4));
    node.left = splitBSP({x:bounds.x, y:bounds.y, w:split, h:bounds.h}, rng, minSize, depth+1, maxDepth);
    node.right = splitBSP({x:bounds.x+split, y:bounds.y, w:bounds.w-split, h:bounds.h}, rng, minSize, depth+1, maxDepth);
  } else {
    const split = Math.floor(bounds.h * (0.3 + rng() * 0.4));
    node.left = splitBSP({x:bounds.x, y:bounds.y, w:bounds.w, h:split}, rng, minSize, depth+1, maxDepth);
    node.right = splitBSP({x:bounds.x, y:bounds.y+split, w:bounds.w, h:bounds.h-split}, rng, minSize, depth+1, maxDepth);
  }
  return node;
}
```

---

## Connecting Rooms

```typescript
interface Corridor { x1:number; y1:number; x2:number; y2:number; }

function getRoomCenter(node: BSPNode): {x:number;y:number} | null {
  if (node.room) return { x: Math.floor(node.room.x+node.room.w/2), y: Math.floor(node.room.y+node.room.h/2) };
  return node.left ? getRoomCenter(node.left) : node.right ? getRoomCenter(node.right) : null;
}

function connectSiblings(node: BSPNode): Corridor[] {
  const corridors: Corridor[] = [];
  if (node.left && node.right) {
    const a = getRoomCenter(node.left), b = getRoomCenter(node.right);
    if (a && b) corridors.push({ x1:a.x, y1:a.y, x2:b.x, y2:b.y });
    corridors.push(...connectSiblings(node.left), ...connectSiblings(node.right));
  }
  return corridors;
}
```

---

## Rendering

```typescript
function renderFloorPlan(root: BSPNode, corridors: Corridor[], w: number, h: number, ts = 4): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = w*ts; canvas.height = h*ts;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Corridors
  ctx.fillStyle = '#3a3a4a';
  for (const c of corridors) {
    ctx.fillRect(Math.min(c.x1,c.x2)*ts, c.y1*ts, (Math.abs(c.x2-c.x1)+1)*ts, ts*2);
    ctx.fillRect(c.x2*ts, Math.min(c.y1,c.y2)*ts, ts*2, (Math.abs(c.y2-c.y1)+1)*ts);
  }

  // Rooms
  function drawRooms(node: BSPNode) {
    if (node.room) {
      ctx.fillStyle = '#2a2a3a';
      ctx.fillRect(node.room.x*ts, node.room.y*ts, node.room.w*ts, node.room.h*ts);
      ctx.strokeStyle = '#5a5a7a'; ctx.lineWidth = 2;
      ctx.strokeRect(node.room.x*ts, node.room.y*ts, node.room.w*ts, node.room.h*ts);
    }
    if (node.left) drawRooms(node.left);
    if (node.right) drawRooms(node.right);
  }
  drawRooms(root);
  return canvas;
}

function generateStation(seed: string | number, w = 60, h = 40): HTMLCanvasElement {
  const rng = Alea(seed);
  const root = splitBSP({x:0,y:0,w,h}, rng, 6, 0, 4);
  return renderFloorPlan(root, connectSiblings(root), w, h);
}
```

---

## Room Types

```typescript
type RoomType = 'bridge' | 'quarters' | 'engineering' | 'cargo' | 'medbay' | 'airlock';

function assignRoomTypes(node: BSPNode, rng: () => number): Map<Rect, RoomType> {
  const rooms: Rect[] = [];
  (function collect(n: BSPNode) { if(n.room) rooms.push(n.room); if(n.left) collect(n.left); if(n.right) collect(n.right); })(node);
  rooms.sort((a,b) => (b.w*b.h) - (a.w*a.h)); // largest first
  const types: RoomType[] = ['bridge','quarters','engineering','cargo','medbay','airlock'];
  const map = new Map<Rect, RoomType>();
  rooms.forEach((r, i) => map.set(r, types[i] || (rng()>0.5 ? 'quarters' : 'cargo')));
  return map;
}
```

---

## Visual Result

```
┌──────────────────────────────────────────────────┐
│ ┌──────────┐          ┌─────────────────┐       │
│ │ BRIDGE   │──────────│  ENGINEERING    │       │
│ └──────────┘          └────────┬────────┘       │
│       │                        │                 │
│ ┌─────┴────┐    ┌─────────────┴──┐             │
│ │ QUARTERS │────│     CARGO      │             │
│ └──────────┘    └────────┬───────┘             │
│                    ┌─────┴──┐                    │
│                    │AIRLOCK │                    │
│                    └────────┘                    │
└──────────────────────────────────────────────────┘
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| `maxDepth` | 3 | 6 | Few large vs many small rooms |
| `minSize` | 4 | 10 | Cramped vs spacious |
| Split ratio | 0.3-0.7 | 0.4-0.6 | Uneven vs balanced |

**Juno's notes:**

> "maxDepth 4 gives 8-16 rooms. minSize 6 ensures rooms are big enough to fight in. Always assign types by size — bridge should be biggest."

---

## Exercises

1. **Door placement:** Where corridors meet room walls, place a "door" tile (different color).

2. **Multi-floor:** Generate 3 BSP layouts. Add "elevator" rooms at same position on each floor.

3. **Alien ruins:** Use BSP bounds but fill rooms with cellular automata (Ch 6) for organic shapes.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| BSP | Recursively split rectangle into halves |
| Leaf nodes | Smallest partitions — rooms go here |
| Corridors | Connect sibling room centers (L-shaped) |
| Room types | Assign by size (largest = most important) |
| Connectivity | BSP tree guarantees all rooms connect |

---

[← Ch 9](chapter-09-rocks-crystals.md) | [Ch 11 →](chapter-11-creatures.md)
