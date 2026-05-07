# Chapter 13: Faces and Icons

[← Ch 12](chapter-12-pixel-sprites.md) | [Ch 14 →](chapter-14-animation.md)

---

## Juno's Request

> "NPCs need faces for dialogue. Factions need emblems. Items need icons. I want a composable system — pick eyes from a set, mouth from a set, accessories from a set, layer them. Each seed gives a unique face. Same approach for faction emblems."

---

## Composable Parts System

```typescript
import Alea from 'alea';

type DrawFn = (ctx: CanvasRenderingContext2D, x: number, y: number, s: number) => void;

const EYES: DrawFn[] = [
  (ctx,x,y,s) => { // round
    ctx.fillStyle='#fff'; ctx.beginPath();
    ctx.arc(x-4*s,y,3*s,0,Math.PI*2); ctx.arc(x+4*s,y,3*s,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#111'; ctx.beginPath();
    ctx.arc(x-4*s,y,1.5*s,0,Math.PI*2); ctx.arc(x+4*s,y,1.5*s,0,Math.PI*2); ctx.fill();
  },
  (ctx,x,y,s) => { // narrow
    ctx.fillStyle='#fff';
    ctx.fillRect(x-7*s,y-s,5*s,2*s); ctx.fillRect(x+2*s,y-s,5*s,2*s);
  },
  (ctx,x,y,s) => { // alien
    ctx.fillStyle='#0ff'; ctx.beginPath();
    ctx.ellipse(x-5*s,y,4*s,2*s,0,0,Math.PI*2); ctx.ellipse(x+5*s,y,4*s,2*s,0,0,Math.PI*2); ctx.fill();
  },
];

const MOUTHS: DrawFn[] = [
  (ctx,x,y,s) => { ctx.strokeStyle='#333'; ctx.lineWidth=1.5*s; ctx.beginPath(); ctx.arc(x,y-2*s,4*s,0.2*Math.PI,0.8*Math.PI); ctx.stroke(); },
  (ctx,x,y,s) => { ctx.strokeStyle='#333'; ctx.lineWidth=1.5*s; ctx.beginPath(); ctx.moveTo(x-3*s,y); ctx.lineTo(x+3*s,y); ctx.stroke(); },
  (ctx,x,y,s) => { ctx.fillStyle='#333'; ctx.fillRect(x-4*s,y-s,8*s,2*s); },
];
```

---

## Face Generator

```typescript
function generateFace(seed: string | number, size = 64): HTMLCanvasElement {
  const rng = Alea(seed);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const cx = size/2, cy = size/2, s = size/64;

  ctx.fillStyle = '#1a1a2e'; ctx.fillRect(0, 0, size, size);

  // Head shape
  const skinHue = rng()*40+15;
  const [sr,sg,sb] = hslToRgb(skinHue, 30+rng()*40, 40+rng()*30);
  ctx.fillStyle = `rgb(${sr},${sg},${sb})`;
  const shapes = ['round','oval','square'] as const;
  const shape = shapes[Math.floor(rng()*shapes.length)];
  if (shape === 'round') { ctx.beginPath(); ctx.arc(cx,cy,22*s,0,Math.PI*2); ctx.fill(); }
  else if (shape === 'oval') { ctx.beginPath(); ctx.ellipse(cx,cy,18*s,24*s,0,0,Math.PI*2); ctx.fill(); }
  else { ctx.beginPath(); ctx.roundRect(cx-20*s,cy-22*s,40*s,44*s,4*s); ctx.fill(); }

  // Eyes + Mouth
  EYES[Math.floor(rng()*EYES.length)](ctx, cx, cy-5*s, s);
  MOUTHS[Math.floor(rng()*MOUTHS.length)](ctx, cx, cy+10*s, s);

  // Hair (optional)
  if (rng() > 0.3) {
    const [hr,hg,hb] = hslToRgb(rng()*360, 40, 30+rng()*30);
    ctx.fillStyle = `rgb(${hr},${hg},${hb})`;
    ctx.beginPath(); ctx.ellipse(cx,cy-20*s,22*s,10*s,0,Math.PI,0); ctx.fill();
  }

  // Accessory (optional)
  if (rng() > 0.6) {
    const type = Math.floor(rng()*3);
    if (type === 0) { ctx.strokeStyle='#8b0000'; ctx.lineWidth=2*s; ctx.beginPath(); ctx.moveTo(cx-8*s,cy-12*s); ctx.lineTo(cx-4*s,cy+5*s); ctx.stroke(); } // scar
    else if (type === 1) { ctx.fillStyle='#222'; ctx.fillRect(cx+s,cy-8*s,8*s,6*s); } // eyepatch
    else { ctx.strokeStyle='#0af'; ctx.lineWidth=1.5*s; ctx.beginPath(); ctx.moveTo(cx+10*s,cy-22*s); ctx.lineTo(cx+14*s,cy-32*s); ctx.stroke(); } // antenna
  }
  return canvas;
}
```

