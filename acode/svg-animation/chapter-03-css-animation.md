# Chapter 3: CSS Animations on SVG

[← Ch 2: Paths](chapter-02-paths.md) | [Ch 4: Stroke Animation →](chapter-04-stroke-animation.md)

---

## Zara's Request

> "The notification bell icon — I need it to pulse when there's an unread notification. Subtle scale up and down, maybe a slight opacity shift. Nothing crazy. Just... alive."

---

## CSS Transforms on SVG

SVG elements respond to CSS transforms — but with one critical difference: **transform-origin defaults to (0, 0)** of the SVG canvas, not the element's center.

```css
.bell-icon {
  transform-origin: center; /* Fix: rotate/scale from element center */
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}
```

### What This Looks Like

The bell gently grows to 110% and fades slightly, then returns. A breathing effect that signals "something's here."

---

## Transition on Hover

```svg
<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg" class="nav-icons">
  <rect class="icon-square" x="10" y="10" width="50" height="60" rx="8" fill="#6366f1"/>
  <rect class="icon-square" x="70" y="10" width="50" height="60" rx="8" fill="#6366f1"/>
</svg>
```

```css
.icon-square {
  transition: transform 0.3s ease, fill 0.2s ease;
  transform-origin: center;
}
.nav-icons:hover .icon-square {
  fill: #818cf8;
  transform: scale(0.85) rotate(5deg);
}
```

---

## Combining Transforms — Loading Spinner

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g class="spinner-group">
    <circle cx="50" cy="20" r="6" fill="#6366f1" class="dot dot-1"/>
    <circle cx="80" cy="50" r="6" fill="#818cf8" class="dot dot-2"/>
    <circle cx="50" cy="80" r="6" fill="#a5b4fc" class="dot dot-3"/>
    <circle cx="20" cy="50" r="6" fill="#c7d2fe" class="dot dot-4"/>
  </g>
</svg>
```

```css
.spinner-group {
  transform-origin: 50px 50px;
  animation: orbit 3s linear infinite;
}
@keyframes orbit { to { transform: rotate(360deg); } }

@keyframes fade-pulse { 0%, 100% { opacity: 0.3; } 25% { opacity: 1; } }
.dot-1 { animation: fade-pulse 1.2s ease-in-out infinite; }
.dot-2 { animation: fade-pulse 1.2s ease-in-out 0.3s infinite; }
.dot-3 { animation: fade-pulse 1.2s ease-in-out 0.6s infinite; }
.dot-4 { animation: fade-pulse 1.2s ease-in-out 0.9s infinite; }
```

Four dots orbit while individually pulsing with staggered timing — organic, not mechanical.

---

## Dev Dani's Performance Note

> "Only animate `transform` and `opacity`. Those don't trigger layout or paint. Animating `fill` or `stroke-width` causes repaints every frame. Fine for hover transitions, bad for infinite loops."

```css
/* GOOD: GPU-composited */
@keyframes good { 50% { transform: scale(1.05); opacity: 0.9; } }
/* AVOID in loops: triggers repaint */
@keyframes bad { 50% { fill: #818cf8; stroke-width: 4; } }
```

---

## Staggering Without JavaScript

```svg
<svg viewBox="0 0 100 20" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="10" height="10" rx="2" class="bar bar-1"/>
  <rect x="20" y="5" width="10" height="10" rx="2" class="bar bar-2"/>
  <rect x="35" y="5" width="10" height="10" rx="2" class="bar bar-3"/>
  <rect x="50" y="5" width="10" height="10" rx="2" class="bar bar-4"/>
  <rect x="65" y="5" width="10" height="10" rx="2" class="bar bar-5"/>
</svg>
```

```css
@keyframes bounce {
  0%, 80%, 100% { transform: scaleY(1); }
  40% { transform: scaleY(1.8); }
}
.bar { fill: #6366f1; transform-origin: center bottom; animation: bounce 1.4s ease-in-out infinite; }
.bar-1 { animation-delay: 0s; }
.bar-2 { animation-delay: 0.1s; }
.bar-3 { animation-delay: 0.2s; }
.bar-4 { animation-delay: 0.3s; }
.bar-5 { animation-delay: 0.4s; }
```

An audio equalizer wave — bars stretch in sequence.

---

## Common Mistakes

**transform-origin on SVG** — defaults to canvas (0,0), not element center. Always set explicitly.

**Forgetting `infinite`** — `animation: pulse 2s ease` plays once and stops.

**Inline SVG class conflicts** — inline SVGs share the document's CSS scope. Use specific class names.

---

## Exercise

Create a loading indicator for Orbitly:
1. Three circles (cx: 25, 50, 75 — cy: 50 — r: 8)
2. Bounce keyframe: translateY from 0 to -15px and back
3. Stagger each by 0.15s, `ease-in-out`, loop infinitely

Bonus: Add opacity fade so dots dim at the bottom of the bounce.

---

## Quick Reference

| CSS Property | SVG Behavior | Notes |
|-------------|-------------|-------|
| `transform` | Works on SVG elements | Set `transform-origin: center` |
| `opacity` | Works normally | GPU-composited |
| `animation` | Full @keyframes support | Same syntax as HTML |
| `transition` | Works on hover/state | Good for interactions |
| `transform-origin` | Defaults to SVG (0,0) | Must set explicitly |
| `fill` | Animatable | Triggers repaint |
| `animation-delay` | Stagger effect | Negative = start mid-anim |

---

[← Ch 2: Paths](chapter-02-paths.md) | [Ch 4: Stroke Animation →](chapter-04-stroke-animation.md)
