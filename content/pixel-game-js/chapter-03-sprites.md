# Sprites

[prev: Game Loop](./chapter-02-game-loop.md) | [next: Tilemaps](./chapter-04-tilemap.md)

Sprites are the visual building blocks of pixel games — animated characters, enemies, items, and effects all built from sprite sheets.

## Loading Sprite Sheets

A sprite sheet packs multiple frames into one image:

```
+----+----+----+----+
| 0  | 1  | 2  | 3  |  <- idle animation
+----+----+----+----+
| 4  | 5  | 6  | 7  |  <- run animation
+----+----+----+----+
| 8  | 9  | 10 | 11 |  <- jump animation
+----+----+----+----+
  16px wide each
```

```typescript
const spriteSheet = await loadImage("characters.png");
const TILE_SIZE = 16;

function drawFrame(frameX: number, frameY: number, destX: number, destY: number) {
  ctx.drawImage(
    spriteSheet,
    frameX * TILE_SIZE,
    frameY * TILE_SIZE,
    TILE_SIZE,
    TILE_SIZE,
    Math.floor(destX),
    Math.floor(destY),
    TILE_SIZE,
    TILE_SIZE,
  );
}
```

## Animation

```typescript
interface Animation {
  frames: number[]; // frame indices in the row
  row: number; // which row in the sheet
  speed: number; // frames per second
  loop: boolean;
}

class AnimatedSprite {
  x = 0;
  y = 0;
  currentAnim: Animation;
  frameIndex = 0;
  timer = 0;

  constructor(public anims: Record<string, Animation>) {
    this.currentAnim = Object.values(anims)[0];
  }

  play(name: string) {
    const anim = this.anims[name];
    if (this.currentAnim !== anim) {
      this.currentAnim = anim;
      this.frameIndex = 0;
      this.timer = 0;
    }
  }

  update(dt: number) {
    this.timer += dt;
    const frameDuration = 1 / this.currentAnim.speed;
    if (this.timer >= frameDuration) {
      this.timer -= frameDuration;
      this.frameIndex++;
      if (this.frameIndex >= this.currentAnim.frames.length) {
        this.frameIndex = this.currentAnim.loop ? 0 : this.currentAnim.frames.length - 1;
      }
    }
  }

  draw(ctx: CanvasRenderingContext2D) {
    const frame = this.currentAnim.frames[this.frameIndex];
    ctx.drawImage(
      spriteSheet,
      frame * TILE_SIZE,
      this.currentAnim.row * TILE_SIZE,
      TILE_SIZE,
      TILE_SIZE,
      Math.floor(this.x),
      Math.floor(this.y),
      TILE_SIZE,
      TILE_SIZE,
    );
  }
}

// Usage
const player = new AnimatedSprite({
  idle: { frames: [0, 1, 2, 3], row: 0, speed: 4, loop: true },
  run: { frames: [0, 1, 2, 3, 4, 5], row: 1, speed: 10, loop: true },
  jump: { frames: [0, 1], row: 2, speed: 6, loop: false },
});
player.play("idle");
```

## Sprite Class with Physics

```typescript
class Sprite {
  x = 0;
  y = 0;
  vx = 0;
  vy = 0;
  width = 16;
  height = 16;
  flipX = false;

  update(dt: number) {
    this.x += this.vx * dt;
    this.y += this.vy * dt;
  }

  draw(ctx: CanvasRenderingContext2D, img: HTMLImageElement, frameX: number, frameY: number) {
    ctx.save();
    if (this.flipX) {
      ctx.translate(Math.floor(this.x) + this.width, Math.floor(this.y));
      ctx.scale(-1, 1);
      ctx.drawImage(img, frameX, frameY, this.width, this.height, 0, 0, this.width, this.height);
    } else {
      ctx.drawImage(
        img,
        frameX,
        frameY,
        this.width,
        this.height,
        Math.floor(this.x),
        Math.floor(this.y),
        this.width,
        this.height,
      );
    }
    ctx.restore();
  }

  getBounds() {
    return { x: this.x, y: this.y, w: this.width, h: this.height };
  }
}
```

## Collision Detection (AABB)

Axis-Aligned Bounding Box — the simplest and fastest collision check:

