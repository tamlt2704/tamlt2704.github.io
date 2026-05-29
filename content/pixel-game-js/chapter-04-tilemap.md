# Tilemaps

[prev: Sprites](./chapter-03-sprites.md) | [next: Phaser 3](./chapter-05-phaser.md)

Tilemaps let you build large worlds from small reusable tiles. A 16x16 tileset can create infinite variety.

## Tile-Based World

```
Tileset (one image):        Map (array of indices):
+---+---+---+---+           [0,0,0,0,0,0,0,0]
| 0 | 1 | 2 | 3 |          [0,0,0,0,0,0,0,0]
+---+---+---+---+           [0,0,0,0,0,0,0,0]
| 4 | 5 | 6 | 7 |          [1,1,1,0,0,1,1,1]
+---+---+---+---+           [2,2,2,0,0,2,2,2]
                             [3,3,3,3,3,3,3,3]
0=sky, 1=grass-top, 2=dirt, 3=stone
```

## Basic Tilemap Renderer

```typescript
const TILE_SIZE = 16;
const MAP_W = 10;
const MAP_H = 9;

const map = [
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,
  1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
];

let tileset: HTMLImageElement;
const TILESET_COLS = 4; // tiles per row in the tileset image

function drawMap() {
  for (let i = 0; i < map.length; i++) {
    const tileId = map[i];
    if (tileId === 0) continue;

    const destX = (i % MAP_W) * TILE_SIZE;
    const destY = Math.floor(i / MAP_W) * TILE_SIZE;
    const srcX = (tileId % TILESET_COLS) * TILE_SIZE;
    const srcY = Math.floor(tileId / TILESET_COLS) * TILE_SIZE;

    ctx.drawImage(tileset, srcX, srcY, TILE_SIZE, TILE_SIZE, destX, destY, TILE_SIZE, TILE_SIZE);
  }
}
```

## Loading Tilemap Data (JSON)

Export from Tiled editor or define manually:

```typescript
interface TilemapData {
  width: number;
  height: number;
  tileSize: number;
  layers: { name: string; data: number[] }[];
}

async function loadMap(url: string): Promise<TilemapData> {
  const res = await fetch(url);
  return res.json();
}

// map.json
// {
//   "width": 20, "height": 15, "tileSize": 16,
//   "layers": [
//     { "name": "background", "data": [0,0,0,...] },
//     { "name": "foreground", "data": [0,0,5,...] },
//     { "name": "collision",  "data": [0,0,1,...] }
//   ]
// }
```

## Camera / Viewport Scrolling

For maps larger than the screen, use a camera offset:

```typescript
const camera = { x: 0, y: 0 };
const SCREEN_W = 160;
const SCREEN_H = 144;

function updateCamera(targetX: number, targetY: number) {
  camera.x = targetX - SCREEN_W / 2;
  camera.y = targetY - SCREEN_H / 2;

  // Clamp to map bounds
  camera.x = Math.max(0, Math.min(camera.x, MAP_W * TILE_SIZE - SCREEN_W));
  camera.y = Math.max(0, Math.min(camera.y, MAP_H * TILE_SIZE - SCREEN_H));

  camera.x = Math.floor(camera.x);
  camera.y = Math.floor(camera.y);
}

function drawMapWithCamera() {
  // Only draw visible tiles
  const startCol = Math.floor(camera.x / TILE_SIZE);
  const startRow = Math.floor(camera.y / TILE_SIZE);
  const endCol = Math.min(startCol + Math.ceil(SCREEN_W / TILE_SIZE) + 1, MAP_W);
  const endRow = Math.min(startRow + Math.ceil(SCREEN_H / TILE_SIZE) + 1, MAP_H);

  for (let row = startRow; row < endRow; row++) {
    for (let col = startCol; col < endCol; col++) {
      const tileId = map[row * MAP_W + col];
      if (tileId === 0) continue;

      const destX = col * TILE_SIZE - camera.x;
      const destY = row * TILE_SIZE - camera.y;
      const srcX = (tileId % TILESET_COLS) * TILE_SIZE;
      const srcY = Math.floor(tileId / TILESET_COLS) * TILE_SIZE;

      ctx.drawImage(tileset, srcX, srcY, TILE_SIZE, TILE_SIZE, destX, destY, TILE_SIZE, TILE_SIZE);
    }
  }
}
```

## Tile Collision

```typescript
function getTile(x: number, y: number, layer: number[]): number {
  const col = Math.floor(x / TILE_SIZE);
  const row = Math.floor(y / TILE_SIZE);
  if (col < 0 || col >= MAP_W || row < 0 || row >= MAP_H) return 1; // solid outside
  return layer[row * MAP_W + col];
}

function isSolid(x: number, y: number): boolean {
  return getTile(x, y, collisionLayer) !== 0;
}

// Check player movement
function movePlayer(dt: number) {
  const newX = player.x + player.vx * dt;
  const newY = player.y + player.vy * dt;

  // Horizontal
  if (
    !isSolid(newX, player.y) &&
    !isSolid(newX + player.width - 1, player.y) &&
    !isSolid(newX, player.y + player.height - 1) &&
    !isSolid(newX + player.width - 1, player.y + player.height - 1)
  ) {
    player.x = newX;
  } else {
    player.vx = 0;
  }

  // Vertical
  if (
    !isSolid(player.x, newY) &&
    !isSolid(player.x + player.width - 1, newY) &&
    !isSolid(player.x, newY + player.height - 1) &&
    !isSolid(player.x + player.width - 1, newY + player.height - 1)
  ) {
    player.y = newY;
  } else {
    player.vy = 0;
  }
}
```

