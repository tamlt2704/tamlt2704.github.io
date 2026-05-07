# Chapter 10: Animated Tiles

[← Chapter 9: Terrain](chapter-09-terrain.md) | [Chapter 11: Build Mode →](chapter-11-build-mode.md)

---

## The Task

The water tiles are static. In every isometric game Riku references — SimCity, Banished, Kingdoms and Castles — water shimmers, flags wave, smoke drifts from chimneys. Static tiles feel lifeless.

Riku delivers a water spritesheet: 4 frames of a 64×32 water tile, arranged horizontally in a single PNG. "Cycle through these. Make it look alive."

## Sprite Sheet Animation Basics

An animated tile is a sequence of frames in a spritesheet:

```
┌────────┬────────┬────────┬────────┐
│ Frame 0│ Frame 1│ Frame 2│ Frame 3│   water_anim.png
│  64×32 │  64×32 │  64×32 │  64×32 │   256×32 total
└────────┴────────┴────────┴────────┘
```

To animate: draw one frame at a time, advancing to the next frame at a fixed interval.

```typescript
// src/engine/animation.ts
export class SpriteAnimation {
  private image: HTMLImageElement;
  private frameWidth: number;
  private frameHeight: number;
  private frameCount: number;
  private frameDuration: number; // Seconds per frame
  private elapsed = 0;
  private currentFrame = 0;

  constructor(
    image: HTMLImageElement,
    frameWidth: number,
    frameHeight: number,
    frameCount: number,
    frameDuration: number
  ) {
    this.image = image;
    this.frameWidth = frameWidth;
    this.frameHeight = frameHeight;
    this.frameCount = frameCount;
    this.frameDuration = frameDuration;
  }

  update(dt: number) {
    this.elapsed += dt;
    if (this.elapsed >= this.frameDuration) {
      this.elapsed -= this.frameDuration;
      this.currentFrame = (this.currentFrame + 1) % this.frameCount;
    }
  }

  draw(ctx: CanvasRenderingContext2D, destX: number, destY: number) {
    const srcX = this.currentFrame * this.frameWidth;

    ctx.drawImage(
      this.image,
      srcX, 0, this.frameWidth, this.frameHeight,  // Source rect
      destX, destY, this.frameWidth, this.frameHeight // Dest rect
    );
  }

  get frame(): number {
    return this.currentFrame;
  }
}
```

## Frame Timing Independent of Game Loop

The game loop runs at 60fps (16.6ms per frame). But water should animate at ~4fps (250ms per frame). Don't tie animation speed to frame rate:

```typescript
// WRONG: advances every frame (too fast at 60fps)
function update() {
  currentFrame = (currentFrame + 1) % frameCount;
}

// RIGHT: advances based on elapsed time
function update(dt: number) {
  elapsed += dt;
  while (elapsed >= frameDuration) {
    elapsed -= frameDuration;
    currentFrame = (currentFrame + 1) % frameCount;
  }
}
```

Using `while` instead of `if` handles the case where `dt` is larger than `frameDuration` (lag spike — skip frames rather than playing them all at once).

## Animating Water Tiles

Water tiles all share the same animation. Instead of creating a `SpriteAnimation` per tile, use one shared animation and draw it at multiple positions:

```typescript
// src/game/animated-terrain.ts
export class AnimatedTerrain {
  private animations: Map<string, SpriteAnimation> = new Map();

  register(terrainType: string, animation: SpriteAnimation) {
    this.animations.set(terrainType, animation);
  }

  update(dt: number) {
    for (const anim of this.animations.values()) {
      anim.update(dt);
    }
  }

  getAnimation(terrainType: string): SpriteAnimation | undefined {
    return this.animations.get(terrainType);
  }

  hasAnimation(terrainType: string): boolean {
    return this.animations.has(terrainType);
  }
}
```

Usage in the render loop:

