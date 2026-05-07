# Chapter 12: Performance

[← Chapter 11: Build Mode](chapter-11-build-mode.md) | [Chapter 13: Pathfinding →](chapter-13-pathfinding.md)

---

## The Problem

Riku placed 500 buildings. The frame rate dropped to 12 FPS. You open the browser profiler and see the truth: `drawImage` is being called 800+ times per frame. Each call is a separate GPU texture upload. The Canvas 2D API wasn't designed for this.

```
Frame budget: 16.6ms (60 FPS)
Actual frame time: 83ms (12 FPS)

Breakdown:
  drawImage calls: 812
  Terrain tiles: 400 (20×20 visible)
  Buildings: 380
  Decorations: 32
```

The Canvas 2D context can't batch. Every `drawImage` is an independent operation. You need WebGL — but you don't want to write shaders by hand.

## Introducing PixiJS

PixiJS is a 2D WebGL renderer that speaks the same language as Canvas (sprites, containers, positions) but batches draw calls automatically:

```bash
npm install pixi.js
```

```typescript
// src/engine/renderer.ts
import { Application, Sprite, Container, Texture, Assets } from 'pixi.js';

const TILE_W = 64;
const TILE_H = 32;

export async function createRenderer(canvas: HTMLCanvasElement) {
  const app = new Application();

  await app.init({
    canvas,
    width: 960,
    height: 640,
    backgroundColor: 0x1a1a2e,
    antialias: false,
  });

  return app;
}
```

## Migrating from Canvas to PixiJS

The key insight: PixiJS batches all sprites that share the same texture into a single draw call. 500 buildings using the same spritesheet = 1 draw call.

Before (Canvas 2D):
```typescript
// 500 separate drawImage calls
for (const building of buildings) {
  ctx.drawImage(building.sprite, building.x, building.y);
}
```

After (PixiJS):
```typescript
// 500 sprites, but PixiJS batches them into ~1-3 draw calls
const worldContainer = new Container();

for (const building of buildings) {
  const sprite = new Sprite(building.texture);
  sprite.x = building.x;
  sprite.y = building.y;
  worldContainer.addChild(sprite);
}

app.stage.addChild(worldContainer);
```

## Setting Up the Isometric World Container

```typescript
// src/engine/iso-stage.ts
import { Container, Sprite, Texture, Spritesheet } from 'pixi.js';

export class IsoStage {
  readonly world: Container;
  readonly terrainLayer: Container;
  readonly buildingLayer: Container;
  readonly effectsLayer: Container;

  private tileSprites: Map<string, Sprite> = new Map();

  constructor() {
    this.world = new Container();
    this.terrainLayer = new Container();
    this.buildingLayer = new Container();
    this.effectsLayer = new Container();

    this.world.addChild(this.terrainLayer);
    this.world.addChild(this.buildingLayer);
    this.world.addChild(this.effectsLayer);
  }

  buildTerrain(grid: GameGrid, textures: Map<string, Texture>) {
    this.terrainLayer.removeChildren();

    for (let y = 0; y < grid.height; y++) {
      for (let x = 0; x < grid.width; x++) {
        const terrain = grid.getTerrain(x, y);
        const texture = textures.get(terrain) ?? textures.get('grass')!;

        const sprite = new Sprite(texture);
        const { screenX, screenY } = cartToIso(x, y);
        sprite.x = screenX - TILE_W / 2;
        sprite.y = screenY - TILE_H / 2;

        // Store for later updates
        this.tileSprites.set(`${x},${y}`, sprite);
        this.terrainLayer.addChild(sprite);
      }
    }
  }

  addBuilding(gridX: number, gridY: number, texture: Texture, spriteHeight: number) {
    const sprite = new Sprite(texture);
    const { screenX, screenY } = cartToIso(gridX, gridY);

    sprite.x = screenX - TILE_W / 2;
    sprite.y = screenY - spriteHeight + TILE_H / 2;

    // Depth sorting: use zIndex based on grid position
    sprite.zIndex = gridX + gridY;

    this.buildingLayer.addChild(sprite);
    return sprite;
  }

  enableDepthSort() {
    this.buildingLayer.sortableChildren = true;
  }
}
```

## Sprite Batching Explained

WebGL draws triangles. Each sprite is 2 triangles (a quad). PixiJS collects all sprites that share the same base texture and submits them in one `drawElements` call:

```
Canvas 2D:                    PixiJS WebGL:
┌─────────────────────┐       ┌─────────────────────┐
│ drawImage (house)   │       │ Batch:              │
│ drawImage (house)   │       │   512 sprites       │
│ drawImage (house)   │       │   same spritesheet  │
│ ... × 500           │       │   1 draw call       │
│ drawImage (tree)    │       │                     │
│ drawImage (tree)    │       │ Batch:              │
│ ... × 200           │       │   200 sprites       │
│                     │       │   tree texture      │
│ Total: 700 calls    │       │   1 draw call       │
│ Frame time: 80ms    │       │                     │
└─────────────────────┘       │ Total: 2 calls      │
                              │ Frame time: 3ms     │
                              └─────────────────────┘
```

The rule: **same texture = same batch**. Use spritesheets (texture atlases) to keep everything on one texture.

## Loading a Spritesheet