---

## Faction Emblems

```typescript
function generateEmblem(seed: string | number, size = 64): HTMLCanvasElement {
  const rng = Alea(seed);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const cx = size/2, cy = size/2;

  // Shield background
  const bgHue = rng()*360;
  ctx.fillStyle = `hsl(${bgHue},60%,20%)`;
  ctx.beginPath();
  ctx.moveTo(cx,4); ctx.lineTo(size-4,size*0.3); ctx.lineTo(size-8,size*0.8);
  ctx.lineTo(cx,size-4); ctx.lineTo(8,size*0.8); ctx.lineTo(4,size*0.3);
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle = `hsl(${bgHue},70%,50%)`; ctx.lineWidth = 2; ctx.stroke();

  // Central symbol
  ctx.fillStyle = `hsl(${(bgHue+180)%360},70%,60%)`;
  const sym = Math.floor(rng()*4);
  if (sym === 0) { // star
    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = (i/10)*Math.PI*2-Math.PI/2;
      const r = i%2===0 ? size*0.3 : size*0.15;
      const px = cx+Math.cos(a)*r, py = cy+Math.sin(a)*r;
      i===0 ? ctx.moveTo(px,py) : ctx.lineTo(px,py);
    }
    ctx.closePath(); ctx.fill();
  } else if (sym === 1) { // triangle
    const ts = size*0.25;
    ctx.beginPath(); ctx.moveTo(cx,cy-ts); ctx.lineTo(cx+ts,cy+ts*0.7); ctx.lineTo(cx-ts,cy+ts*0.7); ctx.closePath(); ctx.fill();
  } else if (sym === 2) { // diamond
    const ds = size*0.2;
    ctx.beginPath(); ctx.moveTo(cx,cy-ds); ctx.lineTo(cx+ds,cy); ctx.lineTo(cx,cy+ds); ctx.lineTo(cx-ds,cy); ctx.closePath(); ctx.fill();
  } else { // rings
    ctx.strokeStyle = ctx.fillStyle; ctx.lineWidth = 2;
    for (let i = 3; i > 0; i--) { ctx.beginPath(); ctx.arc(cx,cy,size*0.08*i,0,Math.PI*2); ctx.stroke(); }
  }
  return canvas;
}
```

---

## Layering System

Draw parts back-to-front — each layer is independent:

```
Layer order: background → head → eyes → nose → mouth → hair → accessories
```

Combinatorial variety: 3 eyes × 3 mouths × 3 heads × 3 accessories = 81 unique faces from 12 parts.

---

## Visual Result

```
Generated faces:
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│◉  ◉│ │●  ●│ │◎  ◎│ │■  ■│ │◉  ◉│
│  ▲ │ │  ● │ │  ◇ │ │  ▽ │ │  △ │
│ ◡  │ │ ── │ │ ── │ │ ── │ │ ◡  │
│scar│ │helm│ │ant.│ │    │ │patch│
└────┘ └────┘ └────┘ └────┘ └────┘
```

---

## Parameter Tuning

| Parameter | Options | Effect |
|-----------|---------|--------|
| Head shape | round, oval, square | Species feel |
| Eye style | round, narrow, alien | Personality |
| Mouth style | smile, flat, fangs | Friendliness |
| Accessories | scar, patch, antenna | Character history |

**Juno's notes:**

> "The accessory layer makes faces memorable. Without it, they blur together. Keep base parts simple (5-8 variants each) and let combinations do the work."

---

## Exercises

1. **Mood system:** Add `emotion` parameter. Happy = smile + wide eyes. Angry = narrow eyes + frown. Same seed + different emotion = same face, different expression.

2. **Faction portraits:** 5 faces sharing same accessory (badge) and color scheme but varying features.

3. **Item icons:** Base shape (circle/square/diamond) + symbol (sword/potion/gem) + rarity color. Generate a 5×5 grid.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Composable parts | Independent drawable components layered |
| Layer order | Back-to-front: background → face → features → accessories |
| Combinatorial | N eyes × M mouths × K heads = N×M×K faces |
| Emblems | Shield shape + geometric symbol + complementary colors |
| Scale parameter | All drawing relative to `s` for resolution independence |

---

[← Ch 12](chapter-12-pixel-sprites.md) | [Ch 14 →](chapter-14-animation.md)
