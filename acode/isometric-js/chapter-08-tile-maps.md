# Chapter 8: Tile Maps

[← Chapter 7: Multi-Tile Objects](chapter-07-multi-tile-objects.md) | [Chapter 9: Terrain →](chapter-09-terrain.md)

---

## The Task

Riku is tired of you hard-coding tile positions. "I want to design the map visually. Place grass here, water there, a road connecting the buildings. Like a level editor."

You could build a custom editor. Or you could use **Tiled** — a free, open-source map editor that exports JSON. Every 2D game uses it. The format is well-documented and easy to parse.

"Export the map as JSON. I'll load it and render it."

## Tiled Map Editor Basics

Download Tiled from [mapeditor.org](https://www.mapeditor.org/). Create a new map:

- **Orientation**: Isometric
- **Tile size**: 64×32 (matches our TILE_W and TILE_H)
- **Map size**: 20×20 tiles

Add a tileset — point it at Riku's spritesheet (`atlas.png`). Now Riku can paint the map visually: grass base layer, water features, roads, decoration placement.

Tiled organizes maps into **layers**:
- **ground** — base terrain (grass, dirt, sand)
- **roads** — road tiles on top of ground
- **objects** — buildings, trees, decorations
- **collision** — invisible layer marking unbuildable tiles

## The Tiled JSON Format

Export as JSON. The structure:

```json
{
  "width": 20,
  "height": 20,
  "tilewidth": 64,
  "tileheight": 32,
  "orientation": "isometric",
  "layers": [
    {
      "name": "ground",
      "type": "tilelayer",
      "width": 20,
      "height": 20,
      "data": [1, 1, 1, 2, 2, 1, 1, 3, 3, 1, ...]
    },
    {
      "name": "objects",
      "type": "objectgroup",
      "objects": [
        {
          "name": "townHall",
          "type": "building",
          "x": 192,
          "y": 128,
          "width": 128,
          "height": 64,
          "properties": [
            { "name": "buildingId", "value": "townHall" }
          ]
        }
      ]
    }
  ],
  "tilesets": [
    {
      "firstgid": 1,
      "name": "terrain",
      "tilewidth": 64,
      "tileheight": 32,
      "tilecount": 24,
      "columns": 6,
      "image": "atlas.png"
    }
  ]
}
```

Key details:
- `data` is a flat array of tile IDs (row by row, left to right, top to bottom)
- Tile ID `0` means empty (no tile)
- `firstgid` offsets tile IDs per tileset (usually 1 for the first tileset)
- Object layers use pixel coordinates, not tile coordinates

## Parsing the Map

```typescript
// src/engine/tilemap.ts
interface TiledLayer {
  name: string;
  type: 'tilelayer' | 'objectgroup';
  width?: number;
  height?: number;
  data?: number[];
  objects?: TiledObject[];
}

interface TiledObject {
  name: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  properties?: Array<{ name: string; value: string | number | boolean }>;
}

interface TiledTileset {
  firstgid: number;
  name: string;
  tilewidth: number;
  tileheight: number;
  tilecount: number;
  columns: number;
  image: string;
}

interface TiledMap {
  width: number;
  height: number;
  tilewidth: number;
  tileheight: number;
  orientation: string;
  layers: TiledLayer[];
  tilesets: TiledTileset[];
}

export class TileMap {
  width: number;
  height: number;
  layers: Map<string, number[]>;
  objects: TiledObject[];
  tilesets: TiledTileset[];

  constructor(data: TiledMap) {
    this.width = data.width;
    this.height = data.height;
    this.layers = new Map();
    this.objects = [];
    this.tilesets = data.tilesets;

    for (const layer of data.layers) {
      if (layer.type === 'tilelayer' && layer.data) {
        this.layers.set(layer.name, layer.data);
      } else if (layer.type === 'objectgroup' && layer.objects) {
        this.objects.push(...layer.objects);
      }
    }
  }

  getTile(layerName: string, x: number, y: number): number {
    const layer = this.layers.get(layerName);
    if (!layer) return 0;
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) return 0;

    // Tiled stores data row by row (y * width + x)
    return layer[y * this.width + x];
  }

  getProperty(obj: TiledObject, name: string): string | number | boolean | undefined {
    const prop = obj.properties?.find(p => p.name === name);
    return prop?.value;
  }
}
```

## Loading the Map

```typescript
// src/engine/loader.ts
export async function loadTiledMap(url: string): Promise<TileMap> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load map: ${url} (${response.status})`);
  }
  const data: TiledMap = await response.json();
  return new TileMap(data);
}
```

```typescript
// src/main.ts
import { loadTiledMap } from './engine/loader';
import { TileAtlas } from './engine/atlas';

