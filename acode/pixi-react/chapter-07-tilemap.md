# Chapter 7: Tilemap — "Build the Dungeon"

[← Chapter 6: Input & Controls](chapter-06-input-controls.md) | [Chapter 8: Collision →](chapter-08-collision.md)

---

## The Crisis

Kai sends a tile atlas: `tiles.png` — a grid of 16×16 tiles. Floor stones, wall bricks, doors, torches, pits. "Build me a dungeon room. 20 tiles wide, 15 tiles tall."

You can't place 300 sprites by hand. You need a data-driven approach: a 2D array that describes the room, and code that renders it.

## The Tile Map Data

A dungeon room as a 2D array. Each number maps to a tile type:

```jsx
// src/data/level1.js
export const TILE_SIZE = 16;
export const SCALE = 3;

// 0 = void, 1 = wall, 2 = floor, 3 = door
export const room1 = [
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
  [1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1],
];
```

20 columns × 15 rows. At 16px per tile × 3x scale = 960×720 pixels. Bigger than our 480×320 viewport — we'll need a camera.

## The Tile Atlas

Kai's tile atlas is a single PNG with tiles in a grid:

```
tiles.png (64×16 — four tiles in a row)
┌────┬────┬────┬────┐
│void│wall│floor│door│
└────┴────┴────┴────┘
  0     1     2     3
```

Create `public/sprites/tiles.json`:

```json
{
  "frames": {
    "void": { "frame": { "x": 0, "y": 0, "w": 16, "h": 16 } },
    "wall": { "frame": { "x": 16, "y": 0, "w": 16, "h": 16 } },
    "floor": { "frame": { "x": 32, "y": 0, "w": 16, "h": 16 } },
    "door": { "frame": { "x": 48, "y": 0, "w": 16, "h": 16 } }
  },
  "meta": {
    "image": "tiles.png",
    "format": "RGBA8888",
    "size": { "w": 64, "h": 16 },
    "scale": "1"
  }
}
```

## Rendering the Tilemap

Map the 2D array to Sprite components:

```jsx
import { Container, Sprite } from '@pixi/react';
import { useMemo } from 'react';

const TILE_NAMES = ['void', 'wall', 'floor', 'door'];

function Tilemap({ tileSheet, mapData, tileSize = 16, scale = 3 }) {
  const tiles = useMemo(() => {
    const result = [];
    for (let row = 0; row < mapData.length; row++) {
      for (let col = 0; col < mapData[row].length; col++) {
        const tileId = mapData[row][col];
        if (tileId === 0) continue; // skip void tiles

        const tileName = TILE_NAMES[tileId];
        result.push({
          key: `${row}-${col}`,
          texture: tileSheet.textures[tileName],
          x: col * tileSize * scale,
          y: row * tileSize * scale,
        });
      }
    }
    return result;
  }, [tileSheet, mapData, tileSize, scale]);

  return (
    <Container>
      {tiles.map(tile => (
        <Sprite
          key={tile.key}
          texture={tile.texture}
          x={tile.x}
          y={tile.y}
          scale={scale}
        />
      ))}
    </Container>
  );
}
```

`useMemo` ensures we only recalculate tile positions when the map data changes — not every frame.

## Camera / Viewport Scrolling

The map is bigger than the screen. We need a camera that follows the player. The trick: move the **world container** in the opposite direction of the player.

```jsx
function Game({ assets }) {
  const [cameraX, setCameraX] = useState(0);
  const [cameraY, setCameraY] = useState(0);
  const playerPos = useRef({ x: 240, y: 200 });

  // Update camera to follow player
  useTick(() => {
    const screenW = 480;
    const screenH = 320;

    // Center camera on player
    let camX = playerPos.current.x - screenW / 2;
    let camY = playerPos.current.y - screenH / 2;

    // Clamp to map bounds
    const mapW = 20 * 16 * 3;  // 20 tiles × 16px × 3 scale
    const mapH = 15 * 16 * 3;
    camX = Math.max(0, Math.min(camX, mapW - screenW));
    camY = Math.max(0, Math.min(camY, mapH - screenH));

    setCameraX(camX);
    setCameraY(camY);
  });

  return (
    <>
      {/* World layer — moves opposite to camera */}
      <Container x={-cameraX} y={-cameraY}>
        <Tilemap tileSheet={assets.tiles} mapData={room1} />
        <Player sheet={assets.knight} posRef={playerPos} />
      </Container>

      {/* HUD — stays fixed */}
      <Container x={0} y={0}>
        {/* health bar, score */}
      </Container>
    </>
  );
}
```

The world container moves left when the player moves right. The player appears to stay centered on screen while the world scrolls beneath them.

## Smoother Camera with Lerp