```typescript
// src/engine/assets.ts
import { Assets, Spritesheet, Texture } from 'pixi.js';

export async function loadSpritesheet(
  imagePath: string,
  atlasData: object
): Promise<Spritesheet> {
  const texture = await Assets.load(imagePath);
  const sheet = new Spritesheet(texture, atlasData);
  await sheet.parse();
  return sheet;
}

// Atlas data describes where each tile lives in the spritesheet
const tileAtlasData = {
  frames: {
    'grass': { frame: { x: 0, y: 0, w: 64, h: 32 } },
    'dirt':  { frame: { x: 64, y: 0, w: 64, h: 32 } },
    'water': { frame: { x: 128, y: 0, w: 64, h: 32 } },
    'road':  { frame: { x: 192, y: 0, w: 64, h: 32 } },
  },
  meta: {
    image: 'tiles.png',
    size: { w: 256, h: 32 },
    scale: 1,
  },
};
```

## Viewport Culling

Even with batching, sending 10,000 sprites to the GPU when only 400 are visible is wasteful. Cull sprites outside the viewport:

```typescript
// src/engine/culling.ts
export class ViewportCuller {
  private viewX = 0;
  private viewY = 0;
  private viewW = 0;
  private viewH = 0;
  private margin = 64; // Extra margin to avoid pop-in

  updateViewport(camera: Camera, screenW: number, screenH: number) {
    this.viewX = camera.x - this.margin;
    this.viewY = camera.y - this.margin;
    this.viewW = screenW + this.margin * 2;
    this.viewH = screenH + this.margin * 2;
  }

  isVisible(sprite: { x: number; y: number; width: number; height: number }): boolean {
    return (
      sprite.x + sprite.width > this.viewX &&
      sprite.x < this.viewX + this.viewW &&
      sprite.y + sprite.height > this.viewY &&
      sprite.y < this.viewY + this.viewH
    );
  }

  cullContainer(container: Container) {
    for (const child of container.children) {
      const sprite = child as Sprite;
      sprite.visible = this.isVisible(sprite);
    }
  }
}
```

Call it every frame:

```typescript
function update() {
  culler.updateViewport(camera, app.screen.width, app.screen.height);
  culler.cullContainer(isoStage.terrainLayer);
  culler.cullContainer(isoStage.buildingLayer);
}
```

## Dirty Flag Optimization

Not everything changes every frame. If the camera hasn't moved and no buildings were placed, skip re-sorting and re-culling:

```typescript
// src/engine/dirty-tracker.ts
export class DirtyTracker {
  private _cameraMoved = false;
  private _buildingsChanged = false;
  private _terrainChanged = false;

  markCameraMoved() { this._cameraMoved = true; }
  markBuildingsChanged() { this._buildingsChanged = true; }
  markTerrainChanged() { this._terrainChanged = true; }

  get needsCullingUpdate(): boolean {
    return this._cameraMoved;
  }

  get needsDepthSort(): boolean {
    return this._buildingsChanged;
  }

  reset() {
    this._cameraMoved = false;
    this._buildingsChanged = false;
    this._terrainChanged = false;
  }
}

// In game loop:
function update() {
  if (dirty.needsCullingUpdate) {
    culler.updateViewport(camera, app.screen.width, app.screen.height);
    culler.cullContainer(isoStage.terrainLayer);
    culler.cullContainer(isoStage.buildingLayer);
  }

  if (dirty.needsDepthSort) {
    isoStage.buildingLayer.sortChildren();
  }

  dirty.reset();
}
```

## Performance Results

After migrating to PixiJS with culling:

```
Before (Canvas 2D, 500 buildings):
  Draw calls: 812
  Frame time: 83ms (12 FPS)

After (PixiJS + culling):
  Draw calls: 3
  Frame time: 4ms (250 FPS, vsync caps at 60)
  Visible sprites: ~400 of 900 total
```

The game is smooth again. Even with 2000 buildings, it holds 60 FPS.

## Keeping Canvas as Fallback

Some players have old hardware without WebGL. Keep the Canvas renderer as a fallback:

```typescript
// src/engine/renderer-factory.ts
export function createRenderer(canvas: HTMLCanvasElement): Renderer {
  if (isWebGLSupported()) {
    return new PixiRenderer(canvas);
  }
  console.warn('WebGL not supported, falling back to Canvas 2D');
  return new CanvasRenderer(canvas);
}

function isWebGLSupported(): boolean {
  try {
    const testCanvas = document.createElement('canvas');
    return !!(testCanvas.getContext('webgl2') || testCanvas.getContext('webgl'));
  } catch {
    return false;
  }
}
```

## Riku's Reaction

You show Riku the FPS counter: solid 60 with 1000 buildings on screen.

Riku: "Smooth. Now I want little people walking between buildings. Like, NPCs that find their way around obstacles."

You: "Pathfinding. A* on the isometric grid. Let's do it."

## What You Built

- **Identified the bottleneck** — too many individual `drawImage` calls
- **Migrated to PixiJS** — WebGL-accelerated sprite rendering
- **Sprite batching** — same texture = same draw call, 800 calls → 3
- **Spritesheet loading** — all tiles on one texture for maximum batching
- **Viewport culling** — hide sprites outside the camera view
- **Dirty tracking** — skip expensive operations when nothing changed
- **Fallback strategy** — Canvas 2D for devices without WebGL

From 12 FPS to 60 FPS. The city can grow. Next: giving it life with walking NPCs.

---

[← Chapter 11: Build Mode](chapter-11-build-mode.md) | [Chapter 13: Pathfinding →](chapter-13-pathfinding.md)
