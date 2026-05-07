# Chapter 8: L-Systems

[← Ch 7](chapter-07-wfc.md) | [Ch 9 →](chapter-09-rocks-crystals.md)

---

## Juno's Request

> "Some planets have vegetation — alien trees, coral structures, fungal growths. I need branching structures that look organic. Each seed gives a different species. Some tall and sparse, some bushy and dense."

---

## L-Systems: The Concept

A string rewriting system interpreted as drawing instructions:

```
Axiom:    F
Rule:     F → F[+F]F[-F]F
Symbols:  F=forward, +=turn right, -=turn left, [=save state, ]=restore state

Iteration 0:  F
Iteration 1:  F[+F]F[-F]F
Iteration 2:  F[+F]F[-F]F[+F[+F]F[-F]F]F[+F]F[-F]F[-F[+F]F[-F]F]F[+F]F[-F]F
```

---

## Grammar Engine

```typescript
import Alea from 'alea';

interface LSystem {
  axiom: string;
  rules: { symbol: string; replacement: string; probability?: number }[];
  angle: number;
  iterations: number;
  lengthFactor: number;
}

function expandLSystem(system: LSystem, rng?: () => number): string {
  let current = system.axiom;
  for (let i = 0; i < system.iterations; i++) {
    let next = '';
    for (const char of current) {
      const matches = system.rules.filter(r => r.symbol === char);
      if (matches.length === 0) { next += char; continue; }
      if (matches.length === 1 && !rng) { next += matches[0].replacement; continue; }
      // Stochastic selection
      const roll = rng ? rng() : 0;
      let cum = 0;
      for (const rule of matches) {
        cum += rule.probability || (1 / matches.length);
        if (roll <= cum) { next += rule.replacement; break; }
      }
    }
    current = next;
  }
  return current;
}
```

---

## Turtle Graphics Renderer

```typescript
function renderLSystem(instructions: string, system: LSystem, size: number = 256): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, size, size);

  const stack: {x:number;y:number;angle:number;len:number;depth:number}[] = [];
  let state = { x: size/2, y: size-20, angle: -90, len: 5, depth: 0 };
  const angleRad = system.angle * (Math.PI / 180);

  ctx.strokeStyle = '#4a8c3f';
  for (const char of instructions) {
    switch (char) {
      case 'F': case 'G':
        const nx = state.x + Math.cos(state.angle * Math.PI/180) * state.len;
        const ny = state.y + Math.sin(state.angle * Math.PI/180) * state.len;
        ctx.lineWidth = Math.max(0.5, 3 - state.depth * 0.5);
        ctx.beginPath(); ctx.moveTo(state.x, state.y); ctx.lineTo(nx, ny); ctx.stroke();
        state.x = nx; state.y = ny; break;
      case '+': state.angle += system.angle; break;
      case '-': state.angle -= system.angle; break;
      case '[': stack.push({...state}); state.len *= system.lengthFactor; state.depth++; break;
      case ']': state = stack.pop()!; break;
    }
  }
  return canvas;
}
```

---

## Tree Presets

```typescript
const TREE_PRESETS: Record<string, LSystem> = {
  oak: { axiom: 'F', rules: [{symbol:'F', replacement:'FF+[+F-F-F]-[-F+F+F]'}],
         angle: 22.5, iterations: 4, lengthFactor: 0.7 },
  pine: { axiom: 'F', rules: [{symbol:'F', replacement:'F[+F]F[-F]F'}],
          angle: 25.7, iterations: 4, lengthFactor: 0.6 },
  coral: { axiom: 'F', rules: [{symbol:'F', replacement:'F[+F][-F]F[+F]'}],
           angle: 30, iterations: 4, lengthFactor: 0.75 },
  alien: { axiom: 'X', rules: [{symbol:'X', replacement:'F[+X][-X]FX'}, {symbol:'F', replacement:'FF'}],
           angle: 35, iterations: 5, lengthFactor: 0.65 },
};
```

---

## Adding Leaves

Draw colored circles at branch tips (deep branches):

```typescript
// After rendering branches, re-traverse and draw leaves at max depth
if (state.depth >= system.iterations - 1) {
  ctx.fillStyle = 'rgba(80, 180, 60, 0.7)';
  ctx.beginPath();
  ctx.arc(state.x, state.y, 3, 0, Math.PI * 2);
  ctx.fill();
}
```

---

## Stochastic Variety from Seeds

```typescript
function generateTree(seed: string | number, preset: string = 'oak'): HTMLCanvasElement {
  const rng = Alea(seed);
  const base = TREE_PRESETS[preset];
  const system: LSystem = {
    ...base,
    angle: base.angle + (rng() - 0.5) * 10,
    lengthFactor: base.lengthFactor + (rng() - 0.5) * 0.1,
    rules: base.rules.flatMap(rule => [
      { ...rule, probability: 0.7 },
      { symbol: rule.symbol, replacement: rule.replacement.replace(/FF/g, 'F'), probability: 0.3 },
    ]),
  };
  return renderLSystem(expandLSystem(system, rng), system);
}
```

---

## Visual Result

```
Oak (22.5°):      Pine (25.7°):     Coral (30°):
    ╱╲  ╱╲             │              ╱╲╱╲
   ╱  ╲╱  ╲           ╱│╲            ╱╲  ╱╲
  ╱╲      ╱╲         ╱ │ ╲          ╱  ╲╱  ╲
     │                 ╱│╲              │
     │                  │               │
  (broad)          (layered)       (fan-shaped)
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| `angle` | 15° | 45° | Narrow/tall vs wide/bushy |
| `iterations` | 3 | 6 | Simple vs complex (exponential!) |
| `lengthFactor` | 0.5 | 0.85 | Short vs long branches |

**Juno's notes:**

> "4 iterations is the sweet spot for real-time. The angle is the personality — 22° feels Earth-like, 35° feels alien. Warning: string length grows exponentially. Cap at 5-6 iterations."

---

## Exercises

1. **Alien species generator:** Random L-System from seed: pick axiom, 1-2 rules with random brackets, angle 15-45°, iterations 3-5. Each seed = unique species.

2. **Seasonal trees:** Same structure, different leaf rendering. Spring: small green dots. Autumn: orange/red random. Winter: no leaves.

3. **Animated growth:** Render at iteration 1, then 2, then 3 with delays. Tree appears to grow.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Axiom | Starting string (usually `F` or `X`) |
| Rules | Rewrite symbols each iteration |
| Turtle | F=forward, +=right, -=left, [=push, ]=pop |
| Stochastic | Multiple rules per symbol with probabilities |
| Exponential growth | String doubles+ per iteration — cap at 5-6 |

---

[← Ch 7](chapter-07-wfc.md) | [Ch 9 →](chapter-09-rocks-crystals.md)
