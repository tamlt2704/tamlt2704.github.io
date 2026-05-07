# Chapter 4: Stroke Animation — The Self-Drawing Effect

[← Ch 3: CSS Animation](chapter-03-css-animation.md) | [Ch 5: Path Morphing →](chapter-05-path-morphing.md)

---

## Zara's Request

> "I want the logo to draw itself on page load. Like someone's sketching it in real-time. The orbit ring traces around, then the dot appears. This is the most requested animation in SaaS landing pages right now."

---

## The Trick: stroke-dasharray + stroke-dashoffset

Make one dash the exact length of the path, offset it by that length (invisible), then animate offset to zero (draws itself):

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="none" stroke="#6366f1" stroke-width="3" class="draw-circle"/>
</svg>
```

```css
.draw-circle {
  stroke-dasharray: 251;   /* 2πr = 2 × π × 40 ≈ 251 */
  stroke-dashoffset: 251;  /* fully hidden */
  animation: draw 2s ease-in-out forwards;
}
@keyframes draw { to { stroke-dashoffset: 0; } }
```

The circle traces itself clockwise over 2 seconds. `forwards` keeps it visible after completion.

---

## Calculating Path Length

Simple shapes: Circle = `2πr`, Rectangle = `2(w+h)`. Complex paths — use JavaScript:

```javascript
const path = document.querySelector('.logo-path');
const length = path.getTotalLength(); // e.g., 342.57
path.style.strokeDasharray = length;
path.style.strokeDashoffset = length;
```

---

## The Orbitly Logo — Self-Drawing

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" class="orbitly-logo">
  <path d="M 50 15 C 70 15, 85 30, 85 50 C 85 70, 70 85, 50 85 C 30 85, 15 70, 15 50 C 15 30, 30 15, 50 15"
        fill="none" stroke="#6366f1" stroke-width="3" stroke-linecap="round" class="orbit-ring"/>
  <circle cx="85" cy="50" r="5" fill="#6366f1" class="orbit-dot"/>
</svg>
```

```css
.orbit-ring {
  stroke-dasharray: 220;
  stroke-dashoffset: 220;
  animation: draw-ring 1.5s ease-in-out forwards;
}
.orbit-dot {
  opacity: 0; transform: scale(0); transform-origin: 85px 50px;
  animation: pop-dot 0.4s ease-out 1.4s forwards;
}
@keyframes draw-ring { to { stroke-dashoffset: 0; } }
@keyframes pop-dot { to { opacity: 1; transform: scale(1); } }
```

The ring traces over 1.5s, then the dot pops in just before completion — seamless handoff.

---

## JavaScript Approach for Dynamic Paths

```javascript
function animateDrawing(selector, duration = 2000) {
  const path = document.querySelector(selector);
  const length = path.getTotalLength();
  path.style.strokeDasharray = length;
  path.style.strokeDashoffset = length;
  path.style.transition = `stroke-dashoffset ${duration}ms ease-in-out`;
  requestAnimationFrame(() => { path.style.strokeDashoffset = '0'; });
}
```

---

## Multi-Path Sequencing

```css
.letter { stroke-dasharray: 200; stroke-dashoffset: 200; }
.letter-1 { animation: draw 0.8s ease-in-out 0s forwards; }
.letter-2 { animation: draw 0.5s ease-in-out 0.7s forwards; }
.letter-3 { animation: draw 1s ease-in-out 1.1s forwards; }
```

Each letter draws sequentially with slight overlap — feels like handwriting.

---

## Partial Drawing (Progress Indicator)

```javascript
function setProgress(path, percent) {
  const length = path.getTotalLength();
  path.style.strokeDasharray = length;
  path.style.strokeDashoffset = length * (1 - percent / 100);
}
```

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="6"/>
  <circle cx="50" cy="50" r="40" fill="none" stroke="#6366f1" stroke-width="6"
          stroke-linecap="round" class="progress-ring" transform="rotate(-90 50 50)"/>
</svg>
```

The `rotate(-90)` starts drawing from 12 o'clock instead of 3 o'clock.

---

## Common Mistakes

**Wrong dasharray value** — if shorter than the path, you get repeating dashes. Always measure with `getTotalLength()`.

**Forgetting `forwards`** — without it, the path disappears after animation ends.

**Unexpected start point** — drawing starts from the path's first `M` command. Use `transform="rotate(-90 cx cy)"` to change start position.

**Stroke-dashoffset direction** — positive hides from start, negative hides from end.

---

## Exercise

Build a self-drawing checkmark for Orbitly's success state:
1. Circle path (outer ring) + checkmark path (inner tick)
2. Use `getTotalLength()` for exact dash values
3. Circle draws first (0.6s), checkmark draws after (0.4s, delayed 0.5s)
4. Green color (`#10b981`)

Bonus: Add a scale bounce on the entire SVG when animation completes.

---

## Quick Reference

| Property | Purpose | Example |
|----------|---------|---------|
| `stroke-dasharray` | Dash pattern length | `251` (full path) |
| `stroke-dashoffset` | Offset into pattern | `251` (hidden) → `0` (visible) |
| `getTotalLength()` | JS path measurement | `path.getTotalLength()` |
| `stroke-linecap` | End cap style | `round` for smooth drawing |
| `animation-fill-mode` | Keep end state | `forwards` |
| `animation-delay` | Sequence paths | `0.5s`, `1s` |
| `transform: rotate()` | Change start point | `rotate(-90 50 50)` |

---

[← Ch 3: CSS Animation](chapter-03-css-animation.md) | [Ch 5: Path Morphing →](chapter-05-path-morphing.md)
