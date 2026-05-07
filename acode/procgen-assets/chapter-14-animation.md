# Chapter 14: Animation

[← Ch 13](chapter-13-faces-icons.md) | [Ch 15 →](chapter-15-items-loot.md)

---

## Juno's Request

> "Everything needs to feel alive. Stars twinkle. Creatures bob. Items pulse. But no sprite sheets — math-driven animation. Sin for floating, springs for bouncy reactions, lerp for smooth transitions."

---

## The Core Functions

### Sin: Oscillation

```typescript
function bob(time: number, amplitude = 5, frequency = 2): number {
  return Math.sin(time * frequency) * amplitude;
}
// creature.y = baseY + bob(time);
```

### Lerp: Smooth Transitions

```typescript
function lerp(a: number, b: number, t: number): number { return a + (b-a) * t; }
function smoothstep(t: number): number { return t*t*(3-2*t); }
// object.x = lerp(startX, targetX, smoothstep(elapsed/duration));
```

### Spring: Bouncy Physics

```typescript
interface Spring { position: number; velocity: number; target: number; stiffness: number; damping: number; }

function updateSpring(s: Spring): void {
  s.velocity += (s.target - s.position) * s.stiffness;
  s.velocity *= s.damping;
  s.position += s.velocity;
}
// On pickup: spring.velocity = 5; → bouncy scale effect
```

```
sin(t):   ╭─╮   ╭─╮   ╭─╮        Spring:  ╭╮
         ╱   ╲ ╱   ╲ ╱   ╲               ╱  ╲  ╭╮
        ╱     ╲╱     ╲╱     ╲             ╱    ╲╱  ╲───
```

---

## Creature Animation

```typescript
function animateCreature(ctx: CanvasRenderingContext2D, creature: Creature, baseX: number, baseY: number, time: number): void {
  const bodyBob = Math.sin(time * 1.5) * 3;

  // Segments wave with phase offset
  for (let i = 0; i < creature.segments.length; i++) {
    const seg = creature.segments[i];
    const segBob = Math.sin(time * 1.5 + i * 0.5) * 2;
    const squash = 1 + Math.sin(time * 3 + i * 0.5) * 0.05;

    ctx.save();
    ctx.translate(baseX + seg.x, baseY + bodyBob + segBob);
    ctx.scale(1/squash, squash);
    ctx.fillStyle = `rgb(${creature.color.join(',')})`;
    ctx.beginPath(); ctx.ellipse(0, 0, seg.width/2, seg.height/2, 0, 0, Math.PI*2); ctx.fill();
    ctx.restore();
  }

  // Limbs swing
  for (let i = 0; i < creature.limbs.length; i++) {
    const limb = creature.limbs[i];
    const swing = Math.sin(time * 3 + i * 1.5) * 15;
    const angle = (limb.angle + swing) * Math.PI / 180;
    const sx = baseX + limb.attachX, sy = baseY + limb.attachY + bodyBob;
    ctx.strokeStyle = `rgb(${creature.color.join(',')})`;
    ctx.beginPath(); ctx.moveTo(sx, sy);
    ctx.lineTo(sx + Math.cos(angle)*limb.length, sy + Math.sin(angle)*limb.length);
    ctx.stroke();
  }
}
```

---

## UI Animations

```typescript
// Pulse (attention)
function pulse(time: number, speed = 3, min = 0.9, max = 1.1): number {
  return min + ((Math.sin(time*speed)+1)/2) * (max-min);
}

// Wiggle (error shake that decays)
function wiggle(time: number, intensity = 3, speed = 10): number {
  return Math.sin(time * speed) * intensity * Math.exp(-time * 2);
}

// Sway (organic, layered frequencies)
function sway(time: number, x: number, amp = 5): number {
  return Math.sin(time*1.5 + x*0.1)*amp + Math.sin(time*0.7 + x*0.05)*amp*0.5;
}
```

---

## Animation Loop

```typescript
let lastTime = 0;
function gameLoop(timestamp: number): void {
  const dt = (timestamp - lastTime) / 1000;
  lastTime = timestamp;
  const time = timestamp / 1000;

  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Stars twinkle
  for (const star of stars) {
    const b = star.baseBrightness * (0.7 + 0.3*Math.sin(time*2+star.phase));
    drawStar(ctx, star.x, star.y, b);
  }

  // Creatures bob
  animateCreature(ctx, creature, 100, 200, time);

  // Items pulse
  ctx.save(); const s = pulse(time);
  ctx.translate(itemX, itemY); ctx.scale(s, s);
  drawItem(ctx); ctx.restore();

  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

---

## Combining Animations

Layer multiple effects for rich motion:

```typescript
function animateShip(time: number, ship: Ship): void {
  ship.renderY = ship.y + Math.sin(time*1.2)*2;           // hover bob
  ship.renderX = ship.x + Math.sin(time*20)*0.5;          // engine vibration
  ship.tilt = lerp(ship.tilt, ship.velocityX*0.1, 0.1);   // lean into movement
  ship.exhaustLength = 5 + Math.sin(time*15)*2;            // exhaust flicker
}
```

---

## Parameter Tuning

| Animation | Frequency | Amplitude | Notes |
|-----------|-----------|-----------|-------|
| Creature bob | 1-2 Hz | 2-5 px | Slow, gentle |
| Star twinkle | 2-4 Hz | 0.3 opacity | Subtle |
| Item pulse | 2-3 Hz | ±10% scale | Eye-catching |
| UI wiggle | 8-12 Hz | 2-5° | Decays quickly |
| Engine vibration | 15-25 Hz | 0.5 px | Nearly invisible |

**Juno's notes:**

> "One sin wave looks mechanical. Two at different frequencies look organic. Three looks alive. Keep amplitudes small — 2-5 pixels. Subtle = atmospheric."

---

## Exercises

1. **Breathing UI:** Health bar scales Y between 0.95-1.05 at 0.5 Hz. Low health → 2 Hz (panicked).

2. **Spring chain:** 5 circles, each springs toward the previous. Move first with mouse.

3. **Procedural walk:** Stick figure: body bobs sin(t), legs alternate sin(t) vs sin(t+π), arms opposite legs.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| `sin(t * freq)` | Smooth oscillation |
| `lerp(a, b, t)` | Blend between values |
| Spring | `force = (target-pos)*stiffness; vel *= damping` |
| Phase offset | `sin(t + phase)` — same motion, different timing |
| Layered sin | Multiple frequencies = organic |
| No sprite sheets | Math replaces pre-drawn frames |

---

[← Ch 13](chapter-13-faces-icons.md) | [Ch 15 →](chapter-15-items-loot.md)