```typescript
const animatedTerrain = new AnimatedTerrain();

async function init() {
  const waterSheet = await loadImage('/assets/tiles/water_anim.png');
  const waterAnim = new SpriteAnimation(waterSheet, TILE_W, TILE_H, 4, 0.25);
  animatedTerrain.register('water', waterAnim);
}

function update(dt: number) {
  animatedTerrain.update(dt);
}

function renderTile(x: number, y: number, tileType: string, offsetX: number, offsetY: number) {
  const { screenX, screenY } = cartToIso(x, y);
  const drawX = screenX + offsetX - TILE_W / 2;
  const drawY = screenY + offsetY - TILE_H / 2;

  if (animatedTerrain.hasAnimation(tileType)) {
    // Draw animated tile
    animatedTerrain.getAnimation(tileType)!.draw(ctx, drawX, drawY);
  } else {
    // Draw static tile
    atlas.drawTile(ctx, getTileId(tileType), drawX, drawY);
  }
}
```

## Staggered Animation

If all water tiles animate in sync, it looks mechanical. Add a per-tile offset to stagger the animation:

```typescript
export class StaggeredAnimation {
  private image: HTMLImageElement;
  private frameWidth: number;
  private frameHeight: number;
  private frameCount: number;
  private frameDuration: number;
  private globalTime = 0;

  constructor(
    image: HTMLImageElement,
    frameWidth: number,
    frameHeight: number,
    frameCount: number,
    frameDuration: number
  ) {
    this.image = image;
    this.frameWidth = frameWidth;
    this.frameHeight = frameHeight;
    this.frameCount = frameCount;
    this.frameDuration = frameDuration;
  }

  update(dt: number) {
    this.globalTime += dt;
  }

  draw(ctx: CanvasRenderingContext2D, destX: number, destY: number, tileX: number, tileY: number) {
    // Offset based on tile position for staggering
    const offset = ((tileX * 7 + tileY * 13) % this.frameCount) * this.frameDuration * 0.3;
    const adjustedTime = this.globalTime + offset;
    const frame = Math.floor(adjustedTime / this.frameDuration) % this.frameCount;

    const srcX = frame * this.frameWidth;

    ctx.drawImage(
      this.image,
      srcX, 0, this.frameWidth, this.frameHeight,
      destX, destY, this.frameWidth, this.frameHeight
    );
  }
}
```

Now each water tile is at a slightly different frame, creating a natural ripple effect across the lake.

## Smoke and Particle Effects on Buildings

Chimneys emit smoke. Factories have steam. These are small animated sprites drawn above buildings:

```typescript
// src/engine/particles.ts
interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  alpha: number;
}

export class SmokeEmitter {
  private particles: Particle[] = [];
  private worldX: number;
  private worldY: number;
  private emitRate: number;    // Particles per second
  private emitTimer = 0;

  constructor(worldX: number, worldY: number, emitRate = 3) {
    this.worldX = worldX;
    this.worldY = worldY;
    this.emitRate = emitRate;
  }

  update(dt: number) {
    // Emit new particles
    this.emitTimer += dt;
    const emitInterval = 1 / this.emitRate;
    while (this.emitTimer >= emitInterval) {
      this.emitTimer -= emitInterval;
      this.emit();
    }

    // Update existing particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.life -= dt;
      p.alpha = Math.max(0, p.life / p.maxLife);
      p.size += 8 * dt; // Grow over time

      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }

  private emit() {
    this.particles.push({
      x: this.worldX + (Math.random() - 0.5) * 4,
      y: this.worldY,
      vx: (Math.random() - 0.5) * 10,
      vy: -30 - Math.random() * 20, // Float upward
      life: 2 + Math.random(),
      maxLife: 3,
      size: 4 + Math.random() * 4,
      alpha: 0.6,
    });
  }

  draw(ctx: CanvasRenderingContext2D, cameraX: number, cameraY: number) {
    for (const p of this.particles) {
      const screenX = p.x - cameraX;
      const screenY = p.y - cameraY;

      ctx.beginPath();
      ctx.arc(screenX, screenY, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 200, 200, ${p.alpha * 0.5})`;
      ctx.fill();
    }
  }
}
```

Attach emitters to buildings:

```typescript
function createBuildingEmitters(buildings: PlacedBuilding[]): SmokeEmitter[] {
  const emitters: SmokeEmitter[] = [];

  for (const building of buildings) {
    if (building.def.id === 'factory') {
      // Place smoke at the chimney position (offset from building anchor)
      const { screenX, screenY } = cartToIso(building.anchorX, building.anchorY);
      const chimneyX = screenX + worldOffsetX + 10;
      const chimneyY = screenY + worldOffsetY - building.def.spriteHeight + 20;
      emitters.push(new SmokeEmitter(chimneyX, chimneyY, 4));
    }
  }

  return emitters;
}
```

## The AnimatedTile Class

A reusable class for any tile that animates:

```typescript
// src/engine/animated-tile.ts
export interface AnimatedTileDef {
  image: HTMLImageElement;
  frameWidth: number;
  frameHeight: number;
  frameCount: number;
  frameDuration: number;  // Seconds per frame
  loop: boolean;
}