## Tiled Editor Export

[Tiled](https://www.mapeditor.org/) is the standard tilemap editor. Export as JSON:

```typescript
// Tiled JSON format (simplified)
interface TiledMap {
  width: number;
  height: number;
  tilewidth: number;
  tileheight: number;
  layers: {
    name: string;
    type: string;
    data: number[]; // 1-indexed! Subtract 1 for your tileset
  }[];
}

async function loadTiledMap(url: string) {
  const data: TiledMap = await (await fetch(url)).json();
  return {
    width: data.width,
    height: data.height,
    tileSize: data.tilewidth,
    layers: data.layers
      .filter((l) => l.type === "tilelayer")
      .map((l) => ({
        name: l.name,
        data: l.data.map((id) => id - 1), // Tiled uses 1-indexed, 0 = empty
      })),
  };
}
```

## Layers

Render layers in order: background first, then player, then foreground:

```typescript
function render() {
  ctx.fillStyle = "#87ceeb"; // sky
  ctx.fillRect(0, 0, SCREEN_W, SCREEN_H);

  drawLayer(mapData.layers[0]); // background
  drawPlayer();
  drawLayer(mapData.layers[1]); // foreground (trees, roofs)
}

function drawLayer(layer: { data: number[] }) {
  const startCol = Math.floor(camera.x / TILE_SIZE);
  const startRow = Math.floor(camera.y / TILE_SIZE);
  const endCol = Math.min(startCol + Math.ceil(SCREEN_W / TILE_SIZE) + 1, MAP_W);
  const endRow = Math.min(startRow + Math.ceil(SCREEN_H / TILE_SIZE) + 1, MAP_H);

  for (let row = startRow; row < endRow; row++) {
    for (let col = startCol; col < endCol; col++) {
      const tileId = layer.data[row * MAP_W + col];
      if (tileId < 0) continue;
      const destX = col * TILE_SIZE - camera.x;
      const destY = row * TILE_SIZE - camera.y;
      const srcX = (tileId % TILESET_COLS) * TILE_SIZE;
      const srcY = Math.floor(tileId / TILESET_COLS) * TILE_SIZE;
      ctx.drawImage(tileset, srcX, srcY, TILE_SIZE, TILE_SIZE, destX, destY, TILE_SIZE, TILE_SIZE);
    }
  }
}
```

## Complete Example

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
canvas.width = 160;
canvas.height = 144;
ctx.imageSmoothingEnabled = false;

const TILE = 16,
  COLS = 20,
  ROWS = 15;
const camera = { x: 0, y: 0 };
const player = { x: 32, y: 32, vx: 0, vy: 0, w: 12, h: 14 };
const keys: Record<string, boolean> = {};
window.addEventListener("keydown", (e) => {
  keys[e.code] = true;
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

const collision = [
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1,
];

function isSolid(x: number, y: number) {
  const c = Math.floor(x / TILE),
    r = Math.floor(y / TILE);
  if (c < 0 || c >= COLS || r < 0 || r >= ROWS) return true;
  return collision[r * COLS + c] !== 0;
}

let lastTime = 0;
function loop(t: number) {
  const dt = Math.min((t - lastTime) / 1000, 0.1);
  lastTime = t;
  const speed = 80;
  player.vx = 0;
  player.vy = 0;
  if (keys["ArrowLeft"]) player.vx = -speed;
  if (keys["ArrowRight"]) player.vx = speed;
  if (keys["ArrowUp"]) player.vy = -speed;
  if (keys["ArrowDown"]) player.vy = speed;

  const nx = player.x + player.vx * dt;
  if (!isSolid(nx, player.y) && !isSolid(nx + player.w, player.y + player.h)) player.x = nx;
  const ny = player.y + player.vy * dt;
  if (!isSolid(player.x, ny) && !isSolid(player.x + player.w, ny + player.h)) player.y = ny;

  camera.x = Math.floor(player.x - 80);
  camera.y = Math.floor(player.y - 72);

  ctx.fillStyle = "#2d2d44";
  ctx.fillRect(0, 0, 160, 144);
  for (let i = 0; i < collision.length; i++) {
    if (collision[i] === 0) continue;
    const dx = (i % COLS) * TILE - camera.x;
    const dy = Math.floor(i / COLS) * TILE - camera.y;
    ctx.fillStyle = "#5a5a8a";
    ctx.fillRect(dx, dy, TILE, TILE);
  }
  ctx.fillStyle = "#e94560";
  ctx.fillRect(
    Math.floor(player.x - camera.x),
    Math.floor(player.y - camera.y),
    player.w,
    player.h,
  );

  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
```

[prev: Sprites](./chapter-03-sprites.md) | [next: Phaser 3](./chapter-05-phaser.md)
