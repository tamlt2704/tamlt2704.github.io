# Chapter 15: Lighting

[← Chapter 14: Camera & Zoom](chapter-14-camera-zoom.md) | [Chapter 16: HUD →](chapter-16-hud.md)

---

## The Task

Riku sends concept art: TinyTown at sunset, buildings casting warm light from windows, rain streaking across the screen. "The game needs atmosphere. A day/night cycle. Weather. Make it feel alive beyond just animation."

You've got a flat, evenly-lit city. Time to add mood.

## Global Tint Overlay

The simplest lighting: draw a colored rectangle over the entire scene with a blend mode. Dark blue at night, warm orange at sunset:

```typescript
// src/engine/lighting.ts
const TILE_W = 64;
const TILE_H = 32;

export interface TimeOfDay {
  hour: number;  // 0-24 (fractional)
}

export function getAmbientColor(time: TimeOfDay): { r: number; g: number; b: number; a: number } {
  const h = time.hour;

  if (h >= 6 && h < 8) {
    // Dawn: dark blue → warm orange
    const t = (h - 6) / 2;
    return lerpColor(
      { r: 20, g: 30, b: 80, a: 0.4 },
      { r: 255, g: 180, b: 80, a: 0.15 },
      t
    );
  } else if (h >= 8 && h < 17) {
    // Day: minimal tint
    return { r: 255, g: 255, b: 240, a: 0.02 };
  } else if (h >= 17 && h < 20) {
    // Sunset: warm orange → deep blue
    const t = (h - 17) / 3;
    return lerpColor(
      { r: 255, g: 140, b: 50, a: 0.2 },
      { r: 20, g: 20, b: 60, a: 0.5 },
      t
    );
  } else {
    // Night: dark blue overlay
    return { r: 10, g: 15, b: 50, a: 0.55 };
  }
}

function lerpColor(
  a: { r: number; g: number; b: number; a: number },
  b: { r: number; g: number; b: number; a: number },
  t: number
) {
  return {
    r: Math.round(a.r + (b.r - a.r) * t),
    g: Math.round(a.g + (b.g - a.g) * t),
    b: Math.round(a.b + (b.b - a.b) * t),
    a: a.a + (b.a - a.a) * t,
  };
}
```

Apply it with Canvas 2D:

```typescript
// After rendering the world, before HUD
function renderAmbientOverlay(ctx: CanvasRenderingContext2D, time: TimeOfDay) {
  const color = getAmbientColor(time);

  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a})`;
  ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ctx.restore();
}
```

With PixiJS, use a full-screen color overlay sprite:

```typescript
import { Graphics, Container, BLEND_MODES } from 'pixi.js';

export class AmbientOverlay {
  private overlay: Graphics;

  constructor(width: number, height: number) {
    this.overlay = new Graphics();
    this.overlay.blendMode = 'multiply';
    this.resize(width, height);
  }

  update(time: TimeOfDay) {
    const color = getAmbientColor(time);
    const hex = (color.r << 16) | (color.g << 8) | color.b;

    this.overlay.clear();
    this.overlay.rect(0, 0, this.overlay.width, this.overlay.height);
    this.overlay.fill({ color: hex, alpha: color.a });
  }

  resize(width: number, height: number) {
    this.overlay.width = width;
    this.overlay.height = height;
  }

  get displayObject() {
    return this.overlay;
  }
}
```

## Day/Night Cycle

Time progresses each frame. One game day = a few real minutes:

```typescript
// src/game/day-cycle.ts
export class DayCycle {
  hour = 8;  // Start at 8 AM
  private speed = 1; // Game hours per real second (1 = 24 sec per day)

  constructor(speed = 0.5) {
    this.speed = speed;
  }

  update(dt: number) {
    this.hour += this.speed * dt;
    if (this.hour >= 24) {
      this.hour -= 24;
    }
  }

  get isNight(): boolean {
    return this.hour < 6 || this.hour >= 20;
  }

