# Polish

[prev: RPG Project](./chapter-08-rpg.md) | [next: Publishing](./chapter-10-publish.md)

Polish is what makes a game feel good. Screen shake, particles, tweening, and sound design turn a functional prototype into something players love.

## Screen Shake

```typescript
const shake = { x: 0, y: 0, intensity: 0, duration: 0 };

function startShake(intensity: number, duration: number) {
  shake.intensity = intensity;
  shake.duration = duration;
}

function updateShake(dt: number) {
  if (shake.duration > 0) {
    shake.duration -= dt;
    shake.x = (Math.random() - 0.5) * 2 * shake.intensity;
    shake.y = (Math.random() - 0.5) * 2 * shake.intensity;
  } else {
    shake.x = 0;
    shake.y = 0;
  }
}

function render() {
  ctx.save();
  ctx.translate(Math.round(shake.x), Math.round(shake.y));
  // ... draw everything ...
  ctx.restore();
}

// Usage: startShake(3, 0.2) on hit
```

## Particle Effects

```typescript
interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  color: string;
  size: number;
}

const particles: Particle[] = [];

function emit(x: number, y: number, count: number, color: string) {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 20 + Math.random() * 60;
    particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 0.3 + Math.random() * 0.3,
      maxLife: 0.5,
      color,
      size: 1 + Math.floor(Math.random() * 2),
    });
  }
}

function updateParticles(dt: number) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.vy += 100 * dt; // gravity
    p.life -= dt;
    if (p.life <= 0) particles.splice(i, 1);
  }
}

function renderParticles(ctx: CanvasRenderingContext2D) {
  for (const p of particles) {
    const alpha = p.life / p.maxLife;
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.fillRect(Math.floor(p.x), Math.floor(p.y), p.size, p.size);
  }
  ctx.globalAlpha = 1;
}

// Usage: emit(enemy.x + 7, enemy.y + 7, 8, '#e94560')
```

## Tweening

Smooth value transitions for UI, movement, and effects:

```typescript
type EaseFn = (t: number) => number;

const ease = {
  linear: (t: number) => t,
  inQuad: (t: number) => t * t,
  outQuad: (t: number) => t * (2 - t),
  inOutQuad: (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
  outBack: (t: number) => {
    const s = 1.70158;
    return (t -= 1) * t * ((s + 1) * t + s) + 1;
  },
  outBounce: (t: number) => {
    if (t < 1 / 2.75) return 7.5625 * t * t;
    if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
    if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
    return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
  },
};

interface Tween {
  target: any;
  prop: string;
  from: number;
  to: number;
  duration: number;
  elapsed: number;
  ease: EaseFn;
  onComplete?: () => void;
}

const tweens: Tween[] = [];

function tween(
  target: any,
  prop: string,
  to: number,
  duration: number,
  easeFn: EaseFn = ease.outQuad,
  onComplete?: () => void,
) {
  tweens.push({
    target,
    prop,
    from: target[prop],
    to,
    duration,
    elapsed: 0,
    ease: easeFn,
    onComplete,
  });
}

function updateTweens(dt: number) {
  for (let i = tweens.length - 1; i >= 0; i--) {
    const tw = tweens[i];
    tw.elapsed += dt;
    const t = Math.min(tw.elapsed / tw.duration, 1);
    tw.target[tw.prop] = tw.from + (tw.to - tw.from) * tw.ease(t);
    if (t >= 1) {
      tw.onComplete?.();
      tweens.splice(i, 1);
    }
  }
}

// Usage: tween(player, 'y', player.y - 4, 0.1, ease.outQuad, () => tween(player, 'y', player.y + 4, 0.1))
```

## Juice: Squash and Stretch

```typescript
class JuicySprite {
  x = 0;
  y = 0;
  scaleX = 1;
  scaleY = 1;

  squash() {
    this.scaleX = 1.3;
    this.scaleY = 0.7;
    tween(this, "scaleX", 1, 0.2, ease.outBounce);
    tween(this, "scaleY", 1, 0.2, ease.outBounce);
  }

  stretch() {
    this.scaleX = 0.7;
    this.scaleY = 1.3;
    tween(this, "scaleX", 1, 0.15, ease.outQuad);
    tween(this, "scaleY", 1, 0.15, ease.outQuad);
  }

  draw(ctx: CanvasRenderingContext2D, img: HTMLImageElement) {
    ctx.save();
    ctx.translate(Math.floor(this.x + 8), Math.floor(this.y + 16)); // pivot at feet
    ctx.scale(this.scaleX, this.scaleY);
    ctx.drawImage(img, -8, -16, 16, 16);
    ctx.restore();
  }
}

// On land: squash(). On jump: stretch().
```

