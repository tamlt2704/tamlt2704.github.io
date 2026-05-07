# Chapter 19: Runtime Effects — Flip, Tint, Scale, and Swap

[← Chapter 18: State Machine](chapter-18-state-machine.md) | [Chapter 20: Game Feel →](chapter-20-game-feel.md)

---

## The Problem

Ember faces right. Player presses left. You'd need to redraw every animation mirrored — doubling your sprite sheet. Then an enemy hits Ember and you want the white flash from Chapter 11. But you can't change pixels of an image at 60fps... can you?

Riku opens the Canvas transform docs:

> "Canvas gives you transforms and compositing. Combined, they let you flip sprites, tint them any color, squash/stretch them, and swap palettes — all at runtime, without touching the source art."

---

## The Principle: Transform Stack

Canvas transforms are cumulative. Save, transform, draw, restore:

```typescript
ctx.save();           // Save current state
// ... apply transforms ...
ctx.drawImage(...);   // Draw with transforms applied
ctx.restore();        // Undo all transforms
```

---

## Effect 1: Horizontal Flip (Facing Direction)

```typescript
class SpriteAnimator {
  facingLeft: boolean = false;

  draw(ctx: CanvasRenderingContext2D, x: number, y: number): void {
    const frame = this.frames[this.currentFrame];

    if (this.facingLeft) {
      ctx.save();
      ctx.translate(x + frame.w, y);
      ctx.scale(-1, 1);
      ctx.drawImage(this.image, frame.x, frame.y, frame.w, frame.h, 0, 0, frame.w, frame.h);
      ctx.restore();
    } else {
      ctx.drawImage(this.image, frame.x, frame.y, frame.w, frame.h, x, y, frame.w, frame.h);
    }
  }
}
```

How it works: translate to the sprite's right edge, then `scale(-1, 1)` mirrors horizontally. Draw at (0,0) relative to the new origin.

---

## Effect 2: Flash White (Hit Feedback)

Render the sprite as a solid white silhouette for 1-2 frames using an offscreen canvas:

```typescript
class SpriteAnimator {
  flashWhite: boolean = false;
  private flashCanvas: HTMLCanvasElement;
  private flashCtx: CanvasRenderingContext2D;

  constructor(/* ... */) {
    this.flashCanvas = document.createElement('canvas');
    this.flashCanvas.width = 32;
    this.flashCanvas.height = 32;
    this.flashCtx = this.flashCanvas.getContext('2d')!;
  }

  private drawWhiteFlash(ctx: CanvasRenderingContext2D, x: number, y: number): void {
    const frame = this.frames[this.currentFrame];
    const fCtx = this.flashCtx;

    fCtx.clearRect(0, 0, 32, 32);
    fCtx.drawImage(this.image, frame.x, frame.y, frame.w, frame.h, 0, 0, frame.w, frame.h);

    // Fill white only where pixels exist
    fCtx.globalCompositeOperation = 'source-atop';
    fCtx.fillStyle = '#FFFFFF';
    fCtx.fillRect(0, 0, 32, 32);
    fCtx.globalCompositeOperation = 'source-over';

    ctx.drawImage(this.flashCanvas, x, y);
  }
}
```

Trigger: set `flashWhite = true` for 80ms on damage, then reset to false.

---

## Effect 3: Scale (Squash on Land)

Apply squash/stretch from the bottom-center pivot (feet stay planted):

```typescript
function drawScaled(
  ctx: CanvasRenderingContext2D, image: HTMLImageElement,
  sx: number, sy: number, sw: number, sh: number,
  dx: number, dy: number, scaleX: number, scaleY: number
): void {
  ctx.save();
  const pivotX = dx + sw / 2;
  const pivotY = dy + sh; // Bottom of sprite
  ctx.translate(pivotX, pivotY);
  ctx.scale(scaleX, scaleY);
  ctx.translate(-sw / 2, -sh);
  ctx.drawImage(image, sx, sy, sw, sh, 0, 0, sw, sh);
  ctx.restore();
}

// Landing squash: wider + shorter
drawScaled(ctx, image, sx, sy, 32, 32, x, y, 1.3, 0.7);

// Jump stretch: narrower + taller
drawScaled(ctx, image, sx, sy, 32, 32, x, y, 0.8, 1.2);
```