export class AnimatedTile {
  private def: AnimatedTileDef;
  private elapsed = 0;
  private currentFrame = 0;
  private finished = false;

  constructor(def: AnimatedTileDef) {
    this.def = def;
  }

  update(dt: number) {
    if (this.finished) return;

    this.elapsed += dt;
    while (this.elapsed >= this.def.frameDuration) {
      this.elapsed -= this.def.frameDuration;
      this.currentFrame++;

      if (this.currentFrame >= this.def.frameCount) {
        if (this.def.loop) {
          this.currentFrame = 0;
        } else {
          this.currentFrame = this.def.frameCount - 1;
          this.finished = true;
        }
      }
    }
  }

  draw(ctx: CanvasRenderingContext2D, destX: number, destY: number) {
    const srcX = this.currentFrame * this.def.frameWidth;
    const srcY = 0;

    ctx.drawImage(
      this.def.image,
      srcX, srcY, this.def.frameWidth, this.def.frameHeight,
      destX, destY, this.def.frameWidth, this.def.frameHeight
    );
  }

  reset() {
    this.currentFrame = 0;
    this.elapsed = 0;
    this.finished = false;
  }

  get isFinished(): boolean {
    return this.finished;
  }
}
```

## Registering Animated Tiles from Tiled

Tiled supports animated tiles natively. The tileset JSON includes animation data:

```json
{
  "tiles": [
    {
      "id": 4,
      "animation": [
        { "tileid": 4, "duration": 250 },
        { "tileid": 5, "duration": 250 },
        { "tileid": 6, "duration": 250 },
        { "tileid": 7, "duration": 250 }
      ]
    }
  ]
}
```

Parse this to auto-detect animated tiles:

```typescript
interface TiledAnimationFrame {
  tileid: number;
  duration: number; // milliseconds
}

interface TiledTileData {
  id: number;
  animation?: TiledAnimationFrame[];
}

function parseAnimatedTiles(
  tilesetData: { tiles?: TiledTileData[] },
  atlas: TileAtlas
): Map<number, AnimatedTileDef> {
  const animatedTiles = new Map<number, AnimatedTileDef>();

  if (!tilesetData.tiles) return animatedTiles;

  for (const tile of tilesetData.tiles) {
    if (tile.animation && tile.animation.length > 0) {
      // This tile is animated
      animatedTiles.set(tile.id, {
        image: atlas.image,
        frameWidth: TILE_W,
        frameHeight: TILE_H,
        frameCount: tile.animation.length,
        frameDuration: tile.animation[0].duration / 1000, // ms → seconds
        loop: true,
      });
    }
  }

  return animatedTiles;
}
```

## Performance: Only Animate Visible Tiles

With a 50×50 map, hundreds of water tiles might be animating. Only update and draw tiles within the camera viewport:

```typescript
function getVisibleRange(camera: Camera, canvasW: number, canvasH: number) {
  // Convert screen corners to grid coordinates
  const topLeft = isoToCart(camera.x - worldOffsetX, camera.y - worldOffsetY);
  const bottomRight = isoToCart(
    camera.x + canvasW - worldOffsetX,
    camera.y + canvasH - worldOffsetY
  );

  return {
    minX: Math.max(0, topLeft.x - 2),
    minY: Math.max(0, topLeft.y - 2),
    maxX: Math.min(terrainMap.width - 1, bottomRight.x + 2),
    maxY: Math.min(terrainMap.height - 1, bottomRight.y + 2),
  };
}
```

This is a rough culling pass. For animated tiles specifically, the shared animation state (one `SpriteAnimation` per type) means the update cost is constant regardless of how many tiles are visible — only the draw calls scale.

## Putting It Together

```typescript
// src/main.ts
import { SpriteAnimation } from './engine/animation';
import { SmokeEmitter } from './engine/particles';
import { AnimatedTerrain } from './game/animated-terrain';

