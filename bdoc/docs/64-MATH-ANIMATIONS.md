# Chapter 64: Beautiful Math Animations — Simple Formulas, Stunning Visuals

## What you'll learn

- 20+ eye-catching animations from SIMPLE math (no PhD required)
- How sine, cosine, and circles create mesmerising patterns
- Particle systems that look expensive but cost 10 lines of code
- Fractals, spirals, waves, and pendulums
- Colour theory for animations (gradients, HSL, rainbow effects)
- Tools: Canvas 2D (quick), Motion Canvas (for video export)
- Each recipe: the math, the code, and WHY it looks beautiful

---

## The Secret: Beautiful animations come from SIMPLE formulas + repetition + colour

```
You don't need complex math. You need:
  1. A simple formula (sin, cos, modulo, distance)
  2. Many particles/points following that formula
  3. Slight variation between each (offset, delay, colour)
  4. Smooth movement over time

That's it. Every "wow" animation on Twitter/TikTok is this pattern.
```

---

## RECIPE 1: Orbiting Circles (Hypnotic)

```javascript
// Circles orbiting in a ring — each slightly offset in phase
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
const W = canvas.width = 800, H = canvas.height = 800;

function draw(t) {
  ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; // trail effect (don't fully clear)
  ctx.fillRect(0, 0, W, H);

  const N = 30; // number of circles
  for (let i = 0; i < N; i++) {
    const angle = (i / N) * Math.PI * 2 + t * 0.02;
    const radius = 200 + Math.sin(t * 0.03 + i * 0.5) * 80;
    const x = W / 2 + Math.cos(angle) * radius;
    const y = H / 2 + Math.sin(angle) * radius;
    const size = 8 + Math.sin(t * 0.05 + i) * 4;

    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${(i / N) * 360 + t * 2}, 80%, 60%)`;
    ctx.fill();
  }

  requestAnimationFrame(() => draw(t + 1));
}
draw(0);
```

**Why it's beautiful:**
- `sin` + `cos` = circular motion (our eyes love circles)
- Each circle has different phase (`i * 0.5`) → forms a flowing pattern
- HSL colour cycling → rainbow without effort
- Trail effect (`rgba(0,0,0,0.05)`) → ghostly afterimage

---

## RECIPE 2: Lissajous Curves (Elegant Geometry)

```javascript
// Two sine waves at different frequencies create beautiful curves
function draw(t) {
  ctx.fillStyle = "rgba(0, 0, 0, 0.02)";
  ctx.fillRect(0, 0, W, H);

  const a = 3, b = 4; // frequency ratio (try: 3:4, 5:6, 7:8)
  const points = 500;

  ctx.beginPath();
  for (let i = 0; i < points; i++) {
    const p = (i / points) * Math.PI * 2;
    const x = W / 2 + Math.sin(a * p + t * 0.01) * 300;
    const y = H / 2 + Math.sin(b * p + t * 0.013) * 300;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.strokeStyle = `hsl(${t % 360}, 70%, 60%)`;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  requestAnimationFrame(() => draw(t + 1));
}
```

**The math:** `x = sin(a·t)`, `y = sin(b·t)`. Different ratios of a:b create different shapes. Slowly changing `t` makes it evolve.

---

## RECIPE 3: Particle Fountain / Fireworks

```javascript
class Particle {
  constructor(x, y) {
    this.x = x; this.y = y;
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed - 3; // upward bias
    this.life = 1.0;
    this.hue = Math.random() * 60 + 20; // warm colours
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += 0.08; // gravity
    this.life -= 0.015;
  }
  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, 3 * this.life, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${this.hue}, 90%, 60%, ${this.life})`;
    ctx.fill();
  }
}

let particles = [];
function draw() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
  ctx.fillRect(0, 0, W, H);

  // Spawn new particles at center
  for (let i = 0; i < 3; i++) {
    particles.push(new Particle(W / 2, H / 2));
  }

  // Update and draw
  particles = particles.filter(p => p.life > 0);
  for (const p of particles) {
    p.update();
    p.draw(ctx);
  }

  requestAnimationFrame(draw);
}
draw();
```

**Why it's eye-catching:** Gravity + random angles + fading opacity = natural-looking fountain. Our brains are wired to watch things fall.

---

## RECIPE 4: Wave Interference (Water Ripples)

```javascript
function draw(t) {
  const imageData = ctx.createImageData(W, H);
  const data = imageData.data;

  // Two wave sources
  const sources = [
    { x: W * 0.35, y: H * 0.5 },
    { x: W * 0.65, y: H * 0.5 },
  ];

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let wave = 0;
      for (const src of sources) {
        const dist = Math.sqrt((x - src.x) ** 2 + (y - src.y) ** 2);
        wave += Math.sin(dist * 0.05 - t * 0.05);
      }

      // Map wave value (-2 to 2) to colour
      const brightness = (wave + 2) / 4; // 0 to 1
      const idx = (y * W + x) * 4;
      data[idx] = brightness * 50;         // R
      data[idx + 1] = brightness * 120;    // G
      data[idx + 2] = brightness * 255;    // B
      data[idx + 3] = 255;                 // A
    }
  }

  ctx.putImageData(imageData, 0, 0);
  requestAnimationFrame(() => draw(t + 1));
}
```

**The math:** Two `sin(distance)` waves from different sources. Where they overlap constructively → bright. Destructively → dark. Real physics, stunning visual.

---

## RECIPE 5: Golden Spiral / Phyllotaxis (Sunflower Pattern)

```javascript
function draw(t) {
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, W, H);

  const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // ~137.5°
  const maxDots = Math.min(t * 2, 1000); // grow over time

  for (let i = 0; i < maxDots; i++) {
    const angle = i * goldenAngle;
    const radius = Math.sqrt(i) * 8;
    const x = W / 2 + Math.cos(angle) * radius;
    const y = H / 2 + Math.sin(angle) * radius;
    const size = 3 + (i / maxDots) * 4;

    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${i * 0.5 + t}, 70%, 55%)`;
    ctx.fill();
  }

  requestAnimationFrame(() => draw(t + 1));
}
```

**The math:** The golden angle (137.5°) between each dot creates the same pattern as sunflower seeds, pinecones, and galaxies. Nature's favourite arrangement.

---

## RECIPE 6: Pendulum Wave (Physics Poetry)

```javascript
function draw(t) {
  ctx.fillStyle = "rgba(15, 23, 42, 0.3)";
  ctx.fillRect(0, 0, W, H);

  const N = 25;
  const baseFreq = 0.02;

  for (let i = 0; i < N; i++) {
    const freq = baseFreq * (10 + i); // each slightly faster
    const angle = Math.sin(t * freq) * Math.PI * 0.4;
    const length = 300;
    const x = 100 + i * (W - 200) / N;
    const bobX = x + Math.sin(angle) * length;
    const bobY = 100 + Math.cos(angle) * length;

    // String
    ctx.beginPath();
    ctx.moveTo(x, 100);
    ctx.lineTo(bobX, bobY);
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Bob
    ctx.beginPath();
    ctx.arc(bobX, bobY, 10, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${i * (360 / N)}, 80%, 60%)`;
    ctx.fill();
  }

  requestAnimationFrame(() => draw(t + 1));
}
```

**Why it's mesmerising:** Each pendulum has a slightly different frequency. They go in/out of sync creating waves, snakes, and patterns that seem alive. Based on real physics demos.

---

## RECIPE 7: Lorenz Attractor (Chaos Theory Butterfly)

```javascript
// The famous "butterfly" strange attractor
let x = 0.1, y = 0, z = 0;
const points = [];

function draw(t) {
  ctx.fillStyle = "rgba(0, 0, 0, 0.01)";
  ctx.fillRect(0, 0, W, H);

  // Lorenz equations (3 simple formulas → infinite complexity)
  const dt = 0.005;
  const sigma = 10, rho = 28, beta = 8 / 3;

  for (let i = 0; i < 20; i++) { // multiple steps per frame
    const dx = sigma * (y - x) * dt;
    const dy = (x * (rho - z) - y) * dt;
    const dz = (x * y - beta * z) * dt;
    x += dx; y += dy; z += dz;

    // Project 3D to 2D
    const px = W / 2 + x * 10;
    const py = H / 2 + z * 8 - 200;
    points.push({ x: px, y: py, age: 0 });
  }

  // Draw trail
  for (let i = 0; i < points.length; i++) {
    const p = points[i];
    p.age++;
    const alpha = Math.max(0, 1 - p.age / 500);
    ctx.beginPath();
    ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${200 + p.age * 0.3}, 80%, 60%, ${alpha})`;
    ctx.fill();
  }

  // Remove old points
  if (points.length > 5000) points.splice(0, 20);

  requestAnimationFrame(() => draw(t + 1));
}
```

**The math:** Three simple differential equations create a never-repeating pattern shaped like a butterfly. Chaos theory visualised — deterministic but unpredictable.

---

## RECIPE 8: Fourier Epicycles (Drawing with Circles)

```javascript
// Circles rotating on circles → draws any shape!
// (This is what 3Blue1Brown uses)

