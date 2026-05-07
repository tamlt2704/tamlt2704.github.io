# Chapter 20: Game Feel — The Juice That Makes It Sing

[← Chapter 19: Runtime Effects](chapter-19-runtime-effects.md)

---

## The Problem

Everything works. Ember is drawn, animated, rendered, state-machined. You play the game. It's... fine. Technically correct. But hits don't feel impactful. Jumps don't feel satisfying. Landing doesn't feel weighty.

Riku plays a commercial indie game next to yours. Same style. Same mechanics. Theirs feels incredible.

> "The difference is **juice**. Screen shake on hit. Freeze frames on impact. Camera that smoothly follows. Particles on every action. None affect gameplay — they're pure feel. But they're the difference between 'this works' and 'this feels amazing.'"

---

## The Principle: Feedback Layers

A single hit in a polished game triggers ALL of these simultaneously:

| Layer | Effect | Duration |
|---|---|---|
| Animation | Knockback pose plays | 160ms |
| VFX | White flash + particles | 80ms + 400ms |
| Screen shake | Camera jolts 3-4px | 100-150ms |
| Hit stop | Game freezes | 50ms |
| Sound | Impact SFX | instant |

Each layer alone is subtle. Together, they create IMPACT.

---

## Effect 1: Screen Shake

```typescript
class ScreenShake {
  private intensity = 0;
  private duration = 0;
  private elapsed = 0;
  offsetX = 0;
  offsetY = 0;

  trigger(intensity: number, duration: number): void {
    this.intensity = intensity;
    this.duration = duration;
    this.elapsed = 0;
  }

  update(deltaTime: number): void {
    if (this.elapsed >= this.duration) {
      this.offsetX = 0;
      this.offsetY = 0;
      return;
    }
    this.elapsed += deltaTime;
    const remaining = 1 - this.elapsed / this.duration;
    const current = this.intensity * remaining;
    this.offsetX = Math.round((Math.random() * 2 - 1) * current);
    this.offsetY = Math.round((Math.random() * 2 - 1) * current);
  }

  apply(ctx: CanvasRenderingContext2D): void {
    ctx.translate(this.offsetX, this.offsetY);
  }
}
```

Shake intensity by event: player hit (3px, 100ms), enemy death (5px, 150ms), boss slam (8px, 250ms).

---

## Effect 2: Hit Stop (Freeze Frames)

Freeze the game for 2-4 frames on impact. The single most satisfying effect in action games:

```typescript
class HitStop {
  private freezeTimer = 0;

  trigger(duration: number): void { this.freezeTimer = duration; }
  isFrozen(): boolean { return this.freezeTimer > 0; }

  update(deltaTime: number): void {
    if (this.freezeTimer > 0) this.freezeTimer -= deltaTime;
  }
}

// In game loop: skip game logic updates while frozen
function gameLoop(timestamp: number): void {
  const deltaTime = timestamp - lastTime;
  lastTime = timestamp;
  hitStop.update(deltaTime);

  if (!hitStop.isFrozen()) {
    player.update(deltaTime, input);
    enemies.forEach(e => e.update(deltaTime));
  }
  render(); // Always render (frozen frame stays visible)
  requestAnimationFrame(gameLoop);
}
```

The freeze gives the brain time to process "I hit something!" — 50ms for normal hits, 80-150ms for kills.

---

## Effect 3: Camera Follow with Lerp

```typescript
class Camera {
  x = 0; y = 0;
  private targetX = 0;
  private targetY = 0;
  private smoothing = 6;

  setTarget(x: number, y: number): void { this.targetX = x; this.targetY = y; }

  update(deltaTime: number): void {
    const dt = deltaTime / 1000;
    this.x += (this.targetX - this.x) * this.smoothing * dt;
    this.y += (this.targetY - this.y) * this.smoothing * dt;
  }

  apply(ctx: CanvasRenderingContext2D): void {
    ctx.translate(-Math.round(this.x), -Math.round(this.y));
  }
}
```

Smoothing 3-4 = floaty/cinematic. **5-8 = platformer sweet spot.** 10+ = nearly instant.

---

## Effect 4: Particle Bursts