  get isDawn(): boolean {
    return this.hour >= 5 && this.hour < 7;
  }

  get isDusk(): boolean {
    return this.hour >= 18 && this.hour < 20;
  }

  get timeOfDay(): TimeOfDay {
    return { hour: this.hour };
  }
}
```

## Point Lights (Buildings Glow at Night)

At night, buildings emit warm light. Render point lights as radial gradients on a separate "light map" canvas:

```typescript
// src/engine/point-lights.ts
export interface PointLight {
  worldX: number;
  worldY: number;
  radius: number;
  color: string;    // e.g., 'rgba(255, 200, 100, 0.8)'
  intensity: number; // 0-1
}

export class LightingSystem {
  private lightCanvas: HTMLCanvasElement;
  private lightCtx: CanvasRenderingContext2D;
  private lights: PointLight[] = [];

  constructor(width: number, height: number) {
    this.lightCanvas = document.createElement('canvas');
    this.lightCanvas.width = width;
    this.lightCanvas.height = height;
    this.lightCtx = this.lightCanvas.getContext('2d')!;
  }

  addLight(light: PointLight) {
    this.lights.push(light);
  }

  clearLights() {
    this.lights = [];
  }

  render(camera: Camera, ambientDarkness: number) {
    const ctx = this.lightCtx;
    const w = this.lightCanvas.width;
    const h = this.lightCanvas.height;

    // Start with ambient darkness
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = `rgba(10, 10, 40, ${ambientDarkness})`;
    ctx.fillRect(0, 0, w, h);

    // Punch holes for each light using 'destination-out' or lighter blend
    ctx.globalCompositeOperation = 'destination-out';

    for (const light of this.lights) {
      const screenX = (light.worldX - camera.x) * camera.zoom;
      const screenY = (light.worldY - camera.y) * camera.zoom;
      const radius = light.radius * camera.zoom;

      const gradient = ctx.createRadialGradient(
        screenX, screenY, 0,
        screenX, screenY, radius
      );
      gradient.addColorStop(0, `rgba(255, 255, 255, ${light.intensity})`);
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalCompositeOperation = 'source-over';
  }

  compositeOnto(mainCtx: CanvasRenderingContext2D) {
    mainCtx.save();
    mainCtx.globalCompositeOperation = 'multiply';
    mainCtx.drawImage(this.lightCanvas, 0, 0);
    mainCtx.restore();
  }
}
```

Attach lights to buildings at night:

```typescript
function updateLights(dayCycle: DayCycle, buildings: PlacedBuilding[], lightSystem: LightingSystem) {
  lightSystem.clearLights();

  if (!dayCycle.isNight) return;

  for (const building of buildings) {
    if (building.def.hasLight) {
      const { screenX, screenY } = cartToIso(building.gridX, building.gridY);
      lightSystem.addLight({
        worldX: screenX + worldOffsetX,
        worldY: screenY + worldOffsetY - building.def.spriteHeight * 0.4,
        radius: 80,
        color: 'rgba(255, 200, 100, 0.8)',
        intensity: 0.7 + Math.sin(Date.now() * 0.002) * 0.1, // Flicker
      });
    }
  }
}
```

## Rain Particles

Rain is a screen-space particle effect — it doesn't move with the world:

```typescript
// src/engine/weather.ts
interface RainDrop {
  x: number;
  y: number;
  speed: number;
  length: number;
}

export class RainEffect {
  private drops: RainDrop[] = [];
  private intensity = 200; // Drops on screen
  private width: number;
  private height: number;

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.initDrops();
  }

  private initDrops() {
    for (let i = 0; i < this.intensity; i++) {
      this.drops.push(this.createDrop());
    }
  }

  private createDrop(): RainDrop {
    return {
      x: Math.random() * this.width,
      y: Math.random() * this.height,
      speed: 400 + Math.random() * 200,
      length: 10 + Math.random() * 15,
    };
  }

