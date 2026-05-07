# Chapter 9: Interactive SVG — Responding to Users

[← Ch 8: Text Animation](chapter-08-text-animation.md) | [Ch 10: Page Transitions →](chapter-10-transitions.md)

---

## Zara's Request

> "The pricing cards are dead. When you hover a plan, nothing happens. I want the SVG icons to react — rocket tilts and fires up, shield pulses, chart bars animate. Micro-interactions add up."

---

## Pointer Events on SVG

SVG elements receive mouse/touch events like HTML:

```javascript
const circle = document.querySelector('.interactive-circle');
circle.addEventListener('mouseenter', () => {
  gsap.to(circle, { scale: 1.1, fill: '#818cf8', duration: 0.3 });
});
circle.addEventListener('mouseleave', () => {
  gsap.to(circle, { scale: 1, fill: '#6366f1', duration: 0.3 });
});
```

The `pointer-events` CSS property controls clickable areas:

```css
.shape { pointer-events: fill; }    /* only filled area */
.shape { pointer-events: all; }     /* fill + stroke + bounding area */
.shape { pointer-events: none; }    /* not clickable */
```

---

## Hover States with CSS

```css
.nav-item { cursor: pointer; }
.nav-item .icon-bg { transition: fill 0.2s ease; }
.nav-item:hover .icon-bg { fill: #eef2ff; }
.nav-item .icon-arrow {
  transition: transform 0.3s ease; transform-origin: center;
}
.nav-item:hover .icon-arrow { transform: translateY(-3px); }
```

---

## Cursor-Following Animation

```javascript
const svg = document.querySelector('.cursor-scene');
const pupils = document.querySelectorAll('.pupil');

svg.addEventListener('mousemove', (e) => {
  const rect = svg.getBoundingClientRect();
  const svgX = (e.clientX - rect.left) / rect.width * 400;
  const svgY = (e.clientY - rect.top) / rect.height * 300;

  pupils.forEach(pupil => {
    const parent = pupil.parentElement;
    const match = parent.getAttribute('transform').match(/translate\((\d+),\s*(\d+)\)/);
    const eyeX = parseInt(match[1]), eyeY = parseInt(match[2]);
    const angle = Math.atan2(svgY - eyeY, svgX - eyeX);
    const dist = Math.min(Math.sqrt((svgX-eyeX)**2 + (svgY-eyeY)**2) * 0.1, 12);
    gsap.to(pupil, { x: Math.cos(angle)*dist, y: Math.sin(angle)*dist, duration: 0.2 });
  });
});
```

Two cartoon eyes follow the cursor — playful for 404 pages or empty states.

---

## Click Animations

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g class="like-button" style="cursor: pointer">
    <circle cx="50" cy="50" r="35" fill="#fef2f2" class="btn-bg"/>
    <path class="heart" d="M 50 70 C 35 55, 25 45, 25 38 C 25 30, 32 25, 38 25
          C 44 25, 48 28, 50 32 C 52 28, 56 25, 62 25 C 68 25, 75 30, 75 38
          C 75 45, 65 55, 50 70 Z" fill="#ef4444" transform-origin="50px 50px"/>
  </g>
</svg>
```

```javascript
likeBtn.addEventListener('click', () => {
  gsap.timeline()
    .to(heart, { scale: 0.7, duration: 0.1 })
    .to(heart, { scale: 1.2, duration: 0.2, ease: 'back.out(3)' })
    .to(heart, { scale: 1, duration: 0.3, ease: 'elastic.out(1, 0.4)' });
});
```

Heart squishes, bounces up larger, then settles with elastic spring.

---

## Drag Interaction

```javascript
const draggable = document.querySelector('.draggable-element');
let isDragging = false;

draggable.addEventListener('mousedown', () => {
  isDragging = true;
  gsap.to(draggable, { scale: 1.05, duration: 0.1 });
});
document.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  const rect = draggable.ownerSVGElement.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 400;
  const y = ((e.clientY - rect.top) / rect.height) * 300;
  gsap.to(draggable, { attr: { cx: x, cy: y }, duration: 0.1 });
});
document.addEventListener('mouseup', () => {
  isDragging = false;
  gsap.to(draggable, { scale: 1, duration: 0.2, ease: 'back.out(2)' });
});
```

---

## Common Mistakes

**Screen coords vs SVG coords** — always convert: `svgX = (clientX - rect.left) / rect.width * viewBoxWidth`.

**Events on `fill="none"`** — invisible elements don't receive events. Use `pointer-events: all` or `fill="transparent"`.

**Hover flicker** — if animation moves element away from cursor, it triggers mouseleave. Attach listener to a parent `<g>`.

**Touch events** — use `pointerenter`/`pointerleave` for cross-device support.

---

## Exercise

Build interactive pricing card icons:
1. Three SVG icons: rocket (Starter), shield (Pro), chart (Enterprise)
2. Hover: rocket tilts 15° + flame scales; shield pulses; chart bars grow
3. Click: "selected" animation (scale bounce + color change)
4. Cursor-following highlight on card backgrounds
5. Keyboard focus support (`:focus-visible`)

---

## Quick Reference

| Event | Use Case | Notes |
|-------|----------|-------|
| `pointerenter`/`pointerleave` | Hover | Cross-device |
| `click` | Tap/click | Works on touch |
| `mousemove` | Cursor tracking | Convert coords |
| `mousedown`/`mouseup` | Drag | Track state |

| SVG Method | Returns |
|-----------|---------|
| `getBBox()` | `{x, y, width, height}` |
| `getScreenCTM()` | Screen transform matrix |
| `ownerSVGElement` | Parent SVG reference |

---

[← Ch 8: Text Animation](chapter-08-text-animation.md) | [Ch 10: Page Transitions →](chapter-10-transitions.md)