```typescript
class ParticleSystem {
  private particles: {x:number; y:number; vx:number; vy:number; life:number; maxLife:number; size:number; color:string}[] = [];

  burst(x: number, y: number, count: number, speed: number, life: number, colors: string[]): void {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const spd = speed * (0.5 + Math.random() * 0.5);
      this.particles.push({ x, y, vx: Math.cos(angle)*spd, vy: Math.sin(angle)*spd,
        life, maxLife: life, size: 2+Math.random()*2, color: colors[Math.floor(Math.random()*colors.length)] });
    }
  }

  update(deltaTime: number): void {
    const dt = deltaTime / 1000;
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 200 * dt;
      p.life -= deltaTime;
      if (p.life <= 0) this.particles.splice(i, 1);
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    for (const p of this.particles) {
      ctx.globalAlpha = p.life / p.maxLife;
      ctx.fillStyle = p.color;
      ctx.fillRect(Math.round(p.x), Math.round(p.y), Math.round(p.size), Math.round(p.size));
    }
    ctx.globalAlpha = 1;
  }
}
```

---

## The Mistake You'll Make

You add juice to everything. Shake on every step. Particles everywhere. Hit stop on every action. The game feels like it's having a seizure.

Riku turns off half your effects:

> "If everything shakes, nothing feels impactful. Reserve the strongest effects for the most important moments. A regular hit gets small shake. A killing blow gets big shake + hit stop + particles. The **contrast** is what creates impact."

### The Fix: Intensity Scaling

| Event | Shake | Hit Stop | Particles |
|---|---|---|---|
| Light hit | 2px, 60ms | None | 3 |
| Heavy hit | 4px, 120ms | 50ms | 8 |
| Kill | 6px, 200ms | 80ms | 15 |
| Boss kill | 10px, 300ms | 150ms | 30 |

Normal actions get subtle feedback. Climactic moments get maximum feedback.

---

## The Complete Render Pipeline

```typescript
function gameLoop(timestamp: number): void {
  const deltaTime = timestamp - lastTime;
  lastTime = timestamp;

  hitStop.update(deltaTime);
  if (!hitStop.isFrozen()) {
    player.update(deltaTime, input);
    enemies.forEach(e => e.update(deltaTime));
    particles.update(deltaTime);
    camera.setTarget(player.x - canvas.width / 2, player.y - canvas.height / 2);
    camera.update(deltaTime);
  }
  shake.update(deltaTime);

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  shake.apply(ctx);
  camera.apply(ctx);
  drawBackground(ctx);
  enemies.forEach(e => e.draw(ctx));
  player.draw(ctx);
  particles.draw(ctx);
  ctx.restore();
  drawUI(ctx); // UI not affected by shake/camera
  requestAnimationFrame(gameLoop);
}
```

---

## Quick Reference

| Effect | When | Intensity |
|---|---|---|
| Screen shake | Hits, explosions, landings | 2-10px, 60-300ms |
| Hit stop | Attack connects, big impacts | 30-150ms |
| Camera lerp | Always (smooth follow) | Smoothing: 5-8 |
| Particles | Deaths, landings, impacts | 3-30 particles |

| Concept | Rule |
|---|---|
| Layered feedback | Multiple subtle effects > one big effect |
| Intensity scaling | Strongest juice for important moments only |
| Hit stop | Freeze logic, keep rendering |
| UI | Never affected by shake or camera |
| Dynamic range | Light=subtle, kill=dramatic |

---

## Exercise: Add Game Feel to Ember Quest

1. Implement `ScreenShake` — trigger on player hit (3px) and enemy death (5px)
2. Implement `HitStop` — 50ms freeze when attack connects
3. Implement `Camera` with lerp follow (smoothing: 6)
4. Implement `ParticleSystem` — fire colors on enemy death, dust on landing
5. Wire into game loop in correct order (hit stop → update → shake → render)

**Final test**: Show 10 seconds of gameplay to someone. Ask "does this feel good?" If yes, you're done.

---

## The Journey Complete

You started with a melted gummy bear. Now you have a 32×32 fire spirit with 54 frames of animation, a state machine, runtime effects, and game feel. 151 total frames of art. All from a 6-color palette.

Riku looks at your game: *"Not bad. The blob is gone. Ember lives."*

---

[← Chapter 19: Runtime Effects](chapter-19-runtime-effects.md)