  update(dt: number) {
    for (const drop of this.drops) {
      drop.y += drop.speed * dt;
      drop.x -= drop.speed * 0.1 * dt; // Slight wind angle

      if (drop.y > this.height) {
        drop.y = -drop.length;
        drop.x = Math.random() * this.width;
      }
    }
  }

  render(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.strokeStyle = 'rgba(180, 200, 255, 0.4)';
    ctx.lineWidth = 1;

    ctx.beginPath();
    for (const drop of this.drops) {
      ctx.moveTo(drop.x, drop.y);
      ctx.lineTo(drop.x - drop.length * 0.1, drop.y + drop.length);
    }
    ctx.stroke();
    ctx.restore();
  }
}
```

## Fog Overlay

Fog is a semi-transparent noise texture that drifts slowly:

```typescript
// src/engine/fog.ts
export class FogEffect {
  private offset = 0;
  private speed = 15; // Pixels per second

  update(dt: number) {
    this.offset += this.speed * dt;
  }

  render(ctx: CanvasRenderingContext2D, width: number, height: number) {
    ctx.save();
    ctx.globalAlpha = 0.15;

    // Draw multiple semi-transparent ellipses drifting across
    const fogColor = 'rgba(200, 210, 220, 0.3)';
    for (let i = 0; i < 8; i++) {
      const x = ((this.offset + i * 150) % (width + 200)) - 100;
      const y = height * 0.3 + Math.sin(i * 1.5 + this.offset * 0.01) * 50;
      const rx = 200 + i * 30;
      const ry = 40 + i * 10;

      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
      ctx.fillStyle = fogColor;
      ctx.fill();
    }

    ctx.restore();
  }
}
```

## Putting It All Together

```typescript
// src/main.ts (render order)
const dayCycle = new DayCycle(0.3);
const lightSystem = new LightingSystem(canvas.width, canvas.height);
const rain = new RainEffect(canvas.width, canvas.height);
const fog = new FogEffect();

let weatherActive = false;

function update(dt: number) {
  dayCycle.update(dt);
  updateLights(dayCycle, buildings, lightSystem);

  if (weatherActive) {
    rain.update(dt);
    fog.update(dt);
  }
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 1. Render world (terrain, buildings, NPCs)
  renderWorld(ctx, camera);

  // 2. Apply lighting overlay
  if (dayCycle.isNight || dayCycle.isDusk) {
    const darkness = dayCycle.isNight ? 0.6 : 0.3;
    lightSystem.render(camera, darkness);
    lightSystem.compositeOnto(ctx);
  } else {
    // Daytime ambient tint
    renderAmbientOverlay(ctx, dayCycle.timeOfDay);
  }

  // 3. Weather effects (screen space, on top)
  if (weatherActive) {
    fog.render(ctx, canvas.width, canvas.height);
    rain.render(ctx);
  }

  // 4. HUD (always on top, unaffected by lighting)
  renderHUD(ctx);
}
```

## Riku's Reaction

The city glows at night. Rain streaks across the screen during storms. Dawn breaks with a warm orange wash. It's atmospheric.

Riku: "Beautiful. Now we need actual UI — resource counters, a build menu, tooltips. The game needs a HUD."

You: "HUD layer. Screen space, separate from the world. HTML overlay or canvas-drawn — let's figure out which."

## What You Built

- **Ambient tint** — multiply blend overlay changes with time of day
- **Day/night cycle** — smooth hour progression with dawn/dusk transitions
- **Point lights** — radial gradients punched into a darkness layer
- **Light flicker** — sine-wave intensity variation for warmth
- **Rain particles** — screen-space streaks with wind angle
- **Fog overlay** — drifting ellipses for atmospheric depth
- **Render order** — world → lighting → weather → HUD

The city has mood. Next: giving the player information with a proper HUD.

---

[← Chapter 14: Camera & Zoom](chapter-14-camera-zoom.md) | [Chapter 16: HUD →](chapter-16-hud.md)