```typescript
function aabb(
  a: { x: number; y: number; w: number; h: number },
  b: { x: number; y: number; w: number; h: number },
): boolean {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

// Usage
if (aabb(player.getBounds(), coin.getBounds())) {
  collectCoin(coin);
}
```

```
  +-------+
  |   A   |     +-------+
  |       |     |   B   |   No overlap = no collision
  +-------+     +-------+

  +-------+
  |   A +---+
  |     | X |   Overlap = collision!
  +-----+   |
        | B |
        +---+
```

## Pixel-Perfect Collision

For precise collision, check actual pixel overlap:

```typescript
function pixelCollision(
  imgA: ImageData,
  ax: number,
  ay: number,
  imgB: ImageData,
  bx: number,
  by: number,
  w: number,
  h: number,
): boolean {
  // First do AABB check (fast reject)
  const left = Math.max(ax, bx);
  const top = Math.max(ay, by);
  const right = Math.min(ax + w, bx + w);
  const bottom = Math.min(ay + h, by + h);

  if (left >= right || top >= bottom) return false;

  // Check overlapping pixels
  for (let y = top; y < bottom; y++) {
    for (let x = left; x < right; x++) {
      const aIdx = ((y - ay) * w + (x - ax)) * 4 + 3; // alpha channel
      const bIdx = ((y - by) * w + (x - bx)) * 4 + 3;
      if (imgA.data[aIdx] > 0 && imgB.data[bIdx] > 0) return true;
    }
  }
  return false;
}
```

## Sprite Flipping

Flip a sprite horizontally using canvas transforms:

```typescript
function drawFlipped(img: HTMLImageElement, x: number, y: number, w: number, h: number) {
  ctx.save();
  ctx.translate(x + w, y);
  ctx.scale(-1, 1);
  ctx.drawImage(img, 0, 0, w, h, 0, 0, w, h);
  ctx.restore();
}
```

## Scaling Pixel Art Without Blur

The key rules:

1. Set `image-rendering: pixelated` on the canvas CSS
2. Set `ctx.imageSmoothingEnabled = false`
3. Only scale by integer multiples (2x, 3x, 4x)
4. Use `Math.floor()` for all positions

```typescript
// Scale a 16x16 sprite to 32x32 (2x) without blur
ctx.imageSmoothingEnabled = false;
ctx.drawImage(img, srcX, srcY, 16, 16, destX, destY, 32, 32);
```

## Complete Example: Animated Character

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
canvas.width = 160;
canvas.height = 144;
ctx.imageSmoothingEnabled = false;

const keys: Record<string, boolean> = {};
window.addEventListener("keydown", (e) => {
  keys[e.code] = true;
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

let sheet: HTMLImageElement;
let px = 72,
  py = 100,
  frame = 0,
  timer = 0,
  flipX = false;

async function init() {
  sheet = await loadImage("player.png"); // 4 frames, 16x16 each
  requestAnimationFrame(loop);
}

let lastTime = 0;
function loop(t: number) {
  const dt = (t - lastTime) / 1000;
  lastTime = t;

  // Move
  let moving = false;
  if (keys["ArrowLeft"]) {
    px -= 60 * dt;
    flipX = true;
    moving = true;
  }
  if (keys["ArrowRight"]) {
    px += 60 * dt;
    flipX = false;
    moving = true;
  }

  // Animate
  if (moving) {
    timer += dt;
    if (timer > 0.1) {
      timer = 0;
      frame = (frame + 1) % 4;
    }
  } else {
    frame = 0;
  }

  // Draw
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, 160, 144);
  ctx.save();
  if (flipX) {
    ctx.translate(Math.floor(px) + 16, Math.floor(py));
    ctx.scale(-1, 1);
    ctx.drawImage(sheet, frame * 16, 0, 16, 16, 0, 0, 16, 16);
  } else {
    ctx.drawImage(sheet, frame * 16, 0, 16, 16, Math.floor(px), Math.floor(py), 16, 16);
  }
  ctx.restore();

  requestAnimationFrame(loop);
}
init();
```

[prev: Game Loop](./chapter-02-game-loop.md) | [next: Tilemaps](./chapter-04-tilemap.md)