let tileMap: TileMap;
let atlas: TileAtlas;

async function init() {
  // Load the map JSON
  tileMap = await loadTiledMap('/assets/maps/town.json');

  // Load the tileset image
  const atlasImage = await loadImage('/assets/tiles/atlas.png');
  atlas = new TileAtlas(atlasImage, TILE_W, TILE_H);

  requestAnimationFrame(gameLoop);
}
```

## Tile IDs and Tilesets

Tiled uses global tile IDs (GIDs). The first tileset starts at `firstgid` (usually 1). To get the local tile index for drawing from the atlas:

```typescript
function gidToLocalId(gid: number, tilesets: TiledTileset[]): { tilesetIndex: number; localId: number } {
  // Find which tileset this GID belongs to
  // Tilesets are sorted by firstgid
  let tilesetIndex = 0;
  for (let i = tilesets.length - 1; i >= 0; i--) {
    if (gid >= tilesets[i].firstgid) {
      tilesetIndex = i;
      break;
    }
  }

  const localId = gid - tilesets[tilesetIndex].firstgid;
  return { tilesetIndex, localId };
}
```

## Rendering a Tiled Map

```typescript
function renderTileLayer(
  layerName: string,
  tileMap: TileMap,
  atlas: TileAtlas,
  offsetX: number,
  offsetY: number
) {
  for (let sum = 0; sum < tileMap.width + tileMap.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= tileMap.width || y >= tileMap.height) continue;

      const gid = tileMap.getTile(layerName, x, y);
      if (gid === 0) continue; // Empty tile

      // Convert GID to local atlas index
      const localId = gid - tileMap.tilesets[0].firstgid;

      const { screenX, screenY } = cartToIso(x, y);

      atlas.drawTile(
        ctx,
        localId,
        screenX + offsetX - TILE_W / 2,
        screenY + offsetY - TILE_H / 2
      );
    }
  }
}
```

Render layers in order — ground first, then roads, then decorations:

```typescript
function render() {
  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  renderTileLayer('ground', tileMap, atlas, worldOffsetX, worldOffsetY);
  renderTileLayer('roads', tileMap, atlas, worldOffsetX, worldOffsetY);
  renderTileLayer('decorations', tileMap, atlas, worldOffsetX, worldOffsetY);

  // Render placed buildings (from object layer or player-placed)
  renderBuildings();

  ctx.restore();
}
```

## Parsing Object Layers

Object layers contain positioned entities — buildings, spawn points, triggers:

```typescript
function loadObjectsFromMap(tileMap: TileMap, buildingManager: BuildingManager, grid: Grid) {
  for (const obj of tileMap.objects) {
    if (obj.type === 'building') {
      const buildingId = tileMap.getProperty(obj, 'buildingId') as string;
      if (buildingId) {
        // Convert pixel position to grid position
        // Tiled uses pixel coords for isometric objects
        const gridX = Math.floor(obj.x / TILE_W);
        const gridY = Math.floor(obj.y / TILE_H);
        buildingManager.tryPlace(gridX, gridY, buildingId, grid);
      }
    }
  }
}
```

## Multiple Tilesets

Larger maps use multiple tilesets — terrain, buildings, decorations. Each has its own `firstgid`:

```typescript
// src/engine/tilemap.ts
export class MultiAtlas {
  private atlases: Array<{ firstgid: number; atlas: TileAtlas }> = [];

