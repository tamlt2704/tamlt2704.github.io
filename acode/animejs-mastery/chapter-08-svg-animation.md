# Chapter 8: Progress Ring Fills to 87% — SVG Animation

[← Chapter 7: Value Animation](chapter-07-value-animation.md) | [Chapter 9: Motion Path →](chapter-09-motion-path.md)

---

## The Brief

Each spec card has a circular progress ring. When the numbers count up, the ring should fill proportionally:

- Water Resistance: 300/300m → 100% fill
- Power Reserve: 72/100h → 72% fill
- Case Diameter: 41/44mm → 93% fill
- Movement Frequency: 28800/36000vph → 80% fill

Mika's comp shows the ring drawing itself clockwise, starting from the top (12 o'clock position). The stroke has a rounded cap. The fill color is the brand gold.

---

## SVG Stroke Basics

An SVG circle has a stroke (outline). Two properties control how much of that stroke is visible:

```
stroke-dasharray:  Total length of the dash pattern
stroke-dashoffset: How far to offset the start of the dash
```

If `dasharray` equals the circle's circumference and `dashoffset` also equals the circumference, the stroke is invisible (offset by its full length). Animate `dashoffset` to 0 and the stroke "draws" itself.

```
dashoffset = circumference → invisible (fully offset)
dashoffset = 0             → fully visible (no offset)
dashoffset = circumference * 0.5 → 50% visible
```

---

## The Progress Ring SVG

```html
<svg class="progress-ring" width="120" height="120" viewBox="0 0 120 120">
  <!-- Background track -->
  <circle
    class="progress-ring-bg"
    cx="60" cy="60" r="45"
    fill="none"
    stroke="#2a2a2a"
    stroke-width="6"
  />
  <!-- Animated fill -->
  <circle
    class="progress-ring-fill"
    cx="60" cy="60" r="45"
    fill="none"
    stroke="#c8a864"
    stroke-width="6"
    stroke-linecap="round"
    transform="rotate(-90 60 60)"
  />
</svg>
```

Key details:
- `r="45"` → circumference = 2π × 45 ≈ 283
- `transform="rotate(-90 60 60)"` → starts from 12 o'clock (SVG circles start at 3 o'clock by default)
- `stroke-linecap="round"` → rounded ends (luxury feel)

---

## The stroke-dashoffset Technique

```css
.progress-ring-fill {
  stroke-dasharray: 283;    /* Full circumference */
  stroke-dashoffset: 283;   /* Fully hidden initially */
}
```

```javascript
// Fill to 87%
const circumference = 2 * Math.PI * 45;  // ≈ 283
const targetOffset = circumference * (1 - 0.87);  // 87% filled

anime({
  targets: '.progress-ring-fill',
  strokeDashoffset: [circumference, targetOffset],
  duration: 1500,
  easing: 'easeOutQuad',
});
```

The stroke starts fully hidden (`dashoffset = 283`) and animates to partially visible (`dashoffset = 283 * 0.13 ≈ 37`). The ring fills 87% of its circumference.

---

## anime.setDashoffset Helper

Anime.js provides a helper that automatically calculates the path length:

```javascript
anime({
  targets: '.progress-ring-fill',
  strokeDashoffset: [anime.setDashoffset, 0],  // From full offset → 0 (100% fill)
  duration: 2000,
  easing: 'easeInOutSine',
});
```

`anime.setDashoffset` reads the element's total path length and sets `stroke-dasharray` and `stroke-dashoffset` to that value. Then it animates to 0 (fully drawn).

For partial fills (not 100%), calculate manually:

```javascript
function fillRing(selector, percentage, duration = 1500) {
  const circle = document.querySelector(selector);
  const radius = circle.getAttribute('r');
  const circumference = 2 * Math.PI * radius;

  // Set the dasharray to full circumference
  circle.style.strokeDasharray = circumference;

  // Animate from fully hidden to target percentage
  const targetOffset = circumference * (1 - percentage / 100);

  anime({
    targets: circle,
    strokeDashoffset: [circumference, targetOffset],
    duration: duration,
    easing: 'easeOutQuad',
  });
}

// Usage
fillRing('.water-resistance-ring', 100);   // 300/300
fillRing('.power-reserve-ring', 72);       // 72/100
fillRing('.case-diameter-ring', 93);       // 41/44
fillRing('.frequency-ring', 80);           // 28800/36000
```

---

## SVG Path Drawing

The same technique works for any SVG path — not just circles:

```html
<svg viewBox="0 0 400 100">
  <path
    class="brand-logo"
    d="M10,50 C50,10 100,90 150,50 C200,10 250,90 300,50 L390,50"
    fill="none"
    stroke="#c8a864"
    stroke-width="2"
  />
</svg>
```

```javascript
// Draw the logo path
anime({
  targets: '.brand-logo',
  strokeDashoffset: [anime.setDashoffset, 0],
  duration: 2500,
  easing: 'easeInOutSine',
});
```

The logo draws itself stroke by stroke. `anime.setDashoffset` handles the math regardless of path complexity.

---

## Animating SVG Attributes

Beyond strokes, animate any SVG attribute:

```javascript
// Circle radius
anime({
  targets: 'circle.pulse',
  r: [20, 40],           // Radius grows
  opacity: [1, 0],       // Fades out
  duration: 1000,
  loop: true,
  easing: 'easeOutQuad',
});

// Rectangle dimensions
anime({
  targets: 'rect.bar',
  height: [0, 200],
  y: [200, 0],           // Grow upward (SVG y is top-down)
  duration: 800,
  easing: 'easeOutCubic',
});

// Line position
anime({
  targets: 'line.indicator',
  x2: 300,
  y2: 50,
  duration: 600,
});

// Polygon points
anime({
  targets: 'polygon.shape',
  points: '64 128 8.574 96 8.574 32 64 0 119.426 32 119.426 96',
  duration: 1000,
  easing: 'easeOutQuad',
});
```

