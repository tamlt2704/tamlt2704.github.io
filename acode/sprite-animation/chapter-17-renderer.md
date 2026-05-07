# Chapter 17: Sprite Renderer — Drawing Frames on Canvas

[← Chapter 16: Sprite Sheets](chapter-16-sprite-sheets.md) | [Chapter 18: State Machine →](chapter-18-state-machine.md)

---

## The Problem

You have `ember-sheet.png` and `ember-sheet.json`. You call `ctx.drawImage(sheet, 0, 0)`. The entire sprite sheet renders — all 45 frames at once. You need to show ONE frame at a time, cycling through them at the right speed.

Riku opens a code editor:

> "Canvas `drawImage` has a 9-argument form that clips a rectangle from the source image. Specify which 32×32 region to grab from the sheet, where to place it on screen. Combine with `requestAnimationFrame` and a timer, and you have animation."

---

## The Principle: Source Rectangle Clipping

```
ctx.drawImage(image, sx, sy, sw, sh, dx, dy, dw, dh)

Source (sprite sheet):              Destination (canvas):
┌────┬────┬────┬────┐              ┌──────────────────┐
│    │ ██ │    │    │              │                  │
│    │████│    │    │              │       ██         │
├────┼────┼────┼────┤              │      ████        │
│    │    │    │    │              │                  │
└────┴────┴────┴────┘              └──────────────────┘
      ↑ sx,sy=(32,0)                      ↑ dx,dy=(200,100)
```

---

## Step-by-Step: Building the Renderer

### Step 1: Load the Sprite Sheet

```typescript
interface SpriteFrame { x: number; y: number; w: number; h: number; duration: number; }
interface AnimationTag { name: string; from: number; to: number; }
interface SpriteData { frames: SpriteFrame[]; tags: AnimationTag[]; }

async function loadSpriteSheet(imagePath: string, jsonPath: string) {
  const image = new Image();
  image.src = imagePath;
  await new Promise(resolve => image.onload = resolve);

  const raw = await (await fetch(jsonPath)).json();
  const frames: SpriteFrame[] = raw.frames.map((f: any) => ({
    x: f.frame.x, y: f.frame.y, w: f.frame.w, h: f.frame.h, duration: f.duration,
  }));
  const tags: AnimationTag[] = raw.meta.frameTags.map((t: any) => ({
    name: t.name, from: t.from, to: t.to,
  }));
  return { image, data: { frames, tags } };
}
```

### Step 2: The SpriteAnimator Class

```typescript
class SpriteAnimator {
  private image: HTMLImageElement;
  private frames: SpriteFrame[];
  private tags: Map<string, AnimationTag>;
  private currentTag!: AnimationTag;
  private currentFrame = 0;
  private elapsed = 0;
  private loop = true;
  private finished = false;
  speed = 1.0;

  constructor(image: HTMLImageElement, data: SpriteData) {
    this.image = image;
    this.frames = data.frames;
    this.tags = new Map(data.tags.map(t => [t.name, t]));
    this.play(data.tags[0].name);
  }

  play(name: string, loop = true): void {
    const tag = this.tags.get(name);
    if (!tag) throw new Error(`Animation "${name}" not found`);
    if (this.currentTag === tag && !this.finished) return;
    this.currentTag = tag;
    this.currentFrame = tag.from;
    this.elapsed = 0;
    this.loop = loop;
    this.finished = false;
  }

  update(deltaTime: number): void {
    if (this.finished) return;
    this.elapsed += deltaTime * this.speed;
    const dur = this.frames[this.currentFrame].duration;
    while (this.elapsed >= dur) {
      this.elapsed -= dur;
      this.currentFrame++;
      if (this.currentFrame > this.currentTag.to) {
        if (this.loop) { this.currentFrame = this.currentTag.from; }
        else { this.currentFrame = this.currentTag.to; this.finished = true; }
      }
    }
  }

  draw(ctx: CanvasRenderingContext2D, x: number, y: number): void {
    const f = this.frames[this.currentFrame];
    ctx.drawImage(this.image, f.x, f.y, f.w, f.h, x, y, f.w, f.h);
  }

  isFinished(): boolean { return this.finished; }
}
```

### Step 3: The Game Loop

```typescript
class Game {
  private canvas = document.getElementById('game') as HTMLCanvasElement;
  private ctx = this.canvas.getContext('2d')!;
  private animator!: SpriteAnimator;
  private lastTime = 0;

  async init(): Promise<void> {
    this.ctx.imageSmoothingEnabled = false; // CRITICAL for pixel art
    const { image, data } = await loadSpriteSheet('assets/ember-sheet.png', 'assets/ember-sheet.json');
    this.animator = new SpriteAnimator(image, data);
    this.animator.play('idle');
    requestAnimationFrame(this.loop.bind(this));
  }

  private loop(timestamp: number): void {
    const deltaTime = timestamp - this.lastTime;
    this.lastTime = timestamp;
    this.animator.update(deltaTime);
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.animator.draw(this.ctx, 100, 100);
    requestAnimationFrame(this.loop.bind(this));
  }
}
new Game().init();
```

### Crisp Pixel Art Rendering

```typescript
ctx.imageSmoothingEnabled = false;
// CSS: canvas { image-rendering: pixelated; }
// For 3x scale: canvas.style.width = `${canvas.width * 3}px`;
```

---

## The Mistake You'll Make

The animation runs too fast on 144Hz and too slow on 30fps. Speed is tied to frame rate.

> "You're advancing one frame per `requestAnimationFrame`. On 144Hz that's 144 advances/second. You need **delta time**."

Our implementation already handles this — `elapsed += deltaTime` accumulates real milliseconds. The `while` loop handles hitches (if deltaTime > frame duration, advance multiple frames).

---

## Animation Speed Control

```typescript
animator.speed = 0.5; // Slow motion
animator.speed = 1.5; // Haste power-up
animator.speed = 1.0; // Normal
```

The `speed` multiplier scales deltaTime before accumulation.

---

## Quick Reference

| Concept | Implementation |
|---|---|
| Load sheet | `new Image()` + `fetch()` for JSON |
| Draw frame | `ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh)` |
| Frame timing | Accumulate deltaTime, advance when >= duration |
| Crisp pixels | `imageSmoothingEnabled = false` + CSS `image-rendering: pixelated` |
| Scaling | CSS width/height on canvas OR `ctx.scale()` |
| Speed control | Multiply deltaTime by speed factor |
| One-shot | `loop = false`, stop at last frame |
| Delta time | `timestamp - lastTimestamp` from requestAnimationFrame |

---

## Exercise: Build the Sprite Renderer

1. Create an HTML file with a `<canvas>` element
2. Implement `loadSpriteSheet()` — load your exported PNG + JSON
3. Implement `SpriteAnimator` with `play()`, `update()`, `draw()`
4. Set up the game loop with `requestAnimationFrame`
5. Add keyboard controls to switch animations:

```typescript
document.addEventListener('keydown', (e) => {
  switch (e.key) {
    case '1': animator.play('idle'); break;
    case '2': animator.play('walk'); break;
    case '3': animator.play('run'); break;
    case '4': animator.play('jump', false); break;
    case '5': animator.play('attack', false); break;
  }
});
```

6. Verify speed is consistent across different refresh rates

**Success criteria**: Number keys switch animations. One-shots play once and hold. Idle loops seamlessly. Speed is frame-rate independent.

---

[← Chapter 16: Sprite Sheets](chapter-16-sprite-sheets.md) | [Chapter 18: State Machine →](chapter-18-state-machine.md)