  addTileset(firstgid: number, atlas: TileAtlas) {
    this.atlases.push({ firstgid, atlas });
    // Keep sorted by firstgid descending for lookup
    this.atlases.sort((a, b) => b.firstgid - a.firstgid);
  }

  drawGid(ctx: CanvasRenderingContext2D, gid: number, destX: number, destY: number) {
    if (gid === 0) return;

    // Find the correct atlas
    for (const { firstgid, atlas } of this.atlases) {
      if (gid >= firstgid) {
        atlas.drawTile(ctx, gid - firstgid, destX, destY);
        return;
      }
    }
  }
}
```

Load all tilesets:

```typescript
async function loadAllTilesets(tileMap: TileMap): Promise<MultiAtlas> {
  const multiAtlas = new MultiAtlas();

  for (const tileset of tileMap.tilesets) {
    const image = await loadImage(`/assets/tiles/${tileset.image}`);
    const atlas = new TileAtlas(image, tileset.tilewidth, tileset.tileheight);
    multiAtlas.addTileset(tileset.firstgid, atlas);
  }

  return multiAtlas;
}
```

## Hot-Reloading Maps During Development

With Vite, you can watch for map file changes and reload:

```typescript
// Development only — reload map on file change
if (import.meta.hot) {
  import.meta.hot.accept(() => {
    // Vite HMR triggers on file change
    loadTiledMap('/assets/maps/town.json').then(map => {
      tileMap = map;
      console.log('Map reloaded');
    });
  });
}
```

Now Riku can edit the map in Tiled, save, and see changes in the browser immediately.

## The Complete Map Loader

```typescript
// src/engine/loader.ts
import { TileMap, TiledMap } from './tilemap';
import { TileAtlas } from './atlas';
import { MultiAtlas } from './tilemap';
import { loadImage } from './assets';

export interface LoadedMap {
  tileMap: TileMap;
  atlas: MultiAtlas;
}

export async function loadMap(mapUrl: string, assetBase: string): Promise<LoadedMap> {
  // Load map JSON
  const response = await fetch(mapUrl);
  const data: TiledMap = await response.json();
  const tileMap = new TileMap(data);

  // Load all tileset images
  const atlas = new MultiAtlas();
  for (const tileset of data.tilesets) {
    const image = await loadImage(`${assetBase}/${tileset.image}`);
    const tileAtlas = new TileAtlas(image, tileset.tilewidth, tileset.tileheight);
    atlas.addTileset(tileset.firstgid, tileAtlas);
  }

  return { tileMap, atlas };
}
```

```typescript
// src/main.ts
import { loadMap } from './engine/loader';

async function init() {
  const { tileMap, atlas } = await loadMap(
    '/assets/maps/town.json',
    '/assets/tiles'
  );

  // Initialize grid from map dimensions
  const grid = new Grid(tileMap.width, tileMap.height);

  // Load objects
  loadObjectsFromMap(tileMap, buildingManager, grid);

  // Start game
  requestAnimationFrame(gameLoop);
}
```

## Riku's Reaction

Riku opens Tiled, paints a lake, adds some roads, places trees. Saves. The browser updates. His map appears in the game — isometric, depth-sorted, interactive.

Riku: "This is great. But the edges between grass and water look harsh. In real games, there are transition tiles — grass fading into water, dirt blending into sand."

You: "Auto-tiling. We look at each tile's neighbors and pick the right transition sprite automatically."

Riku: "And elevation? Hills?"

You: "Same idea — different tile heights. Next chapter."

## What You Built

- **Tiled integration** — load maps from the standard JSON format
- **Layer parsing** — separate ground, roads, objects, decorations
- **Tile ID mapping** — GID to local atlas index with firstgid offset
- **Multi-tileset support** — multiple atlases with automatic GID routing
- **Object layer parsing** — extract building placements and properties
- **Sorted rendering** — diagonal iteration per layer, layers drawn in order
- **Hot reload** — edit in Tiled, see changes instantly in browser

Maps come from files now, not code. Next: making terrain transitions look natural with auto-tiling.

---

[← Chapter 7: Multi-Tile Objects](chapter-07-multi-tile-objects.md) | [Chapter 9: Terrain →](chapter-09-terrain.md)