## Hitstop (Freeze Frames)

```typescript
let hitstopTimer = 0;

function hitstop(duration: number) {
  hitstopTimer = duration;
}

function gameLoop(t: number) {
  const dt = Math.min((t - lastTime) / 1000, 0.1);
  lastTime = t;

  if (hitstopTimer > 0) {
    hitstopTimer -= dt;
    // Still render, just don't update
    render();
  } else {
    update(dt);
    render();
  }
  requestAnimationFrame(gameLoop);
}

// Usage: on enemy hit, hitstop(0.05) + startShake(2, 0.1)
```

## Bitmap Fonts

Pixel-perfect text using a font sprite sheet:

```typescript
const CHAR_W = 5,
  CHAR_H = 7;
const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.!?:,-";
let fontImg: HTMLImageElement;

function drawText(ctx: CanvasRenderingContext2D, text: string, x: number, y: number) {
  const upper = text.toUpperCase();
  for (let i = 0; i < upper.length; i++) {
    const idx = CHARS.indexOf(upper[i]);
    if (idx === -1) continue; // space or unknown
    ctx.drawImage(
      fontImg,
      idx * CHAR_W,
      0,
      CHAR_W,
      CHAR_H,
      x + i * (CHAR_W + 1),
      y,
      CHAR_W,
      CHAR_H,
    );
  }
}
```

## Sound with Howler.js

```bash
npm install howler
```

```typescript
import { Howl } from "howler";

const sounds = {
  jump: new Howl({ src: ["jump.wav"], volume: 0.3 }),
  coin: new Howl({ src: ["coin.wav"], volume: 0.4 }),
  hit: new Howl({ src: ["hit.wav"], volume: 0.5 }),
  music: new Howl({ src: ["music.ogg"], loop: true, volume: 0.2 }),
};

sounds.music.play();

// On jump:
sounds.jump.play();
```

## Music Loops

```typescript
// Seamless loop with Web Audio
const musicCtx = new AudioContext();
let musicBuffer: AudioBuffer;

async function loadMusic(url: string) {
  const res = await fetch(url);
  const data = await res.arrayBuffer();
  musicBuffer = await musicCtx.decodeAudioData(data);
}

function playMusic() {
  const source = musicCtx.createBufferSource();
  source.buffer = musicBuffer;
  source.loop = true;
  source.loopStart = 0;
  source.loopEnd = musicBuffer.duration;
  source.connect(musicCtx.destination);
  source.start();
}
```

## Retro CRT Shader Effect

Apply a CRT scanline effect by drawing over the final frame:

```typescript
function applyCRT(ctx: CanvasRenderingContext2D, w: number, h: number) {
  // Scanlines
  ctx.fillStyle = "rgba(0,0,0,0.15)";
  for (let y = 0; y < h; y += 2) {
    ctx.fillRect(0, y, w, 1);
  }

  // Vignette (darken edges)
  const grad = ctx.createRadialGradient(w / 2, h / 2, w * 0.3, w / 2, h / 2, w * 0.7);
  grad.addColorStop(0, "rgba(0,0,0,0)");
  grad.addColorStop(1, "rgba(0,0,0,0.4)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);
}

// Call after all game rendering:
function render() {
  // ... draw game ...
  applyCRT(ctx, canvas.width, canvas.height);
}
```

For a more advanced CRT with barrel distortion, use WebGL shaders:

```typescript
// Fragment shader (GLSL)
const crtShader = `
  precision mediump float;
  uniform sampler2D uTexture;
  varying vec2 vUv;

  void main() {
    vec2 uv = vUv;
    // Barrel distortion
    vec2 center = uv - 0.5;
    float dist = dot(center, center);
    uv = uv + center * dist * 0.1;
    // Scanlines
    float scanline = sin(uv.y * 144.0 * 3.14159) * 0.04;
    vec4 color = texture2D(uTexture, uv);
    color.rgb -= scanline;
    gl_FragColor = color;
  }
`;
```

## Combining Juice

The best game feel comes from layering multiple effects:

```
Player lands:
  1. Squash sprite (scaleX: 1.3, scaleY: 0.7)
  2. Emit dust particles (3-5, gray, spread horizontal)
  3. Small screen shake (intensity: 1, duration: 0.05)
  4. Play land sound

Enemy hit:
  1. Hitstop (0.04s)
  2. Screen shake (intensity: 3, duration: 0.1)
  3. Flash enemy white (1 frame)
  4. Emit particles (8, red)
  5. Knockback tween
  6. Play hit sound
```

[prev: RPG Project](./chapter-08-rpg.md) | [next: Publishing](./chapter-10-publish.md)
