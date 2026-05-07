# Chapter 17: Accessibility — Animation for Everyone

[← Ch 16: Performance](chapter-16-performance.md) | [Ch 18: Optimization →](chapter-18-optimization.md)

---

## Zara's Request

The accessibility auditor reports: "Animated SVGs have no text alternatives. Screen readers announce nothing. Users with vestibular disorders get motion sick from parallax."

> "I didn't realize animations could be harmful. We need motion for those who want it, calm for those who don't."

---

## ARIA Labels for SVG

```svg
<!-- Decorative: screen reader ignores -->
<svg viewBox="0 0 100 100" aria-hidden="true">
  <circle cx="50" cy="50" r="40" fill="#6366f1"/>
</svg>

<!-- Meaningful: screen reader announces -->
<svg viewBox="0 0 100 100" role="img" aria-label="Project completion: 73%">
  <circle cx="50" cy="50" r="40" fill="none" stroke="#6366f1" stroke-width="8"
          stroke-dasharray="251" stroke-dashoffset="68"/>
</svg>

<!-- Complex: detailed description -->
<svg viewBox="0 0 400 200" role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Weekly Revenue</title>
  <desc id="chart-desc">Revenue grew from $12k Monday to $28k Friday, dipping Wednesday.</desc>
</svg>
```

| SVG Type | Treatment |
|----------|-----------|
| Decorative | `aria-hidden="true"` |
| Informative | `role="img"` + `aria-label` |
| Interactive | `role="button"` + `aria-label` + `tabindex="0"` |
| Complex | `role="img"` + `<title>` + `<desc>` |

---

## prefers-reduced-motion

```css
.animated-element {
  animation: pulse 2s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animated-element { animation: none; }
  /* Better: replace, don't remove */
  .card-entrance { animation: simple-fade 0.3s ease forwards; }
  .spinner { animation: none; opacity: 0.7; }
}
@keyframes simple-fade { from { opacity: 0; } to { opacity: 1; } }
```

### JavaScript Detection

```javascript
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)');

if (prefersReduced.matches) {
  gsap.set('.animated', { opacity: 1 });
} else {
  gsap.from('.animated', { opacity: 0, y: 30, stagger: 0.1, ease: 'back.out(1.7)' });
}

// Listen for changes mid-session
prefersReduced.addEventListener('change', () => {
  prefersReduced.matches ? gsap.globalTimeline.pause() : gsap.globalTimeline.resume();
});
```

---

## Focus Indicators

```svg
<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <g class="svg-button" role="button" aria-label="Start project" tabindex="0">
    <rect x="10" y="10" width="180" height="40" rx="8" fill="#6366f1" class="btn-bg"/>
    <text x="100" y="35" text-anchor="middle" font-size="14" fill="white">Start Project</text>
  </g>
</svg>
```

```css
.svg-button:focus-visible .btn-bg { stroke: #1d4ed8; stroke-width: 3; }
```

```javascript
document.querySelector('.svg-button').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); }
});
```

---

## Pause Controls

WCAG 2.2.2 requires pause for animations > 5 seconds:

```javascript
const pauseBtn = document.querySelector('.pause-animations');
let isPaused = false;

pauseBtn.addEventListener('click', () => {
  isPaused = !isPaused;
  pauseBtn.setAttribute('aria-pressed', isPaused);
  pauseBtn.textContent = isPaused ? '▶ Resume motion' : '⏸ Pause motion';
  isPaused ? gsap.globalTimeline.pause() : gsap.globalTimeline.resume();
});
```

---

## Live Regions for State Changes

```html
<div aria-live="polite" class="sr-only" id="animation-status"></div>
```

```javascript
function onUploadComplete() {
  animateCheckmark();
  document.getElementById('animation-status').textContent = 'Upload complete.';
}
```

---

## Common Mistakes

**`aria-hidden` on meaningful content** — if SVG conveys info, don't hide it.

**Removing all motion** — reduced motion users still want feedback. Replace flashy with subtle fades.

**No pause mechanism** — required for auto-playing animations > 5s.

**No text alternative for animated charts** — self-drawing chart is meaningless to screen readers.

**Focus trap** — if animation moves an element, keyboard focus can get lost.

---

## Exercise

Make Orbitly's dashboard accessible:
1. `role="img"` + `aria-label` on informative SVGs
2. `aria-hidden="true"` on decorative backgrounds
3. `prefers-reduced-motion` — replace entrances with fades
4. Global "Pause animations" button
5. `aria-live` announcements for state changes
6. Keyboard-navigable interactive SVGs with focus indicators

---

## Quick Reference

| ARIA Pattern | When | Example |
|-------------|------|---------|
| `aria-hidden="true"` | Decorative | Background blobs |
| `role="img"` + `aria-label` | Informative | Status icons |
| `<title>` + `<desc>` | Complex | Charts |
| `tabindex="0"` + `role="button"` | Interactive | Clickable icons |
| `aria-live="polite"` | State changes | "Upload complete" |

| WCAG Criteria | Requirement |
|--------------|-------------|
| 1.1.1 | Text alternatives for SVGs |
| 2.2.2 | Pause/stop for auto-playing > 5s |
| 2.3.1 | No flashing > 3 times/second |
| 2.3.3 | Respect prefers-reduced-motion |

---

[← Ch 16: Performance](chapter-16-performance.md) | [Ch 18: Optimization →](chapter-18-optimization.md)