const animatedTerrain = new AnimatedTerrain();
let smokeEmitters: SmokeEmitter[] = [];

async function init() {
  // Load animated spritesheets
  const waterSheet = await loadImage('/assets/tiles/water_anim.png');
  animatedTerrain.register('water', new SpriteAnimation(waterSheet, 64, 32, 4, 0.25));

  // Set up smoke emitters for factories
  smokeEmitters = createBuildingEmitters(buildingManager.buildings);

  requestAnimationFrame(gameLoop);
}

function update(dt: number) {
  // Update all animations
  animatedTerrain.update(dt);

  // Update particle emitters
  for (const emitter of smokeEmitters) {
    emitter.update(dt);
  }
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.save();
  ctx.translate(-camera.x, -camera.y);

  // Render terrain (animated tiles handled automatically)
  for (let sum = 0; sum < terrainMap.width + terrainMap.height - 1; sum++) {
    for (let x = 0; x <= sum; x++) {
      const y = sum - x;
      if (x >= terrainMap.width || y >= terrainMap.height) continue;

      const tileType = terrainMap.get(x, y);
      const { screenX, screenY } = cartToIso(x, y);
      const drawX = screenX + worldOffsetX - TILE_W / 2;
      const drawY = screenY + worldOffsetY - TILE_H / 2;

      if (animatedTerrain.hasAnimation(tileType === Terrain.Water ? 'water' : '')) {
        animatedTerrain.getAnimation('water')!.draw(ctx, drawX, drawY);
      } else {
        atlas.drawTile(ctx, getAutoTileId(terrainMap, x, y), drawX, drawY);
      }
    }
  }

  // Render buildings
  renderBuildings();

  // Render smoke particles (on top of buildings)
  for (const emitter of smokeEmitters) {
    emitter.draw(ctx, camera.x, camera.y);
  }

  ctx.restore();
}
```

## Riku's Reaction

The water shimmers. Smoke drifts from the factory chimney. The world feels alive.

Riku: "Now I want to actually *play* it. Let me pick a building from a menu and place it on the map. Drag to place roads. A proper build mode."

You: "Build mode. Ghost preview, snap to grid, validation. We already have the pieces — placement checking, highlight rendering, click handling. Time to wire them into a proper UI flow."

## What You Built

- **SpriteAnimation** — frame-based animation with time-independent updates
- **Frame timing** — `elapsed += dt` with `while` loop for frame skipping
- **Shared animations** — one animation state drives all tiles of the same type
- **Staggered animation** — per-tile offset prevents mechanical synchronization
- **Smoke particles** — simple emitter with velocity, fade, and growth
- **AnimatedTile class** — reusable, supports loop and one-shot modes
- **Tiled integration** — parse animation data from tileset JSON
- **Viewport culling** — only draw animated tiles the player can see

The world breathes. Next: letting the player build in it.

---

[← Chapter 9: Terrain](chapter-09-terrain.md) | [Chapter 11: Build Mode →](chapter-11-build-mode.md)