Snapping the camera instantly feels jarring. Smooth it with linear interpolation (lerp):

```jsx
function Game({ assets }) {
  const cameraRef = useRef({ x: 0, y: 0 });
  const worldRef = useRef(null);
  const playerPos = useRef({ x: 240, y: 200 });

  useTick((delta) => {
    const screenW = 480;
    const screenH = 320;
    const mapW = 20 * 16 * 3;
    const mapH = 15 * 16 * 3;

    // Target camera position (centered on player)
    let targetX = playerPos.current.x - screenW / 2;
    let targetY = playerPos.current.y - screenH / 2;

    // Clamp
    targetX = Math.max(0, Math.min(targetX, mapW - screenW));
    targetY = Math.max(0, Math.min(targetY, mapH - screenH));

    // Lerp toward target (0.1 = smooth, 1.0 = instant)
    const lerp = 0.1;
    cameraRef.current.x += (targetX - cameraRef.current.x) * lerp;
    cameraRef.current.y += (targetY - cameraRef.current.y) * lerp;

    // Apply to world container
    if (worldRef.current) {
      worldRef.current.x = -Math.round(cameraRef.current.x);
      worldRef.current.y = -Math.round(cameraRef.current.y);
    }
  });

  return (
    <Container ref={worldRef}>
      <Tilemap tileSheet={assets.tiles} mapData={room1} />
      <Player sheet={assets.knight} posRef={playerPos} />
    </Container>
  );
}
```

`Math.round` snaps to whole pixels — important for pixel art. Sub-pixel positions cause shimmer artifacts.

## Culling Off-Screen Tiles

Rendering 300 tiles when only ~60 are visible is wasteful. Cull tiles outside the viewport:

```jsx
function Tilemap({ tileSheet, mapData, tileSize = 16, scale = 3, cameraX = 0, cameraY = 0, screenW = 480, screenH = 320 }) {
  const visibleTiles = useMemo(() => {
    const scaledSize = tileSize * scale;
    const result = [];

    // Calculate visible tile range
    const startCol = Math.max(0, Math.floor(cameraX / scaledSize) - 1);
    const endCol = Math.min(mapData[0].length, Math.ceil((cameraX + screenW) / scaledSize) + 1);
    const startRow = Math.max(0, Math.floor(cameraY / scaledSize) - 1);
    const endRow = Math.min(mapData.length, Math.ceil((cameraY + screenH) / scaledSize) + 1);

    for (let row = startRow; row < endRow; row++) {
      for (let col = startCol; col < endCol; col++) {
        const tileId = mapData[row][col];
        if (tileId === 0) continue;

        result.push({
          key: `${row}-${col}`,
          texture: tileSheet.textures[TILE_NAMES[tileId]],
          x: col * scaledSize,
          y: row * scaledSize,
        });
      }
    }
    return result;
  }, [tileSheet, mapData, tileSize, scale, cameraX, cameraY, screenW, screenH]);

  return (
    <Container>
      {visibleTiles.map(tile => (
        <Sprite key={tile.key} texture={tile.texture} x={tile.x} y={tile.y} scale={scale} />
      ))}
    </Container>
  );
}
```

Only tiles within the camera viewport (plus a 1-tile buffer) are rendered. For a 20×15 map this doesn't matter much, but for larger maps (100×100+) it's essential.

## Multiple Tile Layers

Real dungeons have layers — floor underneath, walls on top, decorations above that:

```jsx
// Level data with multiple layers
export const level1 = {
  floor: [
    [2,2,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,2],
    // ...
  ],
  walls: [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    // ... (0 = no wall)
  ],
  objects: [
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,0,4,0,0,5,0,0,0],
    // ... (4 = torch, 5 = chest)
  ],
};

// Render layers in order
function DungeonRoom({ assets, level }) {
  return (
    <Container>
      <Tilemap tileSheet={assets.tiles} mapData={level.floor} />
      <Tilemap tileSheet={assets.tiles} mapData={level.walls} />
      {/* Objects layer with special components */}
      <ObjectLayer tileSheet={assets.tiles} mapData={level.objects} />
    </Container>
  );
}
```

## Verify

- [ ] Tilemap renders from a 2D array
- [ ] Tiles use the correct textures from the atlas
- [ ] Camera follows the player smoothly
- [ ] Camera clamps to map edges (no void visible)
- [ ] Pixel-perfect rendering (no shimmer, whole-pixel positions)
- [ ] Performance is smooth with 300+ tiles

Kai looks at the dungeon room. Walls, floor, doors. The knight walks around freely. "Wait — he's walking through the walls. That's not right."

Collision detection. That's Chapter 8.

---

[← Chapter 6: Input & Controls](chapter-06-input-controls.md) | [Chapter 8: Collision →](chapter-08-collision.md)
