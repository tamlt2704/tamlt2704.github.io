# Chapter 5: Path Morphing — Shape-Shifting SVG

[← Ch 4: Stroke Animation](chapter-04-stroke-animation.md) | [Ch 6: Data Viz →](chapter-06-data-viz.md)

---

## Zara's Request

> "When the API call succeeds, the spinner should morph into a checkmark. Not disappear-and-replace — actually transform. The circle unwinds into the check stroke."

Paolo: "Our competitor does this. Users said it 'feels faster' even though load time is the same. Perceived performance matters."

---

## The Challenge

To morph between paths, both must have the **same number and type of commands**:

```svg
<!-- CAN morph (same structure) -->
<path d="M 50 10 C 70 10 90 30 90 50 C 90 70 70 90 50 90 C 30 90 10 70 10 50 C 10 30 30 10 50 10 Z"/>
<path d="M 50 10 C 55 10 60 30 60 50 C 60 70 55 90 50 90 C 45 90 40 70 40 50 C 40 30 45 10 50 10 Z"/>

<!-- CANNOT morph (different command counts/types) -->
<path d="M 50 10 C 70 10 90 50 50 90 Z"/>
<path d="M 20 50 L 40 70 L 80 30"/>
```

---

## Method 1: CSS `d` Transition

For paths with matching structures (Chrome/Edge support):

```css
.morph-shape {
  transition: d 0.6s ease-in-out;
}
.morph-shape.checked {
  d: path("M 25 52 C 28 55 36 65 42 72 C 45 74 52 65 58 56 C 64 47 78 28 80 26");
}
```

---

## Method 2: GSAP MorphSVG Plugin

Handles point matching automatically:

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle class="spinner-path" cx="50" cy="50" r="35" fill="none" stroke="#6366f1" stroke-width="4"/>
  <path class="checkmark-path" d="M 25 52 L 42 72 L 78 28"
        fill="none" stroke="#10b981" stroke-width="4" style="visibility: hidden"/>
</svg>
```

```javascript
const tl = gsap.timeline();
tl.to('.spinner-path', { rotation: 720, duration: 1.5, ease: 'power1.inOut', transformOrigin: 'center' })
  .to('.spinner-path', { morphSVG: '.checkmark-path', stroke: '#10b981', duration: 0.6, ease: 'power2.out' }, '-=0.3');
```

The circle spins, then deforms into a checkmark while changing color.

---

## Method 3: Flubber.js (Free Alternative)

```javascript
import { interpolate } from 'flubber';

const circle = "M 50 15 A 35 35 0 1 1 50 85 A 35 35 0 1 1 50 15";
const check = "M 25 52 L 42 72 L 78 28";
const interpolator = interpolate(circle, check, { maxSegmentLength: 5 });

let start = null;
function step(timestamp) {
  if (!start) start = timestamp;
  const progress = Math.min((timestamp - start) / 800, 1);
  document.querySelector('.morph-shape').setAttribute('d', interpolator(progress));
  if (progress < 1) requestAnimationFrame(step);
}
requestAnimationFrame(step);
```

---

## Orbitly's Loading → Success

```css
.status-icon.loading .status-path {
  stroke-dasharray: 80 140;
  animation: spin 1.2s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.status-icon.success .status-path {
  animation: none;
  transition: d 0.5s ease-out, stroke 0.3s ease;
  stroke: #10b981;
}
```

---

## Common Mistakes

**Mismatched point counts without a library** — CSS transition silently fails. No error, no animation, just a hard swap.

**Arc commands in morph targets** — arcs don't interpolate well. Convert to cubic Béziers before morphing.

**Performance on complex paths** — paths with hundreds of points morph slowly. Simplify first.

**Forgetting `fill="none"` during morph** — fill appears/disappears abruptly. Animate fill separately.

---

## Planning Morph-Friendly Paths

When designing icons that will morph between states, plan the path structure upfront:

```svg
<!-- Both states use the same structure: M, C, C, C, C, Z -->
<!-- State A: Circle -->
<path d="M 50 10 C 72 10, 90 28, 90 50 C 90 72, 72 90, 50 90 C 28 90, 10 72, 10 50 C 10 28, 28 10, 50 10 Z"/>

<!-- State B: Rounded square -->
<path d="M 50 15 C 65 15, 85 15, 85 30 C 85 50, 85 70, 85 85 C 70 85, 50 85, 35 85 C 15 85, 15 50, 15 30 Z"/>
```

Both have exactly 4 cubic Bézier segments. The browser can interpolate each control point smoothly between the two states.

---

## Exercise

Build a toggle for Orbitly's task completion:
1. Empty circle path (unchecked) and circle-with-checkmark (checked)
2. Both paths have the same number of commands
3. Morph on click using CSS transitions or flubber.js
4. Color transition: grey (#9ca3af) → green (#10b981)

Bonus: Add a "squish" — scaleX: 0.9 mid-morph, then bounce back.

---

## Quick Reference

| Method | Pros | Cons |
|--------|------|------|
| Manual point matching | No deps, CSS-only | Tedious, limited shapes |
| CSS `d` transition | Simple, declarative | Limited browser support |
| GSAP MorphSVG | Auto matching, smooth | Paid plugin |
| Flubber.js | Free, any shapes | Requires JS, larger bundle |

| Concept | Key Point |
|---------|-----------|
| Point matching | Both paths need same command structure |
| Interpolation | Each point moves linearly between positions |
| Easing | Applied to overall progress, not individual points |
| Color during morph | Animate stroke/fill separately |

---

[← Ch 4: Stroke Animation](chapter-04-stroke-animation.md) | [Ch 6: Data Viz →](chapter-06-data-viz.md)