---

## SVG Transforms

SVG elements use the same transform properties as HTML:

```javascript
anime({
  targets: '.watch-gear',
  rotate: 360,
  duration: 4000,
  loop: true,
  easing: 'linear',  // Constant rotation for gears
});

anime({
  targets: '.watch-crown',
  translateX: [-5, 0],  // Crown pulls out then pushes back
  duration: 300,
  direction: 'alternate',
  loop: 2,
  easing: 'easeInOutQuad',
});
```

For SVG, `transform-origin` defaults to the SVG viewport origin (0,0), not the element's center. Set it explicitly:

```css
.watch-gear {
  transform-origin: center center;
  transform-box: fill-box;  /* Origin relative to element, not viewport */
}
```

---

## The Complete Spec Section

Combining value animation (Chapter 7) with SVG ring animation:

```javascript
function animateSpecCard(card, delay = 0) {
  const target = parseInt(card.dataset.target);
  const max = parseInt(card.dataset.max);
  const percentage = (target / max) * 100;

  const valueEl = card.querySelector('.spec-value');
  const ring = card.querySelector('.progress-ring-fill');
  const radius = parseFloat(ring.getAttribute('r'));
  const circumference = 2 * Math.PI * radius;

  // Set initial state
  ring.style.strokeDasharray = circumference;
  ring.style.strokeDashoffset = circumference;

  const counter = { value: 0 };

  // Count the number
  anime({
    targets: counter,
    value: target,
    duration: 2000,
    delay: delay,
    easing: 'easeOutExpo',
    round: 1,
    update: () => {
      valueEl.textContent = counter.value.toLocaleString();
    },
  });

  // Fill the ring (synchronized)
  anime({
    targets: ring,
    strokeDashoffset: [circumference, circumference * (1 - percentage / 100)],
    duration: 2000,
    delay: delay,
    easing: 'easeOutExpo',
  });
}

// Animate all spec cards with stagger
document.querySelectorAll('.spec-card').forEach((card, i) => {
  animateSpecCard(card, i * 200);
});
```

The number counts up and the ring fills simultaneously, with the same easing and duration. They feel connected — one visualization, two representations.

---

## SVG Line Drawing: The Watch Logo

The watchmaker's logo is an SVG with multiple paths. Draw them sequentially:

```javascript
const logoPaths = document.querySelectorAll('.logo-path');

const logoTimeline = anime.timeline({
  easing: 'easeInOutSine',
  autoplay: false,
});

logoPaths.forEach((path, i) => {
  logoTimeline.add({
    targets: path,
    strokeDashoffset: [anime.setDashoffset, 0],
    duration: 800,
    delay: i * 100,
  }, i * 200);  // Slight overlap between paths
});

// After all paths are drawn, fill them
logoTimeline.add({
  targets: '.logo-path',
  fill: ['rgba(200, 168, 100, 0)', 'rgba(200, 168, 100, 1)'],
  duration: 600,
  delay: anime.stagger(50),
}, '-=400');
```

The logo draws itself path by path, then fills with gold. A signature animation for the brand.

---

## SVG Morphing (Preview)

Anime.js can animate between SVG path data if the paths have the same number of points:

```javascript
anime({
  targets: '.morphing-shape',
  d: [
    { value: 'M10,10 L90,10 L90,90 L10,90 Z' },   // Square
    { value: 'M50,10 L90,90 L10,90 Z' },            // Won't work — different point count!
  ],
});
```

For morphing to work, both paths need the same number of commands and points. We'll cover this properly in Chapter 13 (SVG Morphing).

---

## Common SVG Animation Pitfalls

### 1. Forgetting stroke-dasharray

```javascript
// ❌ Won't work — no dasharray set
anime({
  targets: 'path',
  strokeDashoffset: 0,
});

// ✅ Set dasharray first (or use anime.setDashoffset)
const path = document.querySelector('path');
const length = path.getTotalLength();
path.style.strokeDasharray = length;
path.style.strokeDashoffset = length;

anime({
  targets: path,
  strokeDashoffset: 0,
  duration: 2000,
});
```

### 2. SVG transform-origin

```css
/* ❌ Rotates around viewport origin */
.gear { transform-origin: 50% 50%; }

/* ✅ Rotates around element center */
.gear {
  transform-origin: center center;
  transform-box: fill-box;
}
```

### 3. Animating fill with opacity

```javascript
// ❌ fill doesn't interpolate well from 'none'
anime({ targets: 'path', fill: ['none', '#c8a864'] });

// ✅ Use rgba with alpha
anime({ targets: 'path', fill: ['rgba(200,168,100,0)', 'rgba(200,168,100,1)'] });
```

---

## What You Learned

- **stroke-dashoffset** — the core technique for SVG drawing animations
- **anime.setDashoffset** — auto-calculates path length
- **Partial fills** — calculate offset from circumference and percentage
- **SVG attributes** — r, cx, cy, points, height, width all animatable
- **SVG transforms** — same as HTML but watch transform-origin
- **transform-box: fill-box** — fix SVG transform-origin issues
- **Path drawing** — works on any SVG path, not just circles
- **Synchronized animation** — ring fill + number count with same timing
- **Logo reveal** — sequential path drawing + fill

The progress rings fill. The numbers count. The logo draws itself. SVG animation adds a visual richness that CSS alone can't achieve.

But Mika's comp has one more SVG trick: the watch hands don't just rotate — they follow the curved path of the dial. That's motion path animation.

---

[← Chapter 7: Value Animation](chapter-07-value-animation.md) | [Chapter 9: Motion Path →](chapter-09-motion-path.md)
