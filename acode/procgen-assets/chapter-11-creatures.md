# Chapter 11: Creatures

[← Ch 10](chapter-10-buildings.md) | [Ch 12 →](chapter-12-pixel-sprites.md)

---

## Juno's Request

> "Every planet needs fauna. Alien creatures that look like they belong. Bilateral symmetry, consistent proportions, recognizable body plans. A seed determines body shape, segments, limb count, head size. Think Spore's creature creator, but algorithmic."

---

## Body Plan Architecture

```
HEAD ── TORSO ── TORSO ── TORSO ── TAIL
 │        │        │        │
eyes    arms     legs     legs

Parameters: segments (2-5), limb pairs (0-4), head scale, taper style
```

---

## Segment-Based Generation

```typescript
import Alea from 'alea';

interface Segment { x: number; y: number; width: number; height: number; type: 'head'|'body'|'tail'; }
interface Limb { attachX: number; attachY: number; length: number; angle: number; }
interface Creature { segments: Segment[]; limbs: Limb[]; color: [number,number,number]; eyeCount: number; }

function generateCreature(seed: string | number): Creature {
  const rng = Alea(seed);
  const segCount = 2 + Math.floor(rng() * 4);
  const limbPairs = Math.floor(rng() * 4);
  const headScale = 0.6 + rng();
  const bodyW = 12 + rng() * 16, bodyH = 10 + rng() * 12;

  const segments: Segment[] = [];
  let cx = 0;

  // Head
  segments.push({ x: cx, y: 0, width: bodyW*headScale, height: bodyH*headScale, type: 'head' });
  cx += bodyW * headScale * 0.8;

  // Body with taper
  const taperType = rng();
  for (let i = 0; i < segCount; i++) {
    const t = i / segCount;
    const scale = taperType < 0.33 ? 1.0 : taperType < 0.66 ? 1.0-t*0.4 : 1.0+Math.sin(t*Math.PI)*0.3;
    segments.push({ x: cx, y: 0, width: bodyW*scale, height: bodyH*scale, type: 'body' });
    cx += bodyW * scale * 0.7;
  }

  // Tail
  if (rng() > 0.4) {
    for (let i = 0; i < 1+Math.floor(rng()*2); i++) {
      const s = Math.max(0.1, 0.5-i*0.15);
      segments.push({ x: cx, y: 0, width: bodyW*s, height: bodyH*s, type: 'tail' });
      cx += bodyW*s*0.5;
    }
  }

  // Limbs (bilateral symmetry)
  const limbs: Limb[] = [];
  const bodySegs = segments.filter(s => s.type === 'body');
  for (let i = 0; i < limbPairs; i++) {
    const seg = bodySegs[Math.floor(rng() * bodySegs.length)];
    const len = 10 + rng() * 20, angle = 60 + rng() * 60;
    limbs.push({ attachX: seg.x+seg.width/2, attachY: seg.height/2, length: len, angle });
    limbs.push({ attachX: seg.x+seg.width/2, attachY: -seg.height/2, length: len, angle: -angle });
  }

  const hue = rng() * 360;
  return { segments, limbs, color: hslToRgb(hue, 30+rng()*50, 30+rng()*30), eyeCount: 1+Math.floor(rng()*4) };
}
```

---

## Rendering

```typescript
function renderCreature(creature: Creature, size = 128): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, size, size);

  const totalW = creature.segments.reduce((s, seg) => s + seg.width*0.7, 0);
  const ox = (size-totalW)/2, oy = size/2;
  const [r,g,b] = creature.color;

  // Limbs (behind body)
  ctx.strokeStyle = `rgb(${r-20},${g-20},${b-20})`; ctx.lineWidth = 3;
  for (const limb of creature.limbs) {
    const sx = ox+limb.attachX, sy = oy+limb.attachY;
    const ex = sx + Math.cos(limb.angle*Math.PI/180)*limb.length;
    const ey = sy + Math.sin(limb.angle*Math.PI/180)*limb.length;
    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
  }

  // Body segments
  ctx.fillStyle = `rgb(${r},${g},${b})`;
  for (const seg of creature.segments) {
    ctx.beginPath();
    ctx.ellipse(ox+seg.x, oy+seg.y, seg.width/2, seg.height/2, 0, 0, Math.PI*2);
    ctx.fill();
  }

  // Eyes on head
  const head = creature.segments[0];
  ctx.fillStyle = '#fff';
  for (let i = 0; i < creature.eyeCount; i++) {
    const spread = ((i-(creature.eyeCount-1)/2) / creature.eyeCount) * head.width*0.3;
    ctx.beginPath(); ctx.arc(ox+head.x+spread, oy-head.height*0.1, 3, 0, Math.PI*2); ctx.fill();
  }
  return canvas;
}
```

---

## Bilateral Symmetry

The key to creatures looking alive — limbs always come in mirrored pairs:

```
Without symmetry:        With symmetry:
  ○                        ○
 /│\                      /│\
/ │ ╲                    ╱ │ ╲
  │   ╲                 ╱  │  ╲
 (broken)              (organic)
```

---

## Planet Adaptation

```typescript
function adaptCreatureToplanet(creature: Creature, planetType: string, rng: () => number): void {
  if (planetType === 'ice') creature.segments.forEach(s => { s.height *= 0.7; s.width *= 1.3; }); // stocky
  if (planetType === 'toxic') creature.color = hslToRgb(60+rng()*60, 80, 50); // warning colors
  if (planetType === 'crystal') creature.segments.forEach(s => { s.width *= 0.8; }); // angular
}
```

---

## Visual Result

```
Seed "c-1":        Seed "c-2":        Seed "c-3":
┌────────────┐     ┌────────────┐     ┌────────────┐
│  ◉◉        │     │    ◉       │     │ ◉◉◉◉      │
│ ╭──╮╭─╮   │     │  ╭───╮╭╮  │     │╭──╮╭─╮╭╮  │
│╱│  ││ │╲  │     │ ╱│   │││╲ │     ││  ││ ││ │  │
│ ╰──╯╰─╯   │     │╱ ╰───╯╰╯╲│     │╰──╯╰─╯╰╯  │
│(4-legged)  │     │(6-legged) │     │(serpentine) │
└────────────┘     └────────────┘     └────────────┘
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| Segments | 2 | 5 | Compact vs elongated |
| Limb pairs | 0 | 4 | Snake vs centipede |
| Head scale | 0.5 | 2.0 | Tiny vs big-brained |
| Eye count | 1 | 6 | Cyclops vs spider-like |

**Juno's notes:**

> "Eye count sells 'alien' more than anything. Always bilateral symmetry on limbs — asymmetric looks broken, not alien."

---

## Exercises

1. **Walk cycle:** Oscillate limb angles with `sin(time + phase)`. Alternate left/right phases.

2. **Size classes:** Small (32px, 2 segments), medium (64px, 3 segments), large (128px, 5 segments).

3. **Creature families:** Parent seed → offspring with same body plan but ±20% proportions.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Body plan | Head → body segments → tail, limbs attached |
| Bilateral symmetry | Mirror limbs across spine |
| Taper | Scale segments by position |
| Planet adaptation | Type modifies proportions and colors |
| Eyes | Count + placement on head sells personality |

---

[← Ch 10](chapter-10-buildings.md) | [Ch 12 →](chapter-12-pixel-sprites.md)