Animate recovery with lerp:

```typescript
// On land:
this.squash = { x: 1.3, y: 0.7 };

// Every frame:
this.squash.x += (1 - this.squash.x) * 8 * dt; // Lerp back to 1.0
this.squash.y += (1 - this.squash.y) * 8 * dt;
```

---

## Effect 4: Palette Swap (Recolor Enemies)

Create color variants at load time (NOT every frame):

```typescript
function createPaletteSwap(source: HTMLImageElement, colorMap: Map<string, string>): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = source.width; canvas.height = source.height;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(source, 0, 0);
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;

  for (let i = 0; i < data.length; i += 4) {
    const hex = `#${data[i].toString(16).padStart(2,'0')}${data[i+1].toString(16).padStart(2,'0')}${data[i+2].toString(16).padStart(2,'0')}`.toUpperCase();
    const replacement = colorMap.get(hex);
    if (replacement) {
      data[i] = parseInt(replacement.slice(1,3), 16);
      data[i+1] = parseInt(replacement.slice(3,5), 16);
      data[i+2] = parseInt(replacement.slice(5,7), 16);
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas; // Use as image source for blue slime, etc.
}
```

---

## Effect 5: Invincibility Blink

Toggle visibility every 60ms:

```typescript
// In update: if invincible, toggle this.visible every 60ms
// In draw: if (!this.visible) return;
// After timer expires: this.visible = true
```

---

## The Mistake You'll Make

You implement flash + flip. The combination breaks — the flash renders at the wrong position when flipped, or the flash persists because you forgot to reset the flag.

Riku reviews your draw function:

> "Each effect must be independent and composable. Build them as layers applied in order: flip → scale → tint → draw."

### The Fix: Composable Pipeline

```typescript
draw(ctx: CanvasRenderingContext2D, x: number, y: number): void {
  const frame = this.frames[this.currentFrame];
  ctx.save();

  // 1. Flip
  if (this.facingLeft) {
    ctx.translate(x + frame.w, y);
    ctx.scale(-1, 1);
    x = 0; y = 0;
  }

  // 2. Squash (from bottom center)
  if (this.squashX !== 1 || this.squashY !== 1) {
    ctx.translate(x + frame.w/2, y + frame.h);
    ctx.scale(this.squashX, this.squashY);
    ctx.translate(-frame.w/2, -frame.h);
    x = 0; y = 0;
  }

  // 3. Draw (normal or flash)
  if (this.flashWhite) { this.drawWhiteFlash(ctx, x, y); }
  else { ctx.drawImage(this.image, frame.x, frame.y, frame.w, frame.h, x, y, frame.w, frame.h); }

  ctx.restore();
}
```

---

## Quick Reference

| Effect | Technique | Cost |
|---|---|---|
| Flip | `ctx.scale(-1, 1)` + translate | Free (GPU) |
| White flash | Offscreen canvas + `source-atop` | Cheap |
| Squash/stretch | `ctx.scale(sx, sy)` from pivot | Free (GPU) |
| Palette swap | `getImageData` pixel swap | Once at load |
| Blink | Skip draw call | Free |

| Concept | Rule |
|---|---|
| Transform sandwich | save → transform → draw → restore |
| Pivot point | Translate to pivot, scale, translate back |
| Composable | Each effect independent, applied in order |
| Flash duration | 40-80ms (1-2 frames) |
| Squash recovery | Lerp to (1,1) over 100-200ms |
| Blink interval | 60ms toggle for 1 second |

---

## Exercise: Implement Runtime Effects

1. **Flip**: Track `facingLeft`, mirror sprite when moving left
2. **Flash**: White silhouette for 80ms on damage (offscreen canvas + source-atop)
3. **Squash**: On landing, scale (1.3, 0.7) then lerp back to (1, 1)
4. **Palette swap**: Create a blue variant of your slime at load time
5. **Blink**: 60ms on/off toggle for 1 second after hit

**Success criteria**: All effects work simultaneously. A hit should: flash white → knockback animation → blink. Flipping direction during any of this should work correctly.

---

[← Chapter 18: State Machine](chapter-18-state-machine.md) | [Chapter 20: Game Feel →](chapter-20-game-feel.md)
