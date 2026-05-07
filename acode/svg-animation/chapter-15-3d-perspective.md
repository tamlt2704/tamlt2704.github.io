# Chapter 15: Pseudo-3D — Perspective and Depth

[← Ch 14: Scroll Animations](chapter-14-scroll-animations.md) | [Ch 16: Performance →](chapter-16-performance.md)

---

## Zara's Request

> "Pricing cards need to feel like physical objects. Hover → tilt toward the cursor. And a 3D flip for monthly/annual toggle."

Dani: "SVG is 2D. But CSS perspective transforms work on SVG elements. Layer elements at different Z-depths and they parallax naturally."

---

## CSS Perspective on SVG

```css
.perspective-scene { perspective: 800px; }
.card-3d {
  transform-style: preserve-3d;
  transform-origin: center;
  transition: transform 0.3s ease-out;
}
.card-3d:hover { transform: rotateY(5deg) rotateX(-3deg); }
```

On hover, the card tilts in 3D — left edge toward you, right recedes.

---

## Cursor-Tracking Tilt

```javascript
const card = document.querySelector('.card-3d');
const svg = document.querySelector('.perspective-scene');

svg.addEventListener('mousemove', (e) => {
  const rect = svg.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;
  const y = (e.clientY - rect.top) / rect.height;
  gsap.to(card, { rotateY: (x - 0.5) * 20, rotateX: (y - 0.5) * -15, duration: 0.3 });
});

svg.addEventListener('mouseleave', () => {
  gsap.to(card, { rotateY: 0, rotateX: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
});
```

Card follows cursor — springs back with elastic bounce on leave.

---

## Parallax Depth Layers

```svg
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" class="depth-scene">
  <g class="depth-layer" data-depth="0.2">
    <circle cx="320" cy="60" r="30" fill="#fef3c7"/>
  </g>
  <g class="depth-layer" data-depth="0.5">
    <rect x="100" y="80" width="200" height="140" rx="12" fill="white" stroke="#e5e7eb"/>
  </g>
  <g class="depth-layer" data-depth="1.0">
    <rect x="140" y="120" width="120" height="80" rx="8" fill="#6366f1"/>
  </g>
</svg>
```

```javascript
const scene = document.querySelector('.depth-scene');
const layers = document.querySelectorAll('.depth-layer');

scene.addEventListener('mousemove', (e) => {
  const rect = scene.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width - 0.5;
  const y = (e.clientY - rect.top) / rect.height - 0.5;

  layers.forEach(layer => {
    const depth = parseFloat(layer.dataset.depth);
    gsap.to(layer, { x: x * depth * 30, y: y * depth * 20, duration: 0.4 });
  });
});
```

Foreground moves most, background least — diorama effect.

---

## Card Flip Animation

```javascript
let flipped = false;
document.querySelector('.flip-card').addEventListener('click', () => {
  flipped = !flipped;
  gsap.to('.card-front', { rotateY: flipped ? 180 : 0, duration: 0.6, ease: 'power2.inOut' });
  gsap.to('.card-back', { rotateY: flipped ? 360 : 180, duration: 0.6, ease: 'power2.inOut' });
});
```

### Fallback (without backface-visibility support)

```javascript
gsap.to('.card-front', {
  rotateY: 90, duration: 0.3, ease: 'power2.in',
  onComplete: () => {
    gsap.set('.card-front', { visibility: 'hidden' });
    gsap.set('.card-back', { visibility: 'visible', rotateY: -90 });
    gsap.to('.card-back', { rotateY: 0, duration: 0.3, ease: 'power2.out' });
  }
});
```

---

## Isometric SVG

```svg
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <g class="iso-block">
    <polygon points="200,100 280,140 200,180 120,140" fill="#818cf8"/>
    <polygon points="120,140 200,180 200,240 120,200" fill="#6366f1"/>
    <polygon points="200,180 280,140 280,200 200,240" fill="#4f46e5"/>
  </g>
</svg>
```

```javascript
gsap.to('.iso-block', { y: -15, duration: 1, yoyo: true, repeat: -1, ease: 'power1.inOut' });
```

Three-face polygon with shading creates convincing 3D block.

---

## Common Mistakes

**`transform-style: preserve-3d` browser support** — Firefox/Safari handle 3D on SVG groups differently. Fallback: apply perspective to a wrapping `<div>`.

**Perspective too low** — `200px` = extreme distortion. Start at 800–1200px.

**backface-visibility on SVG groups** — not universally supported. Toggle visibility at 90° midpoint instead.

**Z-fighting** — overlapping layers can flip z-order during movement. Ensure clear visual separation.

---

## Exercise

Build Orbitly's 3D pricing section:
1. Three pricing cards that tilt toward cursor (max ±10°)
2. "Pro" card floats above others with subtle shadow
3. Flip animation for monthly/annual toggle
4. Background elements parallax at 0.2x depth

Bonus: Isometric dashboard illustration with slow rotation oscillation.

---

## Quick Reference

| CSS Property | Purpose | Value |
|-------------|---------|-------|
| `perspective` | Viewing distance | 800–1200px |
| `transform-style` | Enable 3D children | `preserve-3d` |
| `backface-visibility` | Hide flipped back | `hidden` |
| `rotateX/Y` | 3D tilt | ±10–15deg |

| Depth Effect | Technique |
|-------------|-----------|
| Cursor tilt | Map mouse to rotateX/Y |
| Parallax layers | `data-depth` multipliers |
| Card flip | rotateY(180) + backface |
| Isometric | Polygon faces with shading |

---

[← Ch 14: Scroll Animations](chapter-14-scroll-animations.md) | [Ch 16: Performance →](chapter-16-performance.md)