const epicycles = [
  { radius: 100, freq: 1, phase: 0 },
  { radius: 50, freq: 2, phase: Math.PI / 4 },
  { radius: 30, freq: 3, phase: Math.PI / 2 },
  { radius: 20, freq: 5, phase: 0 },
  { radius: 15, freq: -3, phase: Math.PI },
];

const trail = [];

function draw(t) {
  ctx.fillStyle = "rgba(15, 23, 42, 0.05)";
  ctx.fillRect(0, 0, W, H);

  let x = W / 2, y = H / 2;

  // Draw each epicycle (circle on circle on circle...)
  for (const epi of epicycles) {
    const prevX = x, prevY = y;
    const angle = epi.freq * t * 0.02 + epi.phase;
    x += Math.cos(angle) * epi.radius;
    y += Math.sin(angle) * epi.radius;

    // Draw the circle
    ctx.beginPath();
    ctx.arc(prevX, prevY, epi.radius, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(100, 120, 150, 0.3)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw radius line
    ctx.beginPath();
    ctx.moveTo(prevX, prevY);
    ctx.lineTo(x, y);
    ctx.strokeStyle = "rgba(150, 170, 200, 0.5)";
    ctx.stroke();
  }

  // Draw the point and trail
  trail.push({ x, y });
  if (trail.length > 2000) trail.shift();

  ctx.beginPath();
  for (let i = 0; i < trail.length; i++) {
    const p = trail[i];
    if (i === 0) ctx.moveTo(p.x, p.y);
    else ctx.lineTo(p.x, p.y);
  }
  ctx.strokeStyle = "#3b82f6";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Current point (bright dot)
  ctx.beginPath();
  ctx.arc(x, y, 5, 0, Math.PI * 2);
  ctx.fillStyle = "#f59e0b";
  ctx.fill();

  requestAnimationFrame(() => draw(t + 1));
}
```

**The math:** Fourier series — ANY shape can be decomposed into rotating circles. More circles = more accuracy. This is how JPEGs work (but in frequency domain).

---

## RECIPE 9: Matrix Rain (Simple but Iconic)

```javascript
const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZアカサタナハマヤラワ0123456789";
const fontSize = 16;
const cols = Math.floor(W / fontSize);
const drops = Array(cols).fill(0);

function draw() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
  ctx.fillRect(0, 0, W, H);

  ctx.fillStyle = "#0f0";
  ctx.font = `${fontSize}px monospace`;

  for (let i = 0; i < cols; i++) {
    const char = chars[Math.floor(Math.random() * chars.length)];
    const x = i * fontSize;
    const y = drops[i] * fontSize;

    // Head character (bright)
    ctx.fillStyle = "#fff";
    ctx.fillText(char, x, y);

    // Trailing characters (green)
    ctx.fillStyle = `rgba(0, 255, 0, ${0.5 + Math.random() * 0.5})`;
    ctx.fillText(chars[Math.floor(Math.random() * chars.length)], x, y - fontSize);

    // Reset drop randomly
    if (y > H && Math.random() > 0.98) drops[i] = 0;
    else drops[i]++;
  }

  requestAnimationFrame(draw);
}
```

---

## RECIPE 10: Breathing Circle (Meditation / Minimal)

```javascript
function draw(t) {
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, W, H);

  const breath = (Math.sin(t * 0.02) + 1) / 2; // 0 to 1, smooth
  const radius = 100 + breath * 100;
  const alpha = 0.3 + breath * 0.5;

  // Glow layers (outer to inner)
  for (let i = 5; i >= 0; i--) {
    const r = radius + i * 20;
    const a = alpha * (1 - i / 6);
    ctx.beginPath();
    ctx.arc(W / 2, H / 2, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(59, 130, 246, ${a * 0.3})`;
    ctx.fill();
  }

  // Core circle
  ctx.beginPath();
  ctx.arc(W / 2, H / 2, radius, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(59, 130, 246, ${alpha})`;
  ctx.fill();

  requestAnimationFrame(() => draw(t + 1));
}
```

**Why it works:** Slow `sin` oscillation mimics breathing. Layered glows create depth. Minimal = elegant.

---

## THE PATTERNS BEHIND ALL OF THESE

## 64.1 The 5 building blocks of beautiful math animations

```
1. CIRCULAR MOTION: x = cos(t), y = sin(t)
   → Orbits, spirals, pendulums, waves

2. PHASE OFFSET: each element has a slightly different starting point
   → Creates flowing, organic-looking group behaviour

3. FREQUENCY RATIO: combining waves at different speeds
   → Lissajous, interference, beats, moiré patterns

4. DECAY / GROWTH: values that fade (opacity) or grow (radius) over time
   → Trails, fireworks, breathing, explosions

5. HSL COLOUR CYCLING: hue shifts over time or by index
   → Rainbow effects with zero effort
   → hsl(time % 360, 80%, 60%) = endless smooth colour change
```

## 64.2 The colour trick (HSL > RGB)

```javascript
// RGB: hard to make smooth gradients
ctx.fillStyle = "rgb(255, 0, 0)"; // ← what's "the next colour"? Not obvious.

// HSL: rotate the hue for instant rainbow
ctx.fillStyle = `hsl(${t % 360}, 80%, 60%)`;
// t=0: red, t=60: yellow, t=120: green, t=180: cyan, t=240: blue, t=300: purple

// Per-particle colour (rainbow distribution):
ctx.fillStyle = `hsl(${(i / N) * 360}, 80%, 60%)`;

// Temperature colour (blue → red):
const temp = value / maxValue; // 0 to 1
ctx.fillStyle = `hsl(${240 - temp * 240}, 80%, 50%)`; // blue=240° to red=0°
```

## 64.3 The trail effect (one line of code → 10× more beautiful)

```javascript
// Instead of clearing fully:
ctx.clearRect(0, 0, W, H);  // ← clean but boring

// Semi-transparent overlay (trails/ghosting):
ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; // ← adjust 0.05 for trail length
ctx.fillRect(0, 0, W, H);

// 0.01 = very long trails (ghostly)
// 0.05 = medium trails (most animations)
// 0.2  = short trails (snappy)
// 1.0  = no trail (same as clearRect)
```

## 64.4 Quick reference: formulas → visuals

| Formula | Visual result |
|---------|--------------|
| `sin(t)` | Smooth oscillation (breathing, waves) |
| `cos(t), sin(t)` | Circular motion |
| `cos(a·t), sin(b·t)` | Lissajous curves (a≠b) |
| `sqrt(i) * angle` | Spiral (phyllotaxis) |
| `sin(distance - t)` | Expanding ripples |
| `noise(x, y, t)` | Organic flow fields |
| `x % n` | Repeating patterns (grids, tiles) |
| `1/distance` | Gravity-like attraction |
| `random() * 2 - 1` | Randomness (sparks, stars, noise) |
| `pow(x, 3)` | Acceleration curves (easing) |

---

## RECIPE 11 (Bonus): Flow Field (Organic Movement)

```javascript
// Particles following a noise-based vector field
const particles = Array.from({ length: 1000 }, () => ({
  x: Math.random() * W,
  y: Math.random() * H,
}));

function noise2D(x, y, t) {
  // Simple pseudo-noise (for real noise, use a library like simplex-noise)
  return Math.sin(x * 0.01 + t * 0.002) + Math.cos(y * 0.01 + t * 0.003);
}

function draw(t) {
  ctx.fillStyle = "rgba(15, 23, 42, 0.02)"; // very long trails
  ctx.fillRect(0, 0, W, H);

  for (const p of particles) {
    const angle = noise2D(p.x, p.y, t) * Math.PI * 2;
    p.x += Math.cos(angle) * 1.5;
    p.y += Math.sin(angle) * 1.5;

    // Wrap around edges
    if (p.x > W) p.x = 0; if (p.x < 0) p.x = W;
    if (p.y > H) p.y = 0; if (p.y < 0) p.y = H;

    ctx.beginPath();
    ctx.arc(p.x, p.y, 1, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${200 + noise2D(p.x, p.y, t) * 30}, 70%, 60%, 0.6)`;
    ctx.fill();
  }

  requestAnimationFrame(() => draw(t + 1));
}
```

---

## Summary

✅ 11 complete recipes: orbits, Lissajous, particles, waves, spirals, pendulums, Lorenz attractor, Fourier, Matrix rain, breathing circle, flow fields
✅ 5 building blocks: circular motion, phase offset, frequency ratio, decay/growth, HSL colour
✅ The trail trick: `rgba(0,0,0,0.05)` overlay instead of clearRect
✅ HSL for colour: rotate hue for instant rainbow, per-particle for distribution
✅ Formula → visual reference table (sin, cos, sqrt, distance, noise, modulo)
✅ All code is vanilla Canvas 2D — no libraries needed

## Key takeaways

**Simple math × many particles = beauty.** One `sin(t)` is boring. But 100 particles each with `sin(t + i*0.1)` creates a flowing, organic pattern. Repetition with slight variation is the secret.

**The trail effect is free beauty.** Change `ctx.clearRect()` to `ctx.fillStyle = "rgba(0,0,0,0.05)"` and suddenly everything looks 10× more polished. Ghost trails make movement visible and elegant.

**HSL is the colour hack.** `hsl(time % 360, 80%, 60%)` gives you smooth, endless colour cycling without thinking about RGB values. Use it for everything.

**Start with a recipe, then tweak ONE parameter.** Change the number of particles. Change the frequency ratio. Change the trail opacity. Each small tweak creates a completely different visual. Exploration IS the creative process.

---

→ [Back to Chapter 63: Revideo / Motion Canvas](./63-REVIDEO-MOTION-CANVAS.md)
